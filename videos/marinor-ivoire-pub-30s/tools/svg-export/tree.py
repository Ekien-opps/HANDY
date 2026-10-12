#!/usr/bin/env python3
"""Compact view of qa.mjs --inspect JSON: one line per node with id/text, bbox and on-canvas %."""
import json, sys
data = json.load(sys.stdin)
min_on = int(sys.argv[1]) if len(sys.argv) > 1 else 1
def walk(nodes, d, path):
    for i, n in enumerate(nodes):
        if n.get("onCanvasPct", 0) < min_on and n["tag"] == "g":
            print("  " * d + f"[OFF] {n.get('id') or n['tag']} ({n['nodes']} nodes)"); continue
        label = n.get("id") or ("“" + n["text"] + "”" if n.get("text") else n["tag"])
        if n["tag"] != "g" and not n.get("id") and not n.get("text"): continue
        print("  " * d + f"{label}  bbox={n['bbox']} on={n['onCanvasPct']}% nodes={n['nodes']}")
        if n.get("children"): walk(n["children"], d + 1, path)
walk(data, 0, "")
