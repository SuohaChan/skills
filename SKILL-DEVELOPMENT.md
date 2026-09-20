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

## 分支和合并流程

一个 Skill 的修改必须在自己的分支完成，不直接在 `master` 编写：

```powershell
cd D:\project\skill
git switch master
git pull --ff-only
git switch -c feat/<skill-name>
```

完成后按顺序检查：

1. `SKILL.md` 有合法 YAML frontmatter，至少包含 `name` 和 `description`；
2. description 写清楚 Skill 做什么以及什么时候触发；
3. 正文是可执行的工作流，不把无关百科内容全部塞进主文件；
4. 具体分支资料放在 `references/`，重复或机械操作放在 `scripts/`；
5. 为可验证的 Skill 写 `evals/evals.json`；
6. 运行结构检查和针对性验证；
7. 提交该 Skill 的变更：

```powershell
git add <skill-name> SKILL-DEVELOPMENT.md
git commit -m "feat(<skill-name>): add skill"
```

再合并回 `master`：

```powershell
git switch master
git merge --no-ff feat/<skill-name> -m "merge(<skill-name>): add skill"
git branch -d feat/<skill-name>
```

如果合并冲突，先解决冲突、验证文件内容，再 `git add` 和 `git commit` 完成合并。不要用强制覆盖来消除冲突。

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
python C:\Users\yanme\.codex\skills\skill-creator\scripts\quick_validate.py D:\project\skill\<skill-name>
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
