# Skill 开发与安装规范

这是本仓库所有个人 Skill 的统一工作约定。仓库是唯一事实来源，运行目录只放指向仓库的链接。

## 目录约定

```text
D:\project\skill\
├── SKILL-DEVELOPMENT.md
├── <skill-name>\
│   ├── SKILL.md
│   ├── evals\
│   ├── references\
│   ├── scripts\
│   └── assets\
└── ...
```

每个 Skill 使用一个独立目录，目录名使用小写短横线命名；`SKILL.md` 必须位于该目录根部。只有确实需要时才创建 `evals`、`references`、`scripts` 或 `assets`。

## 版本基线、分支和合并流程

Git 是 Skill 版本的唯一基线。旧版和新版通过 commit、branch 和 diff 管理，不复制完整的 `SKILL.md` 作为长期快照。OpenSpec 记录变更意图、规格、任务和归档；评测记录行为证据；三者职责不同但必须互相引用。

每个真实 Skill 都有一个固定的功能分支，命名为 `feat/<skill-name>`。修改某个 Skill 时，只在它对应的分支工作；不要把单个 Skill 的修改直接写到 `master`。

分支映射示例：

```text
anime-schedule              -> feat/anime-schedule
desktop-screenshot          -> feat/desktop-screenshot
obsidian-cli-knowledge-base -> feat/obsidian-cli-knowledge-base
obsidian-rag                -> feat/obsidian-rag
power-on-computer           -> feat/power-on-computer
```

进入已有 Skill 分支：

```powershell
cd D:\project\skill
git switch feat/<skill-name>
# 记录本次工作的基线，不复制 Skill 文件：
git rev-parse HEAD
```

第一次建立某个 Skill 分支时，从当时的 `master` 创建；后续继续修改该 Skill 时复用同一个 `feat/<skill-name>` 分支。旧版基线是本次修改开始前的分支 commit，新版是验证后的最新 commit。比较时使用 Git：

```powershell
git diff <baseline-commit>...HEAD -- <skill-name>/SKILL.md
git show <baseline-commit>:<skill-name>/SKILL.md
```

分支范围必须清晰：

- Skill 分支承载对应 Skill 目录及其专属的脚本、参考资料、评测和行为变更记录；
- 整个 Skill 项目的规范、治理、仓库说明、根目录工具链和跨 Skill 管理直接在 `master` 修改；
- 修改前用 `git diff --name-only` 检查范围，禁止用 `git add .` 把项目级文件混入 Skill 提交。

如果评测工具需要不可变输入，可以在 OpenSpec 归档中保存评测元数据或 commit hash；只有工具明确不能读取 Git 时才保留文件快照。快照不是 Skill 的第二个事实来源，也不能被 Agent 当成主文件继续维护。

完成后按顺序检查：

1. `SKILL.md` 有合法 YAML frontmatter，至少包含 `name` 和 `description`；
2. description 写清楚 Skill 做什么以及什么时候触发；
3. 正文是可执行的工作流，不把无关百科内容全部塞进主文件；
4. 具体分支资料放在 `references/`，重复或机械操作放在 `scripts/`；
5. 为可验证的 Skill 写 `evals/evals.json`；
6. 运行结构检查和针对性验证；
7. 记录评测使用的旧版 commit、新版 commit、训练集、holdout 和已知限制；
8. 在对应 `feat/<skill-name>` 分支提交该 Skill 的变更：

```powershell
git add <skill-name>
git add openspec/changes/<change-name> .agents/skills/<generated-openspec-skills-if-added>
git commit -m "feat(skill): 用中文描述 Skill 修改"
```

验证通过后合并回 `master`：

```powershell
git switch master
git pull --ff-only
git merge --no-ff feat/<skill-name> -m "merge(skill): 用中文描述 Skill 合并"
```

合并后保留 `feat/<skill-name>` 作为该 Skill 的工作分支；下一次修改前先将它快进到最新 `master`：

```powershell
git switch feat/<skill-name>
git merge --ff-only master
```

如果合并冲突，先解决冲突、验证文件内容，再 `git add` 和 `git commit` 完成合并。不要用强制覆盖来消除冲突。

`master` 只接受已经完成验证的合并结果。若需要继续修改，基于最新 `master` 创建新的变更分支，不在已经合并的 commit 上直接改写历史。

## OpenSpec、Git 和评测的职责

一次 Skill 变更的推荐关系是：

```text
Git baseline commit
  -> OpenSpec proposal / spec / design / tasks
  -> feature branch implementation
  -> old-vs-new + holdout evaluation
  -> validated merge commit on master
  -> OpenSpec archive
```

- **Git**：保存版本、分支、差异和可恢复的旧版；旧版优先从 commit 读取。
- **OpenSpec**：保存为什么改、改什么、如何改、任务是否完成，以及归档后的长期规格。
- **评测**：证明新版相对于旧版是否改善，必须记录输入集合、版本 commit、结果和限制。

评测报告至少记录：

- `baseline_commit`：旧版 commit；
- `candidate_commit`：新版 commit；
- 使用的训练集、负例、holdout 和回归集；
- 触发、工具顺序、输出质量、安全边界等实际指标；
- 无法执行的部分和待人工验证内容。

不要只保存“新版结果很好”这类结论；未来 Agent 必须能从 commit 和评测文件重新定位新旧版本。

## Skill 内容设计

Skill 使用渐进式披露：

1. **元数据层**：frontmatter 的 `name`、`description`，用于触发判断；
2. **工作流层**：`SKILL.md` 中的核心步骤、边界和完成条件；
3. **参考层**：按分支读取 `references/`，不要让所有背景资料常驻上下文。

设计时遵循：

- description 同时写能力和触发场景；
- 步骤使用动作动词，并明确每一步何时完成；
- 把工具接口、环境配置和真实代码作为事实来源，不在 Skill 中复制容易过期的细节；
- 一个规则只保留一个权威位置，Skill 只描述使用方式；
- 给 Agent 正向行为和理由，少写无法验证的抽象要求；
- 让 Skill 能处理同一类请求，而不是只适配一个示例。

## 验证

优先使用 Skill Creator 的结构检查：

```powershell
$env:PYTHONUTF8 = "1"
uv run python C:\Users\yanme\.codex\skills\skill-creator\scripts\quick_validate.py D:\project\skill\<skill-name>
```

对有明确输出的 Skill，再运行 `evals/evals.json` 中的测试。验证触发、工具调用顺序、输出格式和失败处理，不只检查 Markdown 能否读取。

## 安装方式：运行目录只使用软连接

Skill 完成合并后，从仓库目录创建到 Codex 运行目录的目录软连接。优先使用 SymbolicLink；Windows 未开启开发者模式且没有管理员权限时，使用 Junction 作为目录链接，不复制文件：

```powershell
$source = "D:\project\skill\<skill-name>"
$target = "C:\Users\yanme\.agents\skills\<skill-name>"
New-Item -ItemType SymbolicLink -Path $target -Target $source
# 无权限时的 Windows 目录链接替代：
New-Item -ItemType Junction -Path $target -Target $source
```

不要把 Skill 目录复制到运行目录。复制会产生两个事实来源，后续修改容易出现运行版本和仓库版本不一致。安装后用下面的命令确认链接：

```powershell
Get-Item "C:\Users\yanme\.agents\skills\<skill-name>" | Format-List FullName,LinkType,Target
```

如果目标已存在，先确认它是指向本仓库的链接；不要直接删除未知目录。Windows 创建 SymbolicLink 需要相应权限；Junction 仍然是链接而不是第二份目录。无论使用哪种链接，都不能用复制目录冒充安装。

## 本地 RAG Skill 的实例

`obsidian-rag` 遵循这套规范：

- 源码：`D:\project\skill\obsidian-rag`；
- 独立 Skill 分支：`feat/obsidian-rag`；
- MCP 工具：`search_notes`、`read_note`、`index_status`；
- Skill 只规定检索时机、调用顺序和引用规则，不复制 Chroma 实现；
- 合并后通过软连接安装到 `.agents\skills\obsidian-rag`。
