#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 demo/i18n/<lang>.json 合进 demo/index.html 的内联字典。

真值（single source）：
  demo/i18n/zh.json   中文源串清单（数组）—— 键就是页面上的中文原文/模板
  demo/i18n/en.json   {中文源串: 英文}
  demo/i18n/ja.json   {中文源串: 日文}
  demo/i18n/ko.json   {中文源串: 韩文}
  （加语言 = 新建一个 <lang>.json 并登记进 LANGS，不用改 index.html 的逻辑）

用法：
  python3 demo/build_i18n.py --extract   # 从 index.html 现有字典导出 i18n/*.json
  python3 demo/build_i18n.py --check     # 只校验，不写文件
  python3 demo/build_i18n.py             # 校验通过后写回 index.html
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
I18N_DIR = ROOT / "i18n"
PAGE = ROOT / "index.html"
LANGS = ["en", "ja", "ko"]  # zh 是源语言，不单独存翻译

BEGIN = "/* I18N:BEGIN"
END = "/* I18N:END */"
PLACEHOLDER = re.compile(r"\{(\w+)\}")


def load(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, data) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8")


def page_text() -> str:
    return PAGE.read_text(encoding="utf-8")


def extract() -> None:
    """从 index.html 抽取 en 字典，并把代码里 T()/Tf() 的中文模板并入 zh 键表。"""
    src = page_text()
    m = re.search(r"const I18N = (\{.*?\});\n", src, re.S)
    if not m:
        sys.exit("找不到内联字典 const I18N = {...};")
    raw = json.loads(m.group(1))

    # 兼容两种形态：旧 {zh: en} ／ 新 {en: {zh: en}, ja: ...}
    if raw and all(isinstance(v, str) for v in raw.values()):
        en = raw
    else:
        en = raw.get("en", {})

    I18N_DIR.mkdir(parents=True, exist_ok=True)
    dump(I18N_DIR / "en.json", en)
    if not (I18N_DIR / "zh.json").exists():
        dump(I18N_DIR / "zh.json", sorted(en.keys()))

    for lang in LANGS[1:]:
        f = I18N_DIR / f"{lang}.json"
        if not f.exists():
            dump(f, {})
    print(f"导出完成：en {len(en)} 条；zh {len(load(I18N_DIR / 'zh.json', []))} 条")


def code_strings() -> list:
    """扫 index.html 里的 T('…') / Tf('…') / T(`…`) 字面量，要求它们都在 zh.json 里。"""
    src = page_text()
    found = []
    for m in re.finditer(r"\bTf?\(\s*(?:'((?:[^'\\]|\\.)*)'|`((?:[^`\\]|\\.)*)`)", src):
        found.append(m.group(1) if m.group(1) is not None else m.group(2))
    return found


def validate() -> list:
    zh = load(I18N_DIR / "zh.json", [])
    errs = []
    if not zh:
        return ["i18n/zh.json 为空或不存在"]
    zhset = set(zh)

    for lit in code_strings():
        if lit not in zhset:
            errs.append(f"代码里的字符串没进 zh.json：{lit[:60]!r}")

    for lang in LANGS:
        data = load(I18N_DIR / f"{lang}.json", {})
        missing = sorted(zhset - set(data))
        extra = sorted(set(data) - zhset)
        if missing:
            errs.append(f"{lang}.json 缺 {len(missing)} 条，例如：" + " / ".join(repr(x[:28]) for x in missing[:3]))
        if extra:
            errs.append(f"{lang}.json 多出 {len(extra)} 条（zh.json 里没有），例如：" + " / ".join(repr(x[:28]) for x in extra[:3]))
        for key, val in data.items():
            if key in zhset and PLACEHOLDER.findall(key) != PLACEHOLDER.findall(val):
                errs.append(f"{lang}.json 占位符不一致：{key[:30]!r} → {val[:40]!r}")
    return errs


def build() -> None:
    zh = load(I18N_DIR / "zh.json", [])
    data = {lang: load(I18N_DIR / f"{lang}.json", {}) for lang in LANGS}
    payload = {k: v for k, v in data.items() if v}  # zh 不落盘：缺键即回退中文
    blob = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))

    src = page_text()
    lines = src.split("\n")
    start = next((i for i, l in enumerate(lines) if l.startswith(BEGIN)), None)
    if start is None:
        sys.exit("index.html 里找不到 I18N:BEGIN 标记；先手工把 const I18N = {...}; 换成标记包裹。")
    end = next(i for i in range(start, len(lines)) if lines[i].startswith(END))
    block = [
        lines[start],
        "const I18N = " + blob + ";",
        lines[end],
    ]
    out = "\n".join(lines[:start] + block + lines[end + 1:])
    PAGE.write_text(out, encoding="utf-8")
    total = sum(len(v) for v in payload.values())
    print(f"注入完成：{len(payload)} 种语言 / {total} 条；页面 {round(len(out.encode()) / 1024)} KB")


def main() -> None:
    args = set(sys.argv[1:])
    if "--extract" in args:
        extract()
        return
    errs = validate()
    if errs and "--force" not in args:
        print("校验未通过：")
        for e in errs[:40]:
            print(" -", e)
        if len(errs) > 40:
            print(f" …共 {len(errs)} 条")
        sys.exit(1)
    if errs:
        print(f"（--force：带 {len(errs)} 处缺口继续注入，缺的键回退中文）")
    if "--check" in args:
        print("校验通过（i18n 全语言齐备）")
        return
    print("校验通过")
    build()


if __name__ == "__main__":
    main()
