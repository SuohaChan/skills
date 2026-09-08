---
name: anime-schedule
description: Query anime episode release schedules and generate a card-grid image when useful. Use this skill whenever the user asks about anime airing times, new episodes, what's airing today/tomorrow, today's anime, a new-anime guide, an anime schedule, or an anime schedule poster, including "新番", "动漫更新", "今天有什么番", "明天播什么", "这季新番", "anime schedule", "新番导视", "今日新番", "今日番剧", "追番清单".
---

# Anime Schedule

## 1. 拉取数据

```bash
cd <skill-directory> && python3 scripts/fetch_anime.py today --json
```
参数：`today` / `tomorrow` / `yesterday` / `DD.MM.YYYY`；数据源配置在 `sources.json`，脚本按 `priority` 逐条尝试。默认 `--source auto`，也可用 `--source anilist`、`--source jikan`、`--source tsuzuki` 或 `--source bangumi` 指定数据源。Tsuzuki 提供按日期的集数和播出时间；Bangumi 提供番剧列表和星期信息，缺少集数或精确播出时间时统一输出 JSON `null`。

脚本加 `--json` 时输出 JSON 数组；字段示例见 `references/fetch-anime-output.example.json`。
失败或空结果会继续下一源，首个非空结果即返回；所有源失败时以非零状态退出。最终输出 `[]` 表示本次没有取得条目，不一定证明当天没有更新，请结合 stderr 的错误提示判断。

`schedule_kind=episode` 是按日期查询的集数记录；`weekly` 是常规周放送参考，不能确认当天实际更新或停播。AniList 和 Tsuzuki 返回 `episode`，Jikan 和 Bangumi 返回 `weekly`。周放送源仅支持近期日期。维护数据源、适配器及代理配置时参见 README 的“抓取模块”。

## 2. 翻译中文名

- 读状态缓存 `data/title-cache.json`
- 保留 `title` 原名；优先使用源提供的 `title_cn`，缺失时在此步骤补译名
- 缺失的根据你的知识翻译 → 写回缓存
- 中文原名直接用

## 3. 获取简介

- 读状态缓存 `data/desc-cache.json`
- 缓存有则直接用，没有就根据你的知识编20-40字（类型+看点）
- 编完写回缓存
- JSON 里加 `description` 字段

## 4. 合并多集连播

用 `merge-episodes.py` 合并同日同番多集（EP1,EP2,EP3 → EP1~3）：

```bash
echo '<JSON>' | python3 scripts/merge-episodes.py > merged.json
```

再读回 `merged.json` 继续后续步骤。

## 5. 生成拼图

```bash
cd <skill-directory> && echo '<JSON>' | python3 scripts/make-grid.py --rows 4 --cols 2 --output-dir <output-directory>
```
默认布局是 4 行 2 列，每页最多 8 部；可用 `--rows 2 --cols 4` 或 `--rows 3 --cols 3` 切换布局。每部番剧先渲染为独立 Card，再由布局器合成大图。默认图片输出到技能目录的 `output/`；需要交给宿主应用发送时，用 `--output-dir` 指定宿主的图片目录。封面缓存默认在技能目录的 `cover_cache/`，也可用 `--cache-dir` 覆盖。

## 6. 发送

`send_message_to_user` 每页一张：
```
📺 7月16日 周三 — 13部 (1/2)
{图}
```

## 7. 管理缓存

- 清某部简介：删 `data/desc-cache.json` 中对应条目
- 清所有简介：`data/desc-cache.json` 重置为 `{}`
- 清某部译名：删 `data/title-cache.json` 中对应条目

## 8. 黑名单

- 读 `data/blacklist.json`
- 拉黑 → 加日文原名 → 写回
- 取消 → 模糊匹配删 → 写回


## 9. 单部详情

用户问"XXX是什么番"/"XXX介绍"/"XXX什么时候播"时：

1. 从 `python3 scripts/fetch_anime.py today --json` 找到目标（当天列表不保证包含所有番剧）
2. 封面走缓存 `cover_cache/{md5}.jpg`
3. 写一段详细介绍（80-150字）
4. 用 `send_message_to_user` 发：**先图后文**

```json
{"messages": [
  {"type": "image", "path": "{make-grid.py 输出的图片路径}"},
  {"type": "plain", "text": "{中文名}\n{日文原名}\nEP{n} | ⏰ {HH:MM}\n\n{详细介绍}"}
]}
```
