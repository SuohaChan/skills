# anime-schedule

Agent skill — 查询每日新番播出表，中日双语名 + 封面图 + 黑名单过滤。

## 安装

```bash
将整个目录放入当前 Agent 的 skills 目录，例如：

```text
<skills-root>/anime-schedule
```
```

## 依赖

- Node.js ≥ 18
- 能访问 `graphql.anilist.co`（AniList GraphQL API，无需 API Key）

## 用法

在 Agent 对话中直接提问即可，触发词包括：

> 今天有什么番 / 明天播什么 / 这季新番 / 动漫更新 ...

skill 会自动：
1. 从 AniList 抓当天播出数据
2. 日文原名 → 中文译名（查缓存 + 联网搜索）
3. 过滤黑名单
4. 展示结果（中文名 / 日文名 / 封面图 / 播出时间）

## 黑名单

| 操作 | 这样说 |
|------|--------|
| 拉黑 | "拉黑 暗芝居" |
| 取消拉黑 | "取消拉黑 暗芝居" |
| 查看 | "黑名单列表" |

## 文件结构

```
├── SKILL.md                    # 技能定义
├── scripts/
│   └── fetch-anime.js          # AniList 数据抓取
└── references/
    ├── title-cache.json        # 日→中翻译缓存（越用越准）
    └── blacklist.json          # 黑名单
```

## 给 Agent 用

如果你要把这个 skill 给另一个 agent（如 QQ 机器人），只需：

1. 把整个目录克隆过去
2. 让 agent 先跑 `node scripts/fetch-anime.js today` 拿原始数据
3. 再自己处理翻译 + 过滤逻辑，或者直接用 SKILL.md 里的完整工作流

脚本的输出格式是纯文本，方便下游任意格式化（QQ 消息 / 网页 / RSS 等）。

## License

MIT
