# Evaluation status

## Baseline and candidate

- `baseline_commit`: `e4d4f36`（修改前 `feat/obsidian-cli-knowledge-base` 分支提交）
- `candidate_commit`: `95fe827`（候选 Skill 提交）
- 评测资产：8 个 `train`，4 个 `holdout`

## 核验方法

本次执行的是可重复的结构与策略核验，不是实际 Agent 对照运行，也没有连接或修改真实 Obsidian Vault。核验检查：

- 主 `SKILL.md` 是否保留 frontmatter、CLI-first、只读/写入边界、私密路径保护和完成条件；
- 三个 reference 是否存在并由主 Skill 按任务分支明确指向；
- 详细创建、归档、审核步骤是否已经移出主 Skill；
- train/holdout JSON 的分割、唯一 ID、预期路由和断言是否完整；
- OpenSpec 是否通过严格校验，现有 `tests/verify.ps1` 和 `quick_validate.py` 是否通过。

## Result

- Train：8/8 评测案例具有可解析的预期路由和断言，全部通过结构/策略核验。
- Holdout：4/4 评测案例具有可解析的预期路由和断言，全部通过结构/策略核验。
- Reference 路由：3/3 目标 reference 存在且被主 Skill 指向。
- 安全边界：只读禁止写入、Vault 私密路径保护和变更后验证均保留。
- `scripts/`：未新增运行时脚本；确定性核验继续由 `tests/verify.ps1` 负责。

## Limitations

- 当前仓库没有独立的多代理行为评测运行器，因此没有声称旧版和新版的真实 Agent 完成率、工具顺序或 token 成本变化。
- 没有启动 Obsidian，也没有执行真实 Vault 写入、移动、重命名、提交或推送。
- 本次结果是策略/结构核验，不替代真实 Agent 行为对照；后续若接入行为评测运行器，应在同一 train/holdout 集上补充工具顺序、完成度和成本结果。
