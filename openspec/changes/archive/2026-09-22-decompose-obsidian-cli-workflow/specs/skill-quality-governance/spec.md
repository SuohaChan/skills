# skill-quality-governance Specification

## MODIFIED Requirements

### Requirement: Skill content SHALL follow a single-source progressive hierarchy

Skill MUST 将每次触发都需要的核心流程、触发边界、安全限制和完成条件放在 `SKILL.md`；将只在特定任务分支需要的详细流程放在被主文件明确指向的 `references/`；将确定性和重复性操作放在 `scripts/` 或测试入口中，并避免在多个文件中重复维护同一事实。

#### Scenario: A multi-workflow Skill is reorganized

- **WHEN** 一个 Skill 同时覆盖创建、归档、审核或交付等多个任务分支
- **THEN** Agent SHALL 保留共享边界在 `SKILL.md`，为只在单一分支需要的细节建立明确的 reference 指针，并逐分支验证指针和完成条件

#### Scenario: No deterministic runtime operation exists

- **WHEN** 待拆内容包含用户意图判断或依赖 Vault 本地规则的自然语言决策
- **THEN** Agent SHALL 将其放入 reference，而不是为了满足目录结构强行创建运行时脚本

#### Scenario: A reference applies to one branch only

- **WHEN** 某段资料只在一个特定分支需要
- **THEN** Agent SHALL 将其放在被 `SKILL.md` 明确指向的 reference 文件中，而不是加入所有分支都会读取的主流程

#### Scenario: Runtime implementation changes

- **WHEN** 工具接口、路径或实现方式发生变化
- **THEN** Skill SHALL 以工具、配置或代码作为事实来源，并只保留仍然有效的使用策略

### Requirement: Skill evolution SHALL preserve an auditable record

每次正式 Skill 修改 MUST 记录旧版基线提交、新版候选提交、训练集、holdout、核验结果和已知限制；结构拆分也 MUST 说明没有改变的触发与安全边界。

#### Scenario: A progressive-disclosure change is reviewed

- **WHEN** Agent 完成一次 Skill 内容分层
- **THEN** 维护者 SHALL 能从 OpenSpec、Skill 分支提交和验证输出追溯每个被移动的流程及其核验结果

#### Scenario: Archiving a completed optimization

- **WHEN** 一次 Skill 优化已经完成并通过验证
- **THEN** 维护者 SHALL 能从变更记录追溯到提案、行为规格、任务清单和验证结果
