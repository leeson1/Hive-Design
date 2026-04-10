# 02 Execution Plan 规范（演进层）

## Purpose

- 定义演进层执行对象。
- 约束 Phase、Task 来源、验证路径与 revision 链。

## Rules

### Execution Plan 必备内容

- 阶段划分与顺序
- 模块计划
- 任务来源
- 退出准则
- 调整记录
- revision 链
- acceptance 与 validation 提取结果

## 与 Charter 关系

- Execution Plan 不得违反 Charter。
- 若冲突，先走 Decision，再更新计划。

### Revision Discipline

- Execution Plan 的运行中变化必须写成 revision。
- Task 必须绑定到具体 `plan_revision_id`。

## Acceptance Criteria

- 任一执行中的 Task 都能追溯到 Execution Plan revision。
- 任一 Plan 调整都能说明影响了哪些 Phase / Task。
