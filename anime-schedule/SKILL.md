---
name: anime-schedule
description: Query anime episode release schedules for today, tomorrow, or a season. Use when the user asks what anime is airing, when an episode releases, what's new today or tomorrow, or uses terms such as "新番", "动漫更新", "今天有什么番", "明天播什么", "这季新番", or "anime schedule".
---

# Anime Schedule

## 1. Fetch raw data

Run the script to get today/tomorrow's anime from AniList:

```
node "<skill-base>/scripts/fetch-anime.js" [today|tomorrow|yesterday|DD.MM.YYYY]
```

Where `<skill-base>` is the directory containing this `SKILL.md` (the active `anime-schedule` skill directory).

The script returns: Japanese native title, romaji, English title, episode number, airing time, cover image URL.

## 2. Translate to Chinese

### Step A — Check local cache

Read `<skill-base>/references/title-cache.json`. It maps Japanese native titles to Chinese translations. Use any existing matches.

### Step B — Search for missing titles

For any anime whose Japanese title is NOT in the cache, search the web to find its official Chinese name:

```
WebSearch: "{native title} 中文 译名"  or  "{romaji} 动漫 中文名"
```

Examples of authoritative sources: Bangumi (bgm.tv), Wikipedia, 萌娘百科, AniList's own synonyms.

**Use your judgment**: if the native title is already in Chinese characters (e.g. "仙逆", "绝世战魂"), it's a donghua — use it as-is, no search needed.

### Step C — Save to cache

After finding Chinese names, append new entries to `title-cache.json` so future lookups skip the search.

## 3. Filter blacklist

Before presenting results, read `<skill-base>/references/blacklist.json`. Remove any anime whose **exact native title** matches an entry in the blacklist from the results.

The blacklist format:
```json
{
  "entries": {
    "闇芝居 十七期": { "addedAt": "2026-07-13", "reason": "不感兴趣" },
    ...
  }
}
```

**Blacklisted anime are silently dropped** — do not mention them to the user unless they ask.

## 4. Present results

For each remaining anime, show:

```
EP{n}  中文名
       日文原名  (romaji)
       ⏰ HH:MM GMT+8  ✓/待播
       🖼️  cover-url
```

- Chinese name FIRST
- Japanese native + romaji underneath
- Cover image URL at the end

## 5. Blacklist management

When the user says things like "拉黑这个"、"黑名单"、"屏蔽"、"不看这个"、"以后别显示"、"block this" — manage the blacklist:

### Add to blacklist
- Read `blacklist.json`
- Add the entry using the anime's **exact native title from AniList** as key
- Save

### Remove from blacklist
- User says "取消拉黑"、"恢复"、"unblock"、"把XX放出来"
- Read `blacklist.json`
- Remove the matching entry (fuzzy match on the native title key)
- Save

### List blacklist
- User says "黑名单列表"、"看看屏蔽了哪些"、"blocklist"
- Read and display the current blacklist with Chinese names (look up from cache)

### Add/remove during schedule display
When showing the schedule, at the bottom add a line:
```
💡 想屏蔽某部番？告诉我"拉黑 XXX"即可。
```

## 6. Cache maintenance

- Cache file: `<skill-base>/references/title-cache.json`
- Format: `"Japanese native title": "Chinese translation"`
- Key is the EXACT `native` title from AniList
- Same anime different seasons → different entries
