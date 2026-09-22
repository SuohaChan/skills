---
name: anime-schedule
description: 查询动画播出日程并生成拼图卡片或单番介绍。用户询问播出时间、新集、今天/明天有什么番、季度导视或某部动画时使用，包括“新番”“动漫更新”“今日番剧”“追番清单”。
compatibility: 需要 Python 3.13+ 和项目依赖；优先使用 uv 运行项目脚本。
---

# Anime Schedule

## 运行环境

从 `anime-schedule` 技能目录执行脚本。项目使用 `pyproject.toml` 和 `uv.lock` 管理依赖；优先使用 `uv run python`，确保脚本使用项目对应的 Python 和依赖环境。不要直接调用宿主机的 `python` 或 `python3`，因为它们可能指向不同版本或缺少依赖。

## 日程卡片

以下命令从 `anime-schedule` 技能目录执行。

1. 抓取指定日期：

   ```bash
   uv run python scripts/fetch_anime.py today --json
   ```

   按需将 `today` 替换为 `tomorrow`、`yesterday` 或 `DD.MM.YYYY`。数据源按配置优先级依次尝试；失败或空结果会继续下一源，全部失败时命令以非零状态退出。`[]` 表示本次未取得条目，不足以证明当天没有播出。

2. 整理条目：
   - 读取 `data/blacklist.json` 并过滤命中条目。
   - 保留原名 `title`；优先采用源提供的 `title_cn`，否则查 `data/title-cache.json`，缺失时补译并写回。
   - 查 `data/desc-cache.json`；缺失时补写 20–40 字简介，概括类型和看点。
   - 未知集数或时间保留 JSON `null`，不要用总集数推测当日集数。

3. 合并同日同番的多集记录：

   ```bash
   uv run python scripts/merge-episodes.py < input.json > merged.json
   ```

   后续使用 `merged.json`。

4. 生成卡片：

   ```bash
   uv run python scripts/make-grid.py --rows 4 --cols 2 --output-dir <output-directory> < merged.json
   ```

   默认每页 4 行 2 列，最多 8 部；单部卡片用 `--rows 1 --cols 1`。脚本默认读取 `data/recommend.json` 并突出显示命中条目；也可在单次输入条目上设置 `recommended: true`。默认图片和封面缓存目录分别为 `output/`、`cover_cache/`。需要交给宿主应用发送时，将 `--output-dir` 指向宿主的图片目录。

5. 每页发送一张图，并附日期和页码，例如：`📺 7月16日 周三 — 13部 (1/2)`。

`episode` 表示按日期查询到的集数记录；`weekly` 是常规周放送参考，不能确认当天实际更新或停播。AniList 和 Tsuzuki 返回 `episode`；Jikan 和 Bangumi 返回 `weekly`，且周放送源仅支持近期日期。维护数据源或适配器时参见 README 的“抓取模块”。

## 单部详情

用户问“XXX是什么番”“XXX介绍”或“XXX什么时候播”时：

1. 先在指定日期的结果中查找；未找到时再按番名查询数据源，不能据此断定该番不存在。
2. 按上文缓存规则准备译名和卡片简介；封面由 `make-grid.py` 使用缓存处理。
3. 用 `--rows 1 --cols 1` 生成单卡，另写 80–150 字的详细介绍。
4. 先发卡片图片，再发中文名、原名、已知的集数/时间和详细介绍。未知字段显示“未知”。

## 名单与缓存维护

- **推荐名单：** 编辑 `data/recommend.json`；名称按精确值匹配，源标题有不同写法时为同一部番补上各别名。格式示例见 `references/recommend.json.example`。
- **黑名单：** 将原名加入 `data/blacklist.json` 以屏蔽；移除对应条目即可取消。
- **译名或简介：** 从 `data/title-cache.json` 或 `data/desc-cache.json` 删除对应条目以便刷新；重置为 `{}` 可清空整个缓存。

输入输出字段示例见 `references/fetch-anime-output.example.json`。数据源优先级、适配器、代理配置和其他命令说明见 README。
