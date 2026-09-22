# Tasks

## 1. 建立基线和评测资产

- [x] 1.1 记录 `obsidian-rag` 的触发范围、输入输出、工具依赖、失败边界和已知限制，并核对结果与 `SKILL-AUTHORING-GUIDE.md` 及 `SKILL-DEVELOPMENT.md` 一致
- [x] 1.2 为 `obsidian-rag` 建立触发正例、触发负例、质量案例、holdout 和回归案例，并验证覆盖个人知识、一般知识、无结果、冲突和引用完整性
- [x] 1.3 明确本次不修改 `anime-schedule`、`desktop-screenshot` 和 `power-on-computer`，并验证变更差异只涉及 `obsidian-rag`、评测资产和 OpenSpec 文档

## 2. 优化 Skill 结构和规则

- [x] 2.1 根据基线结果修改 `obsidian-rag/SKILL.md` 的触发边界和证据处理规则，并验证正例、负例和 holdout 均保持预期行为
- [x] 2.2 只移动 `obsidian-rag/SKILL.md` 中明显依赖当前环境、路径或易变实现的内容，并验证核心检索流程、引用规则和失败边界仍在主 Skill 中
- [x] 2.3 将默认实现与不可变约束分开记录，并验证可替换的默认值不会被描述成跨环境必须成立的规则

## 3. 对照评测和回归

- [x] 3.1 保存 `obsidian-rag` 修改前的旧版基线结果，并对训练案例执行旧 Skill、新 Skill 的对照，验证新版本没有降低核心任务完成度
- [x] 3.2 在不使用 holdout 修改规则的前提下运行 holdout，验证新版本没有只对原始案例变好而对未见输入退化
- [x] 3.3 运行仓库结构检查、`obsidian-rag` 相关脚本测试和行为评测，验证所有测试结果、失败原因和已知限制均被记录
- [x] 3.4 对通过评测的变更执行 OpenSpec 验证并审阅差异，确认实现范围与 proposal、spec、design、tasks 一致

## 4. 归档与后续维护

- [x] 4.1 将确认有效的长期治理规则同步到 `openspec/specs/skill-quality-governance/spec.md`，并验证归档后的规格仍包含完整场景
- [x] 4.2 为 `obsidian-rag` 记录来源、覆盖案例、已知限制和版本变更，验证未来 Agent 能从变更记录追溯修改依据
- [x] 4.3 归档 `optimize-skill-library` 变更并检查工作树，验证没有把缓存、截图、真实配置或临时评测输出提交到仓库
