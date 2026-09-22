# skill-quality-governance Specification

## Purpose
为本仓库的 Agent Skill 建立可审阅、可测试、可回归的质量治理能力，使 Skill 的改动依据可观察证据推进，并能够区分通用工作流与一次性案例，降低个人偏好和单案例造成的过拟合风险。

## Requirements

### Requirement: Skill changes SHALL have an explicit behavioral scope

每个新增或修改的 Skill MUST 明确任务目标、触发场景、非目标、主要输入、预期输出和失败边界。评测或施工计划不得只依据聊天中隐含的上下文。

#### Scenario: Reviewing a proposed Skill change
- **WHEN** Agent 准备新增或修改一个 Skill
- **THEN** Agent SHALL 先写出该 Skill 的行为范围和非目标，并区分观察到的事实、假设和拟议行为

#### Scenario: A rule is supported by only one example
- **WHEN** 某条规则只能解释一个具体案例且无法迁移到至少三种不同输入
- **THEN** Agent SHALL 将其保留为候选经验，不得直接写入正式 Skill 作为通用规则

### Requirement: Skill changes SHALL be evaluated against diverse cases

每个具有明确行为的 Skill MUST 至少覆盖触发正例、触发负例、质量案例和历史回归案例；对容易过拟合的改动 MUST 保留开发期间不用于改规则的 holdout 案例。

#### Scenario: A trigger boundary is tested
- **WHEN** 评估 Skill 是否应该被调用
- **THEN** 测试集 SHALL 同时包含应该触发的任务和语义相近但不应该触发的任务

#### Scenario: A new rule improves a known example
- **WHEN** 新规则改善训练案例但使 holdout 或负例变差
- **THEN** Agent SHALL 将该结果标记为泛化退化，不得仅凭训练案例通过就合并

### Requirement: Skill behavior SHALL be compared with a baseline

对行为型 Skill 的实质修改 MUST 在可行时比较无 Skill、旧 Skill 和新 Skill 的结果，并记录任务完成度、遗漏、误触发、工具顺序、安全边界和额外成本中的适用指标。

#### Scenario: Comparing two Skill versions
- **WHEN** Agent 提交影响工作流行为的 Skill 修改
- **THEN** Agent SHALL 说明新版本相对于旧版本改善、退化或未变化的可观察结果

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
