#!/usr/bin/env python3
"""读取配置，按优先级回退，输出统一番剧 JSON。"""
import argparse
import json
import math
import sys
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlparse

import requests

from adapters import ADAPTERS, SourceError, TZ

CONFIG = Path(__file__).resolve().parents[1] / "sources.json"


def load_config(path):
    with Path(path).open(encoding="utf-8-sig") as handle:
        config = json.load(handle)
    if not isinstance(config, dict) or not isinstance(config.get("sources"), list):
        raise ValueError("配置必须包含 sources 数组")
    if not isinstance(config.get("trust_env", False), bool):
        raise ValueError("trust_env 必须是布尔值")
    names = set()
    for source in config["sources"]:
        if not isinstance(source, dict):
            raise ValueError("每个源必须是对象")
        name = source.get("name")
        if not isinstance(name, str) or name not in ADAPTERS:
            raise ValueError(f"未注册的源：{name}")
        if name in names:
            raise ValueError(f"重复源：{name}")
        names.add(name)
        if not isinstance(source.get("enabled"), bool):
            raise ValueError(f"{name}: enabled 必须是布尔值")
        if type(source.get("priority")) is not int:
            raise ValueError(f"{name}: priority 必须是整数")
        timeout = source.get("timeout")
        if type(timeout) not in (int, float) or not math.isfinite(timeout) or timeout <= 0:
            raise ValueError(f"{name}: timeout 必须是正数")
        url = source.get("url")
        if not isinstance(url, str) or urlparse(url).scheme not in ("http", "https") or not urlparse(url).netloc:
            raise ValueError(f"{name}: 无效 URL")
    return config


def parse_target(value):
    today = datetime.now(TZ).date()
    offsets = {"today": 0, "tomorrow": 1, "yesterday": -1}
    if value in offsets:
        return today + timedelta(days=offsets[value])
    try:
        return datetime.strptime(value, "%d.%m.%Y").date()
    except ValueError as exc:
        raise ValueError("日期应为 today、tomorrow、yesterday 或 DD.MM.YYYY") from exc


def fetch_with_fallback(sources, target, session, report=None):
    report = report or (lambda message: print(message, file=sys.stderr))
    errors = []
    had_empty = False
    active = sorted((s for s in sources if s["enabled"]), key=lambda s: s["priority"])
    if not active:
        raise ValueError("没有启用的数据源")
    for source in active:
        try:
            items = ADAPTERS[source["name"]](session, source, target)
        except SourceError as exc:
            message = f"{source['name']}: {exc}"
            errors.append(message)
            report(message + "；继续下一源")
            continue
        if items:
            report(f"{source['name']}: 返回 {len(items)} 条")
            if items[0]["schedule_kind"] == "weekly":
                report("注意：这是常规周放送参考，不能确认当天实际更新、停播或集数。")
            return items
        had_empty = True
        report(f"{source['name']}: 空结果；继续下一源")
    if had_empty:
        if errors:
            report("部分源失败，查询不完整；本次未取得条目。")
        return []
    raise SourceError("所有源均失败：" + "；".join(errors))


def main():
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("date", nargs="?", default="today")
    parser.add_argument("--source", default="auto")
    parser.add_argument("--config", type=Path, default=CONFIG)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--list-sources", action="store_true")
    args = parser.parse_args()
    try:
        config = load_config(args.config)
        if args.list_sources:
            print(json.dumps(config["sources"], ensure_ascii=False, indent=2))
            return 0
        target = parse_target(args.date)
        sources = config["sources"]
        if args.source != "auto":
            sources = [s for s in sources if s["name"] == args.source]
            if not sources:
                raise ValueError(f"配置中没有源：{args.source}")
        with requests.Session() as session:
            session.trust_env = config.get("trust_env", False)
            session.headers.update({"Accept": "application/json", "User-Agent": "anime-schedule/1.0"})
            items = fetch_with_fallback(sources, target, session)
        output = items if args.json else {"date": target.isoformat(), "results": items}
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, SourceError) as exc:
        print(f"获取番剧数据失败：{exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
