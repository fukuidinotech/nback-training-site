#!/usr/bin/env python3
"""nback-training-site の共通部分（head の alternate・ヘッダー・フッター・更新日）を
全言語ぶん書き戻す。

各 HTML は次の3つの目印を持つ。目印のあいだはこのスクリプトが上書きするので、
手で書かない。目印の外（title / description / 本文）だけを手で書く。

    <!--chrome:alt-->   ... <!--/chrome:alt-->
    <!--chrome:head-->  ... <!--/chrome:head-->
    <!--chrome:foot-->  ... <!--/chrome:foot-->

法務ページの更新日は `<div class="meta" data-updated="YYYY-MM-DD">` の日付から
言語ごとの書き方で埋める。**日付を直すのは data-lang 属性の1か所だけ**でよい。

使い方: python3 tools/i18n.py        （全ファイルを書き戻す）
        python3 tools/i18n.py --check（差分が出るなら異常終了。CI 用）
"""
from __future__ import annotations

import hashlib
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = "https://fukuidinotech.github.io/nback-training-site/"

# ja は repo 直下。公開済みの URL（App Store の marketing_url・アプリ内リンク）を
# 動かさないため、ja だけサブディレクトリを持たない
PAGES = ["index.html", "privacy.html", "terms.html", "disclaimer.html"]
NAV_PAGES = PAGES
FOOT_PAGES = ["privacy.html", "terms.html", "disclaimer.html"]
CONTACT = "fukuidinotech@gmail.com"

LANGS = {
    "ja": {
        "dir": "", "native": "日本語", "pick": "言語を選ぶ",
        "nav": ["ホーム", "プライバシー", "利用規約", "免責事項"],
        "foot": ["プライバシーポリシー", "利用規約", "免責事項", "お問い合わせ"],
        "updated": "最終更新日", "date": "{y}年{m}月{d}日",
    },
    "en": {
        "dir": "en", "native": "English", "pick": "Choose a language",
        "nav": ["Home", "Privacy", "Terms", "Disclaimer"],
        "foot": ["Privacy Policy", "Terms of Use", "Disclaimer", "Contact"],
        "updated": "Last updated", "date": "{month} {d}, {y}",
    },
    "zh-Hans": {
        "dir": "zh-Hans", "native": "简体中文", "pick": "选择语言",
        "nav": ["首页", "隐私政策", "使用条款", "免责声明"],
        "foot": ["隐私政策", "使用条款", "免责声明", "联系我们"],
        "updated": "最后更新", "date": "{y}年{m}月{d}日",
    },
    "zh-Hant": {
        "dir": "zh-Hant", "native": "繁體中文", "pick": "選擇語言",
        "nav": ["首頁", "隱私權政策", "使用條款", "免責聲明"],
        "foot": ["隱私權政策", "使用條款", "免責聲明", "聯絡我們"],
        "updated": "最後更新", "date": "{y}年{m}月{d}日",
    },
    "ko": {
        "dir": "ko", "native": "한국어", "pick": "언어 선택",
        "nav": ["홈", "개인정보", "이용약관", "면책조항"],
        "foot": ["개인정보 처리방침", "이용약관", "면책조항", "문의"],
        "updated": "최종 업데이트", "date": "{y}년 {m}월 {d}일",
    },
    "de": {
        "dir": "de", "native": "Deutsch", "pick": "Sprache wählen",
        "nav": ["Start", "Datenschutz", "Nutzungsbedingungen", "Haftungsausschluss"],
        "foot": ["Datenschutzerklärung", "Nutzungsbedingungen", "Haftungsausschluss", "Kontakt"],
        "updated": "Zuletzt aktualisiert", "date": "{d}. {month} {y}",
    },
    "fr": {
        "dir": "fr", "native": "Français", "pick": "Choisir la langue",
        "nav": ["Accueil", "Confidentialité", "Conditions", "Avertissement"],
        "foot": ["Politique de confidentialité", "Conditions d'utilisation", "Avertissement", "Contact"],
        "updated": "Dernière mise à jour", "date": "{d} {month} {y}",
    },
    "es": {
        "dir": "es", "native": "Español", "pick": "Elegir idioma",
        "nav": ["Inicio", "Privacidad", "Términos", "Aviso legal"],
        "foot": ["Política de privacidad", "Términos de uso", "Aviso legal", "Contacto"],
        "updated": "Última actualización", "date": "{d} de {month} de {y}",
    },
    "pt": {
        "dir": "pt", "native": "Português", "pick": "Escolher idioma",
        "nav": ["Início", "Privacidade", "Termos", "Aviso legal"],
        "foot": ["Política de Privacidade", "Termos de Uso", "Aviso legal", "Contato"],
        "updated": "Última atualização", "date": "{d} de {month} de {y}",
    },
    "it": {
        "dir": "it", "native": "Italiano", "pick": "Scegli la lingua",
        "nav": ["Home", "Privacy", "Termini", "Avvertenze"],
        "foot": ["Informativa sulla privacy", "Termini di utilizzo", "Avvertenze legali", "Contatti"],
        "updated": "Ultimo aggiornamento", "date": "{d} {month} {y}",
    },}

# 月の名前が要る言語だけ持つ（ja / zh / ko は数字で書く）
MONTHS = {
    "en": ["", "January", "February", "March", "April", "May", "June",
           "July", "August", "September", "October", "November", "December"],
    "de": ["", "Januar", "Februar", "März", "April", "Mai", "Juni",
           "Juli", "August", "September", "Oktober", "November", "Dezember"],
    "fr": ["", "janvier", "février", "mars", "avril", "mai", "juin",
           "juillet", "août", "septembre", "octobre", "novembre", "décembre"],
    "es": ["", "enero", "febrero", "marzo", "abril", "mayo", "junio",
           "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"],
    "pt": ["", "janeiro", "fevereiro", "março", "abril", "maio", "junho",
           "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"],
    "it": ["", "gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno",
           "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre"],
}


def url_for(lang: str, page: str) -> str:
    d = LANGS[lang]["dir"]
    return BASE + (f"{d}/{page}" if d else page)


def rel(from_lang: str, to_lang: str, page: str) -> str:
    """from_lang のページから to_lang の同じページへの相対パス"""
    src, dst = LANGS[from_lang]["dir"], LANGS[to_lang]["dir"]
    if src == dst:
        return page
    up = "../" if src else ""
    return f"{up}{dst}/{page}" if dst else f"{up}{page}"


def asset(lang: str, name: str) -> str:
    """style.css や images/ は repo 直下に1つだけ置く"""
    return f"../{name}" if LANGS[lang]["dir"] else name


_css_version: str | None = None


def css_version() -> str:
    """`style.css` の中身から作る短い印。**手で上げない。**

    HTML と CSS は別々にキャッシュされる。GitHub Pages は両方に `max-age=600` を付けるので、
    CSS を変えた直後は「新しい HTML ＋ 古い CSS」で見る人が出る。
    URL に中身の印を入れておけば、CSS を直した時点で URL も変わるので必ず取り直しになる。
    **中身から導出しているので上げ忘れが起きない。**
    """
    global _css_version
    if _css_version is None:
        _css_version = hashlib.sha256((ROOT / "style.css").read_bytes()).hexdigest()[:8]
    return _css_version


def date_text(lang: str, iso: str) -> str:
    y, m, d = (int(v) for v in iso.split("-"))
    cfg = LANGS[lang]
    month = MONTHS[lang][m] if "{month}" in cfg["date"] else ""
    return f'{cfg["updated"]}: ' + cfg["date"].format(y=y, m=m, d=d, month=month)


def block_alt(lang: str, page: str) -> str:
    lines = [f'<link rel="canonical" href="{url_for(lang, page)}">']
    for other in LANGS:
        lines.append(f'<link rel="alternate" hreflang="{other}" href="{url_for(other, page)}">')
    # 一致する言語が無い人には英語を出す
    lines.append(f'<link rel="alternate" hreflang="x-default" href="{url_for("en", page)}">')
    lines.append('<link rel="preconnect" href="https://fonts.googleapis.com">')
    lines.append('<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>')
    lines.append('<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700'
                 '&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">')
    lines.append(f'<link rel="icon" href="{asset(lang, "images/app-icon.png")}">')
    lines.append(f'<link rel="apple-touch-icon" href="{asset(lang, "images/app-icon.png")}">')
    lines.append(f'<link rel="stylesheet" href="{asset(lang, "style.css")}?v={css_version()}">')
    return "\n".join(lines)


# **言語の自動振り分け（JS）は入れない。**
#
# 2026-09-20 にこのサイトを「JS で辞書を差し替える1 URL」から言語別サブディレクトリへ移した。
# 入口の振り分けは `hreflang`（block_alt）と言語切替（block_head）に任せる。
# kakesu-lp で一度 JS の振り分けを入れて外した経緯がある（外から書ける値を遷移先に使うため、
# 検証を1つ落とすと外部 URL へ飛ばせる穴になる）。同じものをここで作り直さない。
# 作り直すなら、急ぎではないので人のレビューを通してから。


def block_head(lang: str, page: str) -> str:
    cfg = LANGS[lang]
    out = ['<header class="site-header">', '  <div class="container">',
           f'    <a href="{rel(lang, lang, "index.html")}" class="brand">',
           '      <span class="brand-mark">N</span>',
           '      <span>N-Back Training</span>', '    </a>', '    <nav class="nav">']
    for name, label in zip(NAV_PAGES, cfg["nav"]):
        cur = ' aria-current="page"' if name == page else ""
        out.append(f'      <a href="{name}"{cur}>{label}</a>')
    # 言語切替。JS を使わない（GitHub Pages に置くだけで動くようにする）
    out.append('      <details class="langpick">')
    out.append(f'        <summary aria-label="{cfg["pick"]}">{cfg["native"]}</summary>')
    out.append('        <ul>')
    for other, ocfg in LANGS.items():
        cur = ' aria-current="true"' if other == lang else ""
        out.append(f'          <li><a lang="{other}" hreflang="{other}" '
                   f'href="{rel(lang, other, page)}"{cur}>{ocfg["native"]}</a></li>')
    out.append('        </ul>')
    out.append('      </details>')
    out.append('    </nav>')
    out.append('  </div>')
    out.append('</header>')
    return "\n".join(out)


def block_foot(lang: str, page: str) -> str:
    cfg = LANGS[lang]
    out = ['<footer>', '  <div class="container">', '    <div>']
    for name, label in zip(FOOT_PAGES, cfg["foot"]):
        out.append(f'      <a href="{name}">{label}</a>')
    out.append(f'      <a href="mailto:{CONTACT}">{cfg["foot"][3]}</a>')
    out.append('    </div>')
    out.append('    <div>&copy; 2026 Toru Fukui</div>')
    out.append('  </div>')
    out.append('</footer>')
    return "\n".join(out)


BLOCKS = {"alt": block_alt, "head": block_head, "foot": block_foot}


def apply(text: str, lang: str, page: str) -> str:
    for key, fn in BLOCKS.items():
        pattern = re.compile(f"(<!--chrome:{key}-->).*?(<!--/chrome:{key}-->)", re.S)
        if not pattern.search(text):
            raise SystemExit(f"目印 chrome:{key} が無い: {lang}/{page}")
        text = pattern.sub(lambda m: f"{m.group(1)}\n{fn(lang, page)}\n{m.group(2)}", text)
    # 法務ページの更新日
    text = re.sub(r'(<div class="meta" data-updated="(\d{4}-\d{2}-\d{2})">).*?(</div>)',
                  lambda m: f"{m.group(1)}{date_text(lang, m.group(2))}{m.group(3)}", text, flags=re.S)
    # <html lang> も合わせる
    text = re.sub(r'<html lang="[^"]*">', f'<html lang="{lang}">', text, count=1)
    return text


def main() -> int:
    check = "--check" in sys.argv
    stale, missing = [], []
    for lang, cfg in LANGS.items():
        for page in PAGES:
            path = (ROOT / cfg["dir"] / page) if cfg["dir"] else (ROOT / page)
            if not path.exists():
                missing.append(str(path.relative_to(ROOT)))
                continue
            before = path.read_text(encoding="utf-8")
            after = apply(before, lang, page)
            if before != after:
                stale.append(str(path.relative_to(ROOT)))
                if not check:
                    path.write_text(after, encoding="utf-8")

    for name in missing:
        print(f"無い: {name}")
    for name in stale:
        print(("ずれ: " if check else "直した: ") + name)
    if check and (stale or missing):
        return 1
    if missing:
        return 1
    if not stale:
        print("共通部分は全ページ一致")
    return 0


if __name__ == "__main__":
    sys.exit(main())
