# 07 Acceptance 模板

## Purpose

- 提供标准 Acceptance Record 结构。
- 保证 Task 完成结论独立于 Worker 自报。

## Template

```md
# Acceptance Record

## Metadata
- Acceptance ID:
- Task ID:
- Handoff ID:
- Run ID:

## Input Set
- Task Ref:
- Handoff Ref:
- Artifact Refs:
- Validation Refs:

## Result
- accepted / rejected / needs_followup / partial_accepted

## Evidence Summary
- code validation:
- test validation:
- requirement validation:
- integration validation:

## Reason
- 

## Followup Actions
- 
```

## Checklist

- Input Set 完整
- Evidence Summary 可验证
- Result 枚举明确
- Followup Actions 可执行
