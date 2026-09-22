# Design

## Context

当前 Skill 的主文件包含多个互相独立的任务分支。核心安全规则需要每次触发时可见，但创建、归档、审核、知识组织和 Git 交付的细节只在对应分支需要。设计遵循仓库现有 `skill-quality-governance` 规范和 Agent 文档的渐进披露原则。

## Goals / Non-Goals

**Goals:**

- 让主文件能快速决定是否触发、是否允许写入以及下一步该读哪个 reference。
- 让每个详细流程有单一事实来源，并保留完成核验。
- 用可重复的结构检查和 train/holdout 案例证明拆分没有扩大触发范围或削弱安全边界。

**Non-Goals:**

- 不把该 Skill 拆成多个独立 Skill。
- 不新增 Vault 分类体系，不替用户决定目录、属性或标签。
- 不把自然语言判断流程伪装成运行时脚本。
- 不实际操作 `D:\Obsidian Vault`，不执行真实笔记写入或远端 Git 操作。

## Decisions

### 1. 按任务分支拆 reference，而不是按命令拆 Skill

保留一个 Skill，因为所有分支共享 CLI-first、Vault 规则、安全保护和完成验证。创建/归档/审核放入 `references/workflows.md`，组织原则放入 `references/note-organization.md`，Git 交付放入 `references/git-delivery.md`。这样减少主文件负担，同时避免把共享约束复制到多个 Skill。

### 2. 主文件只保留指针和不可变边界

主文件保留触发描述、只读与写入边界、Vault 私密路径保护、CLI 作为事实来源、以及 reference 的读取条件。详细步骤必须由对应任务分支的指针触发后再读取。

### 3. 不为了拆分强行新增 scripts

创建、归档和审核包含用户意图判断，不能安全地硬编码成脚本。现有 `tests/verify.ps1` 负责确定性结构检查；只有未来出现稳定、重复且无业务判断的 CLI 检查时，才新增运行时脚本。

### 4. 评测验证路由和安全边界，而不是模拟真实 Vault

训练集覆盖创建、归档、审核、组织和 Git 请求；holdout 使用不同措辞覆盖相同边界。静态核验确认 reference 指针存在、读写限制仍在、测试文件完整。真实 Vault 端到端行为仍记录为未覆盖限制。

## Risks / Trade-offs

- [Reference 未被读取] → 在主文件使用明确的“当用户请求 X 时读取 Y”指针，并在 eval 中检查路由。
- [拆分后安全规则被遗漏] → 安全边界继续保留在主文件，并由验证脚本检查。
- [文件数量增加造成认知负担] → 只建立三个有明确任务分支的 reference，不再细分成更多文件。
- [静态评测高估真实能力] → 结果明确标注为策略/结构核验，不冒充真实 Obsidian MCP 或 Vault 写入评测。
