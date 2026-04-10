# 03 Task Spec 模板

## Purpose

- 提供标准 Task Spec 结构。
- 保证 Task 可派发、可验证、可恢复。

## Template

```md
# Task Spec

## Metadata
- Task ID:
- Phase ID:
- Plan Revision ID:

## Objective
-

## Scope
-

## Constraints
-

## Plan References
-

## Allowed Paths
-

## Forbidden Paths
-

## Dependencies
-

## Path Locks
- write:
- read:

## Done Criteria
-

## Validation Method
-

## Output Expectations
-

## Escalation Rule
-

## Retry Policy
-
```

## Checklist

- Objective 明确
- Scope 有边界
- Allowed / Forbidden Paths 明确
- Done Criteria 可验证
- Validation Method 可执行
- Escalation Rule 明确
- 依赖关系已写出
