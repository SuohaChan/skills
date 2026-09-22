# Proposal

## Why

当前 Skill 仓库已经具备目录规范、软链接安装、脚本测试和作者指南，但现有 Skill 的质量判断仍主要依赖少量人工案例。需要建立一套可审阅、可回归、能抵抗过拟合的 Skill 演进流程，确保未来 Agent 在修改 Skill 前先理解目标和边界，再根据证据施工。

## What Changes

- 建立 Skill 质量治理能力，覆盖触发边界、核心行为、失败处理和安全边界。
- 先只为 `obsidian-rag` 建立分层评测计划：触发正例、触发负例、质量案例、holdout 案例和历史回归案例；其他 Skill 暂不修改。
- 明确从对话经验提炼通用规则的方法，区分通用规则、个人偏好、实现细节和外部事实。
- 优化 Skill 的信息层级：保留核心流程，将分支细节和确定性操作分别放入 references 与 scripts。
- 采用旧版 Skill 与新版 Skill 的对照方式验证改动是否真正改善泛化能力，并保留独立 holdout 集合防止过拟合。
- 保留现有 Skill 的安全约束和用户可见行为；在测试证据不足前不直接重写现有 Skill。
- 使用 OpenSpec 变更目录保存提案、设计、任务和验证结果，完成后再归档为项目长期记录。

## Capabilities

### New Capabilities

- `skill-quality-governance`: 定义 Skill 的审查、评测、反过拟合、变更和交付规则。

### Modified Capabilities

无。当前项目尚未建立正式的 `openspec/specs/` 能力规格；本变更先建立治理能力，再按评测结果修改具体 Skill。

## Impact

- 影响 `D:\project\skill` 下的 Skill 作者文档、评测目录和后续 Skill 变更流程。
- 本次目标 Skill 仅为 `obsidian-rag`；`anime-schedule`、`desktop-screenshot` 和 `power-on-computer` 只作为后续可复用治理对象，不在本次变更中修改。
- 不引入新的运行时 MCP、API 或业务依赖。
- OpenSpec 规划文件会保存在 `openspec/changes/optimize-skill-library/`；实施完成后将归档并更新长期 specs。
