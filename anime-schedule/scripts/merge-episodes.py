#!/usr/bin/env python3
"""合并同日同番多集连播：EP1, EP2, EP3 → EP1~3。从 stdin 读 JSON，输出到 stdout。"""
import sys, json

def merge(data):
    groups = {}
    episode_values = {}
    order = []
    for index, item in enumerate(data):
        episode = item.get("episode")
        # 没有具体集数的周放送记录不参与合并，保留原始 null。
        key = ("unknown", index) if episode is None else ("known", item.get("title", ""))
        if key not in groups:
            groups[key] = dict(item)  # shallow copy
            if episode is not None:
                episode_values[key] = [str(episode)]
            order.append(key)
        else:
            ep = str(episode)
            if ep not in episode_values[key]:
                episode_values[key].append(ep)
    for key, values in episode_values.items():
        if len(values) == 1:
            groups[key]["episode"] = values[0]
            continue
        try:
            numbers = [int(value) for value in values]
        except ValueError:
            groups[key]["episode"] = "~".join(values)
        else:
            groups[key]["episode"] = f"{min(numbers)}~{max(numbers)}"
    return [groups[k] for k in order]

def main():
    data = json.load(sys.stdin)
    merged = merge(data)
    json.dump(merged, sys.stdout, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
