"""数据源适配器：请求、解析、标准化；不翻译或生成简介。"""
from datetime import datetime, timedelta, timezone

import requests

TZ = timezone(timedelta(hours=8))
JST = timezone(timedelta(hours=9))
WEEKDAYS = ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")


class SourceError(Exception):
    """网络故障、响应无效或数据源不支持当前查询。"""


def request_json(session, config, payload=None, params=None):
    try:
        with session.request(
            "POST" if payload is not None else "GET",
            config["url"], json=payload, params=params,
            timeout=config["timeout"],
        ) as response:
            try:
                data = response.json()
            except ValueError as exc:
                raise SourceError(f"HTTP {response.status_code}: 返回内容不是 JSON") from exc
            if not response.ok:
                detail = data.get("errors") or data.get("message") if isinstance(data, dict) else None
                raise SourceError(f"HTTP {response.status_code}: {str(detail)[:300]}")
            return data
    except requests.RequestException as exc:
        raise SourceError(str(exc)) from exc


def mapping(value, label):
    if not isinstance(value, dict):
        raise SourceError(f"{label} 应为对象")
    return value


def array(value, label):
    if not isinstance(value, list):
        raise SourceError(f"{label} 应为数组")
    return value


def item(config, kind, **values):
    result = dict.fromkeys((
        "source_id", "title", "title_cn", "romaji",
        "episode", "time", "cover", "site_url",
    ))
    result.update({key: None if value == "" else value for key, value in values.items()})
    if not isinstance(result["title"], str) or not result["title"].strip():
        raise SourceError("作品缺少原名")
    result.update(source=config["name"], schedule_kind=kind)
    return result


def check_weekly_date(target):
    # 周放送接口没有历史快照；仅用于当前日附近的常规放送参考。
    today = datetime.now(TZ).date()
    if not today - timedelta(days=1) <= target <= today + timedelta(days=6):
        raise SourceError("仅提供当前周放送参考，不支持该历史或远期日期")


QUERY = """
query ($startTime: Int, $endTime: Int, $page: Int) {
  Page(page: $page, perPage: 50) {
    pageInfo { hasNextPage }
    airingSchedules(airingAt_greater: $startTime, airingAt_lesser: $endTime, sort: TIME) {
      media { id title { native romaji english } coverImage { large } siteUrl }
      episode airingAt
    }
  }
}
"""


def fetch_anilist(session, config, target):
    start = datetime(target.year, target.month, target.day, tzinfo=TZ)
    output = []
    for number in range(1, 101):
        data = mapping(request_json(session, config, {
            "query": QUERY,
            "variables": {
                "startTime": int(start.timestamp()) - 1,
                "endTime": int((start + timedelta(days=1)).timestamp()),
                "page": number,
            },
        }), "response")
        if data.get("errors"):
            raise SourceError(str(data["errors"])[:300])
        page = mapping(mapping(data.get("data"), "data").get("Page"), "Page")
        for entry in array(page.get("airingSchedules"), "airingSchedules"):
            entry = mapping(entry, "schedule")
            media = mapping(entry.get("media"), "media")
            titles = mapping(media.get("title"), "title")
            stamp = entry.get("airingAt")
            try:
                formatted = datetime.fromtimestamp(stamp, TZ).strftime("%H:%M GMT+8") if stamp is not None else None
            except (TypeError, ValueError, OverflowError, OSError) as exc:
                raise SourceError("无效 airingAt") from exc
            output.append(item(
                config, "episode", source_id=media.get("id"),
                title=titles.get("native") or titles.get("romaji") or titles.get("english"),
                romaji=titles.get("romaji"),
                episode=entry.get("episode"), time=formatted,
                cover=mapping(media.get("coverImage") or {}, "coverImage").get("large"),
                site_url=media.get("siteUrl"),
            ))
        more = mapping(page.get("pageInfo"), "pageInfo").get("hasNextPage")
        if not isinstance(more, bool):
            raise SourceError("缺少有效分页标志")
        if not more:
            return output
    raise SourceError("分页超过 100 页，拒绝返回不完整结果")


def fetch_jikan(session, config, target):
    check_weekly_date(target)
    output = []
    # JST 次日 00:00–00:59 属于北京时间当天，需同时查询两个星期分组。
    for japan_date in (target, target + timedelta(days=1)):
        for number in range(1, 101):
            data = mapping(request_json(session, config, params={
                "filter": WEEKDAYS[japan_date.weekday()], "page": number, "sfw": "true",
            }), "response")
            for anime in array(data.get("data"), "data"):
                anime = mapping(anime, "anime")
                broadcast = mapping(anime.get("broadcast") or {}, "broadcast")
                raw = broadcast.get("time")
                formatted = None
                if raw:
                    if broadcast.get("timezone") != "Asia/Tokyo":
                        raise SourceError("不支持的 broadcast.timezone")
                    try:
                        parsed = datetime.strptime(raw, "%H:%M").time()
                        local = datetime.combine(japan_date, parsed, tzinfo=JST).astimezone(TZ)
                    except (TypeError, ValueError) as exc:
                        raise SourceError("无效 broadcast.time") from exc
                    if local.date() != target:
                        continue
                    formatted = local.strftime("%H:%M GMT+8")
                elif japan_date != target:
                    continue
                images = mapping(anime.get("images") or {}, "images")
                jpg = mapping(images.get("jpg") or {}, "jpg")
                output.append(item(
                    config, "weekly", source_id=anime.get("mal_id"),
                    title=anime.get("title_japanese") or anime.get("title"),
                    time=formatted,
                    cover=jpg.get("large_image_url") or jpg.get("image_url"),
                    site_url=anime.get("url"),
                ))
            more = mapping(data.get("pagination"), "pagination").get("has_next_page")
            if not isinstance(more, bool):
                raise SourceError("缺少有效分页标志")
            if not more:
                break
        else:
            raise SourceError("分页超过 100 页")
    return output


def fetch_bangumi(session, config, target):
    check_weekly_date(target)
    groups = array(request_json(session, config), "calendar")
    for group in groups:
        group = mapping(group, "weekday group")
        if mapping(group.get("weekday"), "weekday").get("id") != target.isoweekday():
            continue
        output = []
        for entry in array(group.get("items"), "items"):
            entry = mapping(entry, "subject")
            images = mapping(entry.get("images") or {}, "images")
            output.append(item(
                config, "weekly", source_id=entry.get("id"),
                title=entry.get("name"), title_cn=entry.get("name_cn"),
                cover=images.get("large") or images.get("common"),
                site_url=entry.get("url"),
            ))
        return output
    raise SourceError("calendar 缺少目标星期分组")


def fetch_tsuzuki(session, config, target):
    data = mapping(request_json(
        session, config,
        params={"start": target.isoformat(), "days": 1},
    ), "response")
    if data.get("ok") is not True:
        raise SourceError(str(data.get("error") or "接口返回 ok=false")[:300])

    output = []
    for entry in array(data.get("episodes"), "episodes"):
        entry = mapping(entry, "episode")
        if entry.get("isBreak"):
            continue
        stamp = entry.get("airingAt")
        try:
            formatted = (
                datetime.fromtimestamp(stamp, TZ).strftime("%H:%M GMT+8")
                if stamp is not None else None
            )
        except (TypeError, ValueError, OverflowError, OSError) as exc:
            raise SourceError("无效 airingAt") from exc
        output.append(item(
            config, "episode", source_id=entry.get("mediaId"),
            title=entry.get("title"), episode=entry.get("episode"),
            time=formatted, cover=entry.get("coverImage"),
        ))
    return output


ADAPTERS = {
    "anilist": fetch_anilist,
    "jikan": fetch_jikan,
    "bangumi": fetch_bangumi,
    "tsuzuki": fetch_tsuzuki,
}
