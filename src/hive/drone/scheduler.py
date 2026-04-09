"""DroneScheduler: event-driven task dispatcher."""

from __future__ import annotations

import asyncio
from pathlib import Path

from rich.console import Console

from hive.drone.ai_advisor import AIAdvisor, AdvisorAction
from hive.drone.state_machine import TaskStateMachine
from hive.hive_dir import HiveDir
from hive.memory.l2_writer import L2Writer
from hive.memory.l3_writer import L3Writer
from hive.models.context import DroneContext
from hive.models.task import Task, TaskStatus
from hive.worker.runner import WorkerResult, WorkerRunner

console = Console()


class DroneScheduler:
    def __init__(
        self,
        hive_dir: HiveDir,
        project_root: Path,
        max_parallel_workers: int = 3,
        budget_per_task: float = 5.0,
    ):
        self.hd = hive_dir
        self.project_root = project_root
        self.max_parallel = max_parallel_workers
        self.sm = TaskStateMachine()
        self.runner = WorkerRunner(hive_dir, project_root, self.sm, budget_per_task)
        self.advisor = AIAdvisor(project_root)
        self.l2 = L2Writer(hive_dir)
        self.l3 = L3Writer(hive_dir, project_root)
        self.active_workers: dict[str, asyncio.Task] = {}
        self.total_cost_usd: float = 0.0

    async def run(self) -> None:
        console.print("[bold cyan]Drone starting...[/]")

        while True:
            tasks = self.hd.load_all_tasks()

            if not tasks:
                console.print("[yellow]No tasks found. Exiting.[/]")
                return

            if self._is_complete(tasks):
                self._print_summary(tasks)
                return

            if self._is_deadlocked(tasks):
                await self._handle_deadlock(tasks)
                return

            ready = self._get_ready_tasks(tasks)
            slots = self.max_parallel - len(self.active_workers)

            for task in ready[:slots]:
                if task.id not in self.active_workers:
                    console.print(f"[green]→ Dispatching[/] {task.id}: {task.title}")
                    worker_coro = self._run_worker_and_handle(task, tasks)
                    self.active_workers[task.id] = asyncio.create_task(worker_coro)

            if self.active_workers:
                done, _ = await asyncio.wait(
                    list(self.active_workers.values()),
                    return_when=asyncio.FIRST_COMPLETED,
                )
                for completed_task in done:
                    completed_ids = [
                        tid for tid, t in self.active_workers.items()
                        if t is completed_task
                    ]
                    for tid in completed_ids:
                        del self.active_workers[tid]
            else:
                # No workers running, nothing ready, not complete/deadlocked
                # Shouldn't happen often but protect against infinite loop
                await asyncio.sleep(2)

    async def _run_worker_and_handle(
        self, task: Task, all_tasks: dict[str, Task]
    ) -> None:
        result: WorkerResult = await self.runner.run_task(task, all_tasks)
        self.total_cost_usd += result.cost_usd

        if result.success and result.memo:
            # Update L2 and L3 memory
            updated_tasks = self.hd.load_all_tasks()
            self.l2.write(result.task, result.memo)
            self.l3.update(result.task, result.memo, updated_tasks)
            console.print(
                f"[green]✓ Done[/] {result.task.id} "
                f"(${result.cost_usd:.3f}, {result.duration_seconds:.0f}s)"
            )
        elif not result.success:
            if result.task.status == TaskStatus.BLOCKED:
                console.print(
                    f"[red]✗ Blocked[/] {result.task.id}: {result.error}"
                )
                await self._handle_blocked_task(result.task)
            else:
                console.print(
                    f"[yellow]↻ Retry queued[/] {result.task.id}: {result.error}"
                )

    async def _handle_blocked_task(self, task: Task) -> None:
        ctx = self._build_drone_context()
        decision = await self.advisor.decide_on_blocked_task(ctx, task)
        console.print(
            f"[dim]AI advisor decision for {task.id}: "
            f"{decision.action.value} — {decision.reasoning}[/]"
        )

        if decision.action == AdvisorAction.RETRY:
            if decision.modified_description:
                task.description = decision.modified_description
            task.retry_count = 0
            task.blocked_reason = None
            self.sm.transition(self.hd, task, TaskStatus.QUEUE)
            self.hd.save_task(task)

        elif decision.action == AdvisorAction.SKIP:
            # Mark as done with a synthetic handover
            from hive.models.handover import HandoverMemo
            memo = HandoverMemo.synthesize(
                task_id=task.id,
                duration_seconds=0,
                cost_usd=0,
                notes=f"Skipped by AI advisor: {decision.reasoning}",
            )
            self.hd.save_handover(memo)
            self.sm.transition(self.hd, task, TaskStatus.QUEUE)
            task.status = TaskStatus.QUEUE
            self.sm.transition(self.hd, task, TaskStatus.ACTIVE)
            task.status = TaskStatus.ACTIVE
            self.sm.transition(self.hd, task, TaskStatus.DONE)

        elif decision.action == AdvisorAction.SPLIT and decision.new_tasks:
            for i, td in enumerate(decision.new_tasks):
                from hive.utils.ids import make_task_id
                from hive.models.task import Task as T, TaskPriority
                new_id = make_task_id(1000 + i, td.get("title", "subtask"))
                new_task = T(
                    id=new_id,
                    title=td.get("title", "Subtask"),
                    description=td.get("description", ""),
                    plan_chapters=td.get("plan_chapters", task.plan_chapters),
                    exit_criteria=td.get("exit_criteria", task.exit_criteria),
                    depends_on=td.get("depends_on", []),
                )
                self.hd.save_task(new_task)
            # Mark original as done (superseded)
            self.hd.write_pending(
                task.id,
                f"Superseded by split tasks from advisor: {decision.reasoning}",
            )

        else:  # ESCALATE
            console.print(
                f"[bold red]ESCALATION NEEDED[/]: Task {task.id} requires human input.\n"
                f"Reason: {decision.reasoning}\n"
                f"See: .hive/pending/{task.id}.md"
            )

    async def _handle_deadlock(self, tasks: dict[str, Task]) -> None:
        blocked = [t for t in tasks.values() if t.status == TaskStatus.BLOCKED]
        console.print(
            f"[bold red]Deadlock detected[/]: {len(blocked)} tasks blocked, "
            f"no progress possible."
        )
        for task in blocked:
            console.print(f"  - {task.id}: {task.blocked_reason}")
        console.print("Run [cyan]hive status[/] to review blocked tasks.")

    def _get_ready_tasks(self, tasks: dict[str, Task]) -> list[Task]:
        done_ids = {tid for tid, t in tasks.items() if t.status == TaskStatus.DONE}
        ready = [
            t for t in tasks.values()
            if t.status == TaskStatus.QUEUE
            and set(t.depends_on).issubset(done_ids)
            and t.id not in self.active_workers
        ]
        return sorted(ready, key=lambda t: (t.priority.value, t.created_at))

    def _is_complete(self, tasks: dict[str, Task]) -> bool:
        return bool(tasks) and all(t.status == TaskStatus.DONE for t in tasks.values())

    def _is_deadlocked(self, tasks: dict[str, Task]) -> bool:
        non_done = [t for t in tasks.values() if t.status != TaskStatus.DONE]
        return (
            not self.active_workers
            and bool(non_done)
            and all(t.status == TaskStatus.BLOCKED for t in non_done)
        )

    def _build_drone_context(self) -> DroneContext:
        return DroneContext(
            plan_index=self.hd.read_plan_index(),
            global_state=self.hd.read_l3_state(),
            recent_handovers=self.hd.load_last_n_handovers(10),
            all_tasks=self.hd.load_all_tasks(),
        )

    def _print_summary(self, tasks: dict[str, Task]) -> None:
        done = sum(1 for t in tasks.values() if t.status == TaskStatus.DONE)
        console.print(
            f"\n[bold green]All {done} tasks complete![/] "
            f"Total cost: [cyan]${self.total_cost_usd:.3f}[/]"
        )
