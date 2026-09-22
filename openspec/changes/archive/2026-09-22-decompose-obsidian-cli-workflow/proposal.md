# Proposal

## Why

`obsidian-cli-knowledge-base/SKILL.md` 同时承载 CLI 安全边界、Vault 规则、知识组织原则、创建/归档/审核流程和 Git 交付流程。它目前约 11KB；不同任务只需要其中一部分，全部内联会增加上下文负担，也容易让 Agent 在不适用的任务中执行过多步骤。

本次在已经建立 Skill 分支和评测治理之后，补上这个 Skill 的渐进披露层级，并用训练集与 holdout 核验拆分没有改变触发边界和安全边界。

## What Changes

- 保留 `SKILL.md` 中的触发范围、CLI-first、安全边界、Vault 规则优先级、只读/写入区分和完成条件。
- 将创建、归档、审核等详细流程移到 `references/workflows.md`。
- 将文件夹、属性、标签、链接和模板等组织原则移到 `references/note-organization.md`。
- 将提交、推送和仓库状态检查的详细交付流程移到 `references/git-delivery.md`。
- 在主 Skill 中为上述 reference 增加按任务分支触发的明确指针。
- 扩充现有验证脚本，检查 reference 指针、评测分割和关键安全边界。
- 新增训练集与 holdout 评测案例，记录旧版/新版提交和已知限制。
- 暂不新增运行时 `scripts/`；现有 `tests/verify.ps1` 继续作为确定性验证入口。

## Capabilities

### New Capabilities

无。本次不新增独立 Skill 能力。

### Modified Capabilities

- `skill-quality-governance`：修改现有 Skill 必须通过渐进披露层级、基线对比、训练集和 holdout 核验，并记录可追溯结果。

## Impact

- 影响 `obsidian-cli-knowledge-base/SKILL.md`、其 `references/`、`evals/` 和 `tests/verify.ps1`。
- 不修改真实 Vault，不调用 Obsidian CLI 写入命令，不改变 Git 远端状态。
- 不改变 Skill 名称和触发范围，只改变详细流程的加载位置。
