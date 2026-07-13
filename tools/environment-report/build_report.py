#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build a formatted environment report (connectors / skills / plugins) from a JSON
snapshot produced by the ListConnectors / ListSkills / ListPlugins tools.

Usage:
    python3 build_report.py <input.json> [--out report.md] [--lang en|he]
"""

import argparse
import json
from datetime import datetime

STRINGS = {
    "en": {
        "title": "Environment Report — Claude / Cowork",
        "generated": "Generated",
        "summary": "Summary",
        "active": "Active connectors (usable right now)",
        "off": "Connected, but off in this chat (enable in connector settings)",
        "notconn": "Not connected (need authentication/setup)",
        "skills": "Enabled skills",
        "plugins": "Enabled plugins",
        "usage": "Account usage (tokens / quota / billing)",
        "usage_body": ("Usage, quota, plan tier, and billing are **not** accessible from a session. "
                       "Check your account under **Settings → Usage / Billing** "
                       "(or **console.anthropic.com → Usage** for API/Console users)."),
        "c_active": "active connectors",
        "c_off": "connected but off in this chat",
        "c_not": "not connected",
        "c_skills": "skills enabled",
        "c_plugins": "plugins enabled",
        "none": "_(none)_",
    },
    "he": {
        "title": "דוח סביבה — Claude / Cowork",
        "generated": "נוצר בתאריך",
        "summary": "סיכום",
        "active": "מחברים פעילים (זמינים לשימוש עכשיו)",
        "off": "מחוברים, אך כבויים בצ'אט הזה (יש להפעיל בהגדרות המחברים)",
        "notconn": "לא מחוברים (דורשים אימות/הגדרה)",
        "skills": "כישורים מופעלים",
        "plugins": "תוספים מופעלים",
        "usage": "שימוש בחשבון (טוקנים / מכסה / חיוב)",
        "usage_body": ("נתוני שימוש, מכסה, תוכנית וחיוב **אינם** נגישים מתוך השיחה. "
                       "בדוק בחשבון תחת **Settings → Usage / Billing** "
                       "(או **console.anthropic.com → Usage** למשתמשי API/Console)."),
        "c_active": "מחברים פעילים",
        "c_off": "מחוברים אך כבויים בצ'אט",
        "c_not": "לא מחוברים",
        "c_skills": "כישורים מופעלים",
        "c_plugins": "תוספים מופעלים",
        "none": "_(אין)_",
    },
}


def norm_names(items):
    """Accept a list of strings or list of {'name': ...} dicts efficiently."""
    if not items:
        return []
    return [
        it if isinstance(it, str) else it["name"]
        for it in items
        if isinstance(it, str) or (isinstance(it, dict) and "name" in it)
    ]


def classify(connectors):
    """Classify connectors into buckets efficiently."""
    active, off, notconn = [], [], []

    for c in (connectors or []):
        if not isinstance(c, dict):
            continue
        name = c.get("name", "?")
        desc = (c.get("description") or "").strip()
        connected = c.get("connected", None)
        in_chat = c.get("enabledInChat", False)
        entry = (name, desc)

        if connected is True:
            if in_chat:
                active.append(entry)
            else:
                off.append(entry)
        else:
            notconn.append(entry)

    active.sort(key=lambda e: e[0].lower())
    off.sort(key=lambda e: e[0].lower())
    notconn.sort(key=lambda e: e[0].lower())

    return active, off, notconn


def render(data, lang, now):
    s = STRINGS.get(lang, STRINGS["en"])
    active, off, notconn = classify(data.get("connectors"))

    skills = sorted(norm_names(data.get("skills")), key=str.lower)
    plugins = sorted(norm_names(data.get("plugins")), key=str.lower)

    L = []

    if lang == "he":
        L.append('<div dir="rtl">\n')

    L.append(f"# {s['title']}\n")
    L.append(f"*{s['generated']}: {now}*\n")

    # Summary
    L.append(f"## {s['summary']}\n")
    L.append(f"- **{len(active)}** {s['c_active']}\n")
    L.append(f"- **{len(off)}** {s['c_off']}\n")
    L.append(f"- **{len(notconn)}** {s['c_not']}\n")
    L.append(f"- **{len(skills)}** {s['c_skills']}\n")
    L.append(f"- **{len(plugins)}** {s['c_plugins']}\n")

    def section(title, entries, with_desc=True):
        L.append(f"## {title}\n")
        if not entries:
            L.append(f"{s['none']}\n\n")
            return

        for i, e in enumerate(entries, 1):
            if with_desc and isinstance(e, tuple):
                name, desc = e
                L.append(f"{i}. **{name}** — {desc}\n" if desc else f"{i}. **{name}**\n")
            else:
                L.append(f"{i}. {e}\n")
        L.append("")

    section(f"✓ {s['active']}", active)
    section(f"◐ {s['off']}", off)
    section(f"○ {s['notconn']}", notconn)
    section(s["skills"], skills, with_desc=False)
    section(s["plugins"], plugins, with_desc=False)

    L.append(f"## {s['usage']}\n")
    L.append(f"{s['usage_body']}\n")

    if lang == "he":
        L.append("</div>")

    counts = {
        "active": len(active), "off": len(off), "not_connected": len(notconn),
        "skills": len(skills), "plugins": len(plugins),
    }
    return "".join(L), counts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input", help="Path to the JSON snapshot")
    ap.add_argument("--out", default="environment_report.md")
    ap.add_argument("--lang", default="en", choices=["en", "he"])
    ap.add_argument("--now", default=None, help="Timestamp string (default: now)")
    args = ap.parse_args()

    with open(args.input, encoding="utf-8") as f:
        data = json.load(f)

    now = args.now or datetime.now().strftime("%Y-%m-%d %H:%M")
    report, counts = render(data, args.lang, now)

    with open(args.out, "w", encoding="utf-8") as f:
        f.write(report + "\n")

    print(f"[ok] wrote {args.out}")
    print(f"[summary] active={counts['active']} "
          f"off={counts['off']} not_connected={counts['not_connected']} "
          f"skills={counts['skills']} plugins={counts['plugins']}")


if __name__ == "__main__":
    main()
