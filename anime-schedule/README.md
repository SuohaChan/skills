# anime-schedule

Claude Code skill — 查询每日新番播出表，原名 + 中文译名 + 封面图 + 黑名单过滤。

## 安装

```bash
git clone https://github.com/SuohaChan/skills.git <skills-directory>/skills
# 技能目录为：<skills-directory>/skills/anime-schedule
```

## 依赖

- Python 3.13+
- 推荐安装 [uv](https://docs.astral.sh/uv/)，项目依赖由 `pyproject.toml` 和 `uv.lock` 管理
- Pillow 10+（拼图渲染，已包含在 `requirements.txt`）
- 至少能访问 `sources.json` 中一个已启用的数据源

### 使用 uv（推荐）

在技能目录执行：

```bash
uv sync
uv run python scripts/fetch_anime.py today --json
```

### 不使用 uv

也可以使用 Python 标准虚拟环境和 pip。先在技能目录创建并激活 `.venv`，再安装依赖：

Windows：

```powershell
py -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python scripts\fetch_anime.py today --json
```

Linux/macOS：

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/fetch_anime.py today --json
```

## 用法

在 Claude Code 对话中直接问就行了，触发词包括：

> 今天有什么番 / 明天播什么 / 这季新番 / 动漫更新 ...

skill 会自动：
1. 按配置顺序尝试数据源，取得播出记录或周放送参考
2. 数据源原名 → 中文译名（查缓存 + 联网搜索）
3. 过滤黑名单
4. 展示结果（中文译名 / 原名 / 封面图 / 播出时间）

## 黑名单

| 操作 | 这样说 |
|------|--------|
| 拉黑 | "拉黑 暗芝居" |
| 取消拉黑 | "取消拉黑 暗芝居" |
| 查看 | "黑名单列表" |

## 文件结构

```
├── SKILL.md                    # 技能定义
├── sources.json                # 源地址、开关、优先级、超时及 trust_env
├── data/                       # Agent 维护的运行状态
│   ├── title-cache.json        # 日→中翻译缓存
│   ├── desc-cache.json         # 简介缓存
│   └── blacklist.json          # 黑名单
├── cover_cache/                # 运行时封面缓存
├── output/                     # 默认生成图片目录
├── scripts/
│   ├── fetch_anime.py          # 多数据源抓取与统一 JSON 输出
│   ├── adapters.py             # 请求封装、各源适配器与注册表
│   ├── merge-episodes.py       # 合并同番多集记录
│   ├── make-grid.py            # Card 渲染与行列拼图
│   ├── test_make_grid.py       # 拼图单元测试
│   └── test_merge_episodes.py  # 合并单元测试
└── references/
    ├── title-cache.json.example
    └── blacklist.json.example
```

## 给 Agent 用

如果你要把这个 skill 给另一个 agent（如 QQ 机器人），只需：

1. 把整个目录克隆过去
2. 让 agent 在技能目录执行 `uv run python scripts/fetch_anime.py today --json` 拿原始数据；若宿主没有 uv，先按上面的 pip/venv 方式准备环境
3. 再自己处理翻译 + 过滤逻辑，或者直接用 SKILL.md 里的完整工作流

`--json` 的 stdout 是 JSON 数组；诊断信息写入 stderr，方便下游解析。

`make-grid.py` 会根据自身位置定位字体、缓存和默认输出目录，不依赖宿主应用或固定绝对路径。它先把每部番剧渲染成独立 Card，再按行列合成大图；默认 `--rows 4 --cols 2`，也可切换为 `--rows 2 --cols 4`、`--rows 3 --cols 3`。需要交给宿主应用发送时，用 `--output-dir <宿主图片目录>` 指定图片目录，也可用 `--cache-dir` 指定封面缓存目录。

## 抓取模块

```bash
uv run python scripts/fetch_anime.py today --json
uv run python scripts/fetch_anime.py today --source bangumi --json
uv run python -B -m unittest discover -s scripts -p 'test_*.py' -v
```

`fetch_anime.py` 负责配置校验、北京时间日期、命令行和顺序回退；`adapters.py` 用 `ADAPTERS[name]` 选择函数，把各源响应转换成统一 JSON。无需额外的策略类或重复的 `adapter` 配置字段。

- `priority` 越小越先尝试；失败或空结果继续，首个非空结果返回，不合并不同源。所有源失败则非零退出；有源返回空数组而其余失败时输出 `[]` 并警告查询不完整。
- 已有源的地址、开关、顺序、超时只改配置。当前优先级为 Tsuzuki → AniList → Jikan → Bangumi；新增不同响应格式的源，需要在 `adapters.py` 实现并注册适配器，再加配置。
- `trust_env` 默认 `false`，避免本机代理配置干扰；需要继承系统/环境代理时改为 `true`，同时也会恢复 requests 对环境证书设置等的读取。
- `title` 保留原名；`title_cn` 仅存源提供的中文名，后续流程再补翻译。未知字段统一为 `null`，不把总集数当作当日更新集数。
- `schedule_kind` 为 `episode` 或 `weekly`。Jikan、Bangumi 是周放送参考，仅接受北京时间昨天至未来六天；它们不能确认某日实际更新或停播。AniList、Tsuzuki 返回按日期的集数记录；Jikan 已知日本播出时间转换为北京时间；Bangumi 缺少精确时间时保持 `null`。
- Tsuzuki 是免密钥的缓存日程源，公开部署时应按其要求注明 AniList 与 Tsuzuki 数据来源。
- 输出字段示例见 `references/fetch-anime-output.example.json`，示例不是实时数据。下游应将未知时间/集数显示为“未知”，而不是推测补齐。

## License

MIT
