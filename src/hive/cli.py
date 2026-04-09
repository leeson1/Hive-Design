"""Hive CLI entry point."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

console = Console()


def get_hive_dir(project_root: Path):
    from hive.hive_dir import HiveDir
    return HiveDir(project_root)


@click.group()
@click.option(
    "--project-dir", "-d",
    type=click.Path(exists=False),
    default=".",
    help="Project root directory (default: current directory)",
)
@click.pass_context
def cli(ctx: click.Context, project_dir: str):
    """Hive — AI Agent Orchestration System.

    Two-phase workflow:

    \b
    1. hive init "requirement"   — generate plan and task queue
    2. hive run                  — dispatch tasks to Worker Bees
    """
    ctx.ensure_object(dict)
    ctx.obj["project_root"] = Path(project_dir).resolve()


@cli.command()
@click.argument("requirement")
@click.option("--force", "-f", is_flag=True, help="Reinitialize even if .hive/ exists")
@click.pass_context
def init(ctx: click.Context, requirement: str, force: bool):
    """Phase 1: Expand REQUIREMENT into a full plan and task queue.

    Example:

    \b
    hive init "build a REST API for a todo app with user auth"
    """
    project_root: Path = ctx.obj["project_root"]
    hd = get_hive_dir(project_root)

    if hd.root.exists() and not force:
        if not click.confirm(".hive/ already exists. Reinitialize? (use --force to skip this prompt)"):
            console.print("[yellow]Aborted.[/]")
            return
        # Clean up existing tasks
        import shutil
        shutil.rmtree(hd.root)

    hd.initialize()
    console.print(f"[bold green]Hive initialized[/] in {project_root}")
    console.print(f"Requirement: [italic]{requirement}[/]\n")

    from hive.planner import Planner, PlannerError
    planner = Planner(hd, project_root)

    with console.status("[bold]Generating plan (this may take a minute)...[/]"):
        try:
            plan, tasks = asyncio.run(planner.run(requirement))
        except PlannerError as e:
            console.print(f"[red]Planning failed:[/] {e}")
            sys.exit(1)

    # Display plan
    table = Table(title=f"Plan: {plan.title}", show_lines=True)
    table.add_column("#", style="dim", width=3)
    table.add_column("Chapter")
    table.add_column("Summary")
    for i, ch in enumerate(plan.chapters, 1):
        table.add_row(str(i), ch.title, ch.summary)
    console.print(table)

    # Display tasks
    task_table = Table(title="Task Queue", show_lines=True)
    task_table.add_column("ID", style="dim")
    task_table.add_column("Title")
    task_table.add_column("Depends On")
    task_table.add_column("Priority")
    for task in tasks:
        task_table.add_row(
            task.id,
            task.title,
            ", ".join(task.depends_on) or "—",
            str(task.priority.name),
        )
    console.print(task_table)

    console.print(
        f"\n[bold]{len(tasks)} tasks queued.[/] "
        f"Review plan in [cyan].hive/plan/[/]\n"
        f"When ready: [bold cyan]hive run[/]"
    )


@cli.command()
@click.option("--workers", "-w", default=3, show_default=True, help="Max parallel workers")
@click.option("--budget", "-b", default=5.0, show_default=True, help="Max USD per task")
@click.option("--dry-run", is_flag=True, help="Show what would run, don't execute")
@click.pass_context
def run(ctx: click.Context, workers: int, budget: float, dry_run: bool):
    """Phase 2: Run the Drone to dispatch tasks to Worker Bees.

    Runs until all tasks complete, deadlock, or are escalated.
    """
    project_root: Path = ctx.obj["project_root"]
    hd = get_hive_dir(project_root)

    if not hd.root.exists():
        console.print("[red]No .hive/ found. Run 'hive init \"requirement\"' first.[/]")
        sys.exit(1)

    tasks = hd.load_all_tasks()
    if not tasks:
        console.print("[yellow]No tasks found in .hive/tasks/.[/]")
        sys.exit(1)

    if dry_run:
        _show_dispatch_plan(tasks)
        return

    from hive.drone.scheduler import DroneScheduler
    scheduler = DroneScheduler(
        hive_dir=hd,
        project_root=project_root,
        max_parallel_workers=workers,
        budget_per_task=budget,
    )

    try:
        asyncio.run(scheduler.run())
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted. Active workers may still be running.[/]")


@cli.command()
@click.pass_context
def status(ctx: click.Context):
    """Show current task queue status."""
    project_root: Path = ctx.obj["project_root"]
    hd = get_hive_dir(project_root)

    if not hd.root.exists():
        console.print("[red]No .hive/ found. Run 'hive init' first.[/]")
        sys.exit(1)

    tasks = hd.load_all_tasks()
    if not tasks:
        console.print("[yellow]No tasks.[/]")
        return

    from hive.models.task import TaskStatus

    STATUS_STYLE = {
        TaskStatus.QUEUE: "yellow",
        TaskStatus.ACTIVE: "cyan",
        TaskStatus.DONE: "green",
        TaskStatus.BLOCKED: "red",
    }

    table = Table(title="Hive Status", show_lines=True)
    table.add_column("ID", style="dim")
    table.add_column("Title")
    table.add_column("Status", width=10)
    table.add_column("Depends On")
    table.add_column("Notes", max_width=40)

    for task in sorted(tasks.values(), key=lambda t: t.id):
        style = STATUS_STYLE.get(task.status, "white")
        notes = task.blocked_reason or ""
        table.add_row(
            task.id,
            task.title,
            f"[{style}]{task.status.value}[/]",
            ", ".join(task.depends_on) or "—",
            notes[:40],
        )

    console.print(table)

    # Stats
    from collections import Counter
    counts = Counter(t.status.value for t in tasks.values())
    total = len(tasks)
    done = counts.get("done", 0)
    console.print(
        f"\nTotal: {total} | "
        f"[green]Done: {done}[/] | "
        f"[yellow]Queue: {counts.get('queue', 0)}[/] | "
        f"[cyan]Active: {counts.get('active', 0)}[/] | "
        f"[red]Blocked: {counts.get('blocked', 0)}[/]"
    )
    if total:
        console.print(f"Progress: {done/total*100:.0f}%")


@cli.command()
@click.argument("task_id")
@click.pass_context
def show(ctx: click.Context, task_id: str):
    """Show details of a specific task, including its handover memo."""
    project_root: Path = ctx.obj["project_root"]
    hd = get_hive_dir(project_root)
    task = hd.load_task(task_id)

    if task is None:
        console.print(f"[red]Task not found:[/] {task_id}")
        sys.exit(1)

    console.print(f"[bold]Task:[/] {task.id}")
    console.print(f"[bold]Title:[/] {task.title}")
    console.print(f"[bold]Status:[/] {task.status.value}")
    console.print(f"[bold]Priority:[/] {task.priority.name}")
    console.print(f"[bold]Depends on:[/] {', '.join(task.depends_on) or 'none'}")
    console.print(f"[bold]Plan chapters:[/] {', '.join(task.plan_chapters) or 'none'}")
    console.print(f"\n[bold]Description:[/]\n{task.description}")
    console.print(f"\n[bold]Exit Criteria:[/]")
    for c in task.exit_criteria:
        console.print(f"  - {c}")

    if task.blocked_reason:
        console.print(f"\n[red]Blocked reason:[/] {task.blocked_reason}")

    memo = hd.load_handover(task_id)
    if memo:
        console.print(f"\n[bold]Handover Memo:[/]")
        console.print(memo.to_markdown())


@cli.command()
@click.argument("task_id")
@click.pass_context
def retry(ctx: click.Context, task_id: str):
    """Manually re-queue a blocked task."""
    project_root: Path = ctx.obj["project_root"]
    hd = get_hive_dir(project_root)
    task = hd.load_task(task_id)

    if task is None:
        console.print(f"[red]Task not found:[/] {task_id}")
        sys.exit(1)

    from hive.models.task import TaskStatus
    from hive.drone.state_machine import TaskStateMachine

    if task.status != TaskStatus.BLOCKED:
        console.print(f"[yellow]Task {task_id} is not blocked (status: {task.status.value})[/]")
        return

    sm = TaskStateMachine()
    task.retry_count = 0
    task = sm.transition(hd, task, TaskStatus.QUEUE, reason="manual retry")
    hd.save_task(task)
    console.print(f"[green]Task {task_id} re-queued.[/] Run 'hive run' to execute.")


def _show_dispatch_plan(tasks):
    """Print what the Drone would dispatch without running workers."""
    from hive.models.task import TaskStatus
    console.print("[dim]Dry run — no workers will be launched[/]\n")

    done_ids: set[str] = {
        tid for tid, t in tasks.items() if t.status == TaskStatus.DONE
    }
    ready = [
        t for t in tasks.values()
        if t.status == TaskStatus.QUEUE and set(t.depends_on).issubset(done_ids)
    ]

    table = Table(title="Dispatch Plan (Dry Run)")
    table.add_column("Task ID")
    table.add_column("Title")
    table.add_column("Would Run Now?")
    for task in sorted(tasks.values(), key=lambda t: t.id):
        would_run = task in ready
        table.add_row(
            task.id,
            task.title,
            "[green]Yes[/]" if would_run else "[dim]No[/]",
        )
    console.print(table)
