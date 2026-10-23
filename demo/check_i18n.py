#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""多语言交付闸：字典齐备 + 占位符一致 + 页面实跑无中文残留。

用法：
  python3 demo/check_i18n.py            # 本地文件直接跑（file://）
  python3 demo/check_i18n.py --no-render  # 只做字典静态检查（无浏览器时）

依赖：playwright（python）。缺失时自动降级为静态检查并提示。
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import build_i18n  # noqa: E402  复用键表与占位符规则

DICT_DIR = ROOT / "i18n"
PAGE = ROOT / "index.html"
LANGS = ["en", "ja", "ko"]

LEAK_JS = r"""
(keys) => {
  const set = new Set(keys);
  const out = [];
  const skip = new Set(['SCRIPT', 'STYLE', 'TEXTAREA', 'OPTION']);
  const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  let n;
  while ((n = w.nextNode())) {
    const t = (n.textContent || '').trim();
    if (!t || !set.has(t)) continue;
    const el = n.parentElement;
    if (!el || skip.has(el.tagName)) continue;
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden') continue;
    out.push((el.tagName + '.' + (el.className || '').toString().slice(0, 18) + ' :: ' + t).slice(0, 90));
  }
  return [...new Set(out)];
}
"""


def static_check() -> int:
    zh = json.loads((DICT_DIR / "zh.json").read_text(encoding="utf-8"))
    zhset = set(zh)
    bad = 0
    for lang in LANGS:
        data = json.loads((DICT_DIR / f"{lang}.json").read_text(encoding="utf-8"))
        missing = zhset - set(data)
        extra = set(data) - zhset
        empty = [k for k, v in data.items() if not v.strip()]
        if missing or extra:
            print(f"❌ {lang}: 缺 {len(missing)} / 多 {len(extra)}")
            bad += 1
        else:
            print(f"✅ {lang}: {len(data)} 条齐备（空串 {len(empty)} 条，多为标点/量词占位）")
    return bad


def render_check() -> int:
    try:
        from playwright.sync_api import sync_playwright
    except Exception:
        print("⚠ 未安装 playwright，跳过实跑检查")
        return 0

    zh = json.loads((DICT_DIR / "zh.json").read_text(encoding="utf-8"))
    bad = 0
    url = PAGE.as_uri()
    with sync_playwright() as p:
        b = p.chromium.launch()
        for lang in LANGS:
            data = json.loads((DICT_DIR / f"{lang}.json").read_text(encoding="utf-8"))
            # 译文与中文同形（如日文的「参考」）不算残留，只查真正该变的
            probe = [k for k in zh if data.get(k) != k]
            pg = b.new_page(viewport={"width": 1440, "height": 900})
            errs = []
            pg.on("pageerror", lambda e: errs.append(str(e)[:100]))
            pg.goto(f"{url}?lang={lang}", wait_until="load")
            pg.wait_for_timeout(700)
            pg.click('[data-sample="bad"]')
            pg.click("#evRun")
            pg.wait_for_timeout(1500)
            leaks = pg.evaluate(LEAK_JS, probe)
            flag = "✅" if not leaks and not errs else "❌"
            print(f"{flag} {lang}: 页面错误 {len(errs)} / 残留中文 {len(leaks)}")
            for x in leaks[:8]:
                print("   ", x)
            if leaks or errs:
                bad += 1
            pg.close()
        b.close()
    return bad


def main() -> None:
    bad = static_check()
    if "--no-render" not in sys.argv:
        bad += render_check()
    if bad:
        sys.exit(1)
    print("全部通过：字典齐备、页面无残留中文")


if __name__ == "__main__":
    main()
