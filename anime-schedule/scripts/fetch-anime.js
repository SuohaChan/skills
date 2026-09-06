#!/usr/bin/env node
/**
 * fetch-anime.js — Query AniList for day's anime schedule
 *
 * Usage:
 *   node fetch-anime.js [today|tomorrow|yesterday|DD.MM.YYYY]
 *
 * Output: text table with native title, romaji, english, episode, time, cover URL
 */

const https = require("https");
const DAY_MS = 86400000;

// ── helpers ──────────────────────────────────────────────

function graphql(query, variables = {}) {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify({ query, variables });
    const req = https.request(
      {
        hostname: "graphql.anilist.co",
        path: "/",
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Content-Length": Buffer.byteLength(data),
        },
      },
      (res) => {
        let body = "";
        res.on("data", (chunk) => (body += chunk));
        res.on("end", () => {
          try { resolve(JSON.parse(body)); }
          catch (e) { reject(e); }
        });
      }
    );
    req.on("error", reject);
    req.write(data);
    req.end();
  });
}

function parseDate(input) {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const offsetMs = today.getTimezoneOffset() * 60000;
  const localToday = new Date(today.getTime() - offsetMs);

  if (!input || input === "today") return localToday;
  if (input === "tomorrow") return new Date(localToday.getTime() + DAY_MS);
  if (input === "yesterday") return new Date(localToday.getTime() - DAY_MS);

  const m = input.match(/^(\d{2})\.(\d{2})\.(\d{4})$/);
  if (m) return new Date(+m[3], m[2] - 1, +m[1]);

  return localToday;
}

function dayRange(date) {
  const TZ_OFFSET = 8 * 3600000;
  const start = date.getTime() - TZ_OFFSET;
  return {
    startTimestamp: Math.floor(start / 1000),
    endTimestamp: Math.floor((start + DAY_MS) / 1000),
    dateStr: `${date.getDate().toString().padStart(2, "0")}.${(date.getMonth() + 1).toString().padStart(2, "0")}.${date.getFullYear()}`,
    weekday: ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"][date.getDay()],
  };
}

function formatTime(timestamp) {
  const d = new Date(timestamp * 1000);
  return `${d.getHours().toString().padStart(2, "0")}:${d.getMinutes().toString().padStart(2, "0")} GMT+8`;
}

// ── query ─────────────────────────────────────────────────

const SCHEDULE_QUERY = `
query ($startTime: Int, $endTime: Int, $page: Int) {
  Page(page: $page, perPage: 50) {
    pageInfo { hasNextPage }
    airingSchedules(
      airingAt_greater: $startTime
      airingAt_lesser: $endTime
      sort: TIME
    ) {
      media {
        title { romaji english native }
        coverImage { large medium }
        format
        siteUrl
      }
      episode
      airingAt
      timeUntilAiring
    }
  }
}`;

async function fetchSchedule(dateInput) {
  const date = parseDate(dateInput);
  const range = dayRange(date);
  const allResults = [];
  let page = 1;

  while (true) {
    const result = await graphql(SCHEDULE_QUERY, {
      startTime: range.startTimestamp,
      endTime: range.endTimestamp,
      page,
    });

    const schedules = result?.data?.Page?.airingSchedules || [];
    allResults.push(...schedules);

    if (!result?.data?.Page?.pageInfo?.hasNextPage) break;
    page++;
  }

  return { results: allResults, range };
}

// ── formatter ─────────────────────────────────────────────

function format(results, range) {
  const aired = results.filter((r) => r.timeUntilAiring <= 0);
  const upcoming = results.filter((r) => r.timeUntilAiring > 0);

  let out = "";
  out += `📺 ${range.weekday}, ${range.dateStr} — ${results.length} 部新番 (${upcoming.length} 部待播)\n\n`;

  for (const r of results) {
    const isAired = r.timeUntilAiring <= 0 ? " ✓" : "";
    const media = r.media;
    const native = media.title.native || media.title.romaji;
    const romaji = media.title.romaji;
    const ep = r.episode;
    const time = formatTime(r.airingAt);

    out += `  ${ep ? `EP${ep}` : "??"}  ${native}\n`;
    if (romaji && romaji !== native) out += `       ${romaji}\n`;
    if (media.title.english && media.title.english !== romaji && media.title.english !== native) {
      out += `       EN: ${media.title.english}\n`;
    }
    out += `       ⏰ ${time}${isAired}\n`;
    if (media.coverImage?.large) out += `       🖼️  ${media.coverImage.large}\n`;
    out += "\n";
  }

  out += `── 数据来自 AniList  •  https://anilist.co ──`;
  return out;
}

// ── main ──────────────────────────────────────────────────

async function main() {
  const args = process.argv.slice(2);
  const dateInput = args.find((a) => !a.startsWith("--")) || "today";

  const { results, range } = await fetchSchedule(dateInput);
  console.log(format(results, range));
}

main().catch((e) => {
  console.error("获取新番数据失败:", e.message);
  process.exit(1);
});
