# Tasks

## Baseline and evaluation

- [x] 1.1 记录 `feat/obsidian-cli-knowledge-base` 当前提交作为旧版基线，不复制长期维护的旧版 Skill
- [x] 1.2 新增训练集与 holdout，覆盖创建、归档、审核、组织、只读审计和 Git 交付边界
- [x] 1.3 定义每个案例的预期 reference 路由、禁止动作和完成核验

## Progressive disclosure

- [x] 2.1 从主 `SKILL.md` 提取创建、归档、审核的详细步骤到 `references/workflows.md`
- [x] 2.2 提取知识组织、属性、标签、链接和模板原则到 `references/note-organization.md`
- [x] 2.3 提取 Git 状态、提交和推送边界到 `references/git-delivery.md`
- [x] 2.4 在主 `SKILL.md` 保留共享安全边界，并添加按任务分支读取 reference 的指针

## Verification

- [x] 3.1 扩充 `tests/verify.ps1`，验证 frontmatter、核心安全段落、reference 指针、评测分割和 JSON 结构
- [x] 3.2 运行结构检查、现有测试、训练集和 holdout 核验；不触发真实 Vault 写入
- [x] 3.3 记录旧版/新版提交、结果和限制，确认未新增不必要的 `scripts/`

## Delivery

- [x] 4.1 在 `feat/obsidian-cli-knowledge-base` 提交 Skill、OpenSpec 和核验资产
- [ ] 4.2 将该分支以 `--no-ff` 合并到 `master`，保留 Skill 分支停留在新版 Skill 提交
- [ ] 4.3 推送 `master` 和对应 Skill 分支，并核对远端提交
