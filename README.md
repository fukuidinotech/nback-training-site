<p align="center">
  <img src="images/app-icon.png" width="120" alt="N-Back Brain Trainer アイコン">
</p>

<h1 align="center">N-Back Brain Trainer</h1>

<p align="center">
  A daily working-memory training iOS app based on the N-Back task used in cognitive psychology research.<br>
  認知心理学のN-Backタスクに毎日取り組める、ワーキングメモリ訓練 iOS アプリです。
</p>

<p align="center">
  <a href="https://apps.apple.com/jp/app/n-back-brain-trainer/id6761675343">
    <img src="https://toolbox.marketingtools.apple.com/api/badges/download-on-the-app-store/black/ja-jp?size=250x83" alt="App Store からダウンロード" height="44">
  </a>
</p>

<p align="center">
  <a href="https://fukuidinotech.github.io/nback-training-site/">https://fukuidinotech.github.io/nback-training-site/</a>
</p>

## 構成

**13言語。ja は repo 直下、ほかは同名のサブディレクトリ。**
公開済みの `…/nback-training-site/` を動かさないため、ja だけディレクトリを持ちません。

```
nback-training-site/
├── index.html privacy.html terms.html disclaimer.html   ← ja
├── en/ zh-Hans/ zh-Hant/ ko/ de/ fr/ es/ pt/ it/ ru/ pl/ nl/   ← 各4ページ（同じファイル名）
├── style.css  images/                                   ← 全言語で共有（1つだけ置く）
└── tools/i18n.py                                        ← 共通部分の正本
```

2026-09-20 に「JS で辞書を差し替える1 URL」からこの形へ移しました。
言語別の URL があると、App Store の `marketing_url` をロケール別に出せて、
`hreflang` で検索エンジンにも言語別のページとして拾ってもらえます。
**ページに JS は1行も置きません。**

### 共通部分は手で書かない

各ページの `<head>` の alternate、ヘッダー（ナビ・言語切替）、フッター、
法務ページの更新日は **`tools/i18n.py` が生成します。** 目印のあいだは上書きされます。

```
<!--chrome:alt-->  …  <!--/chrome:alt-->    canonical / hreflang / フォント / css
<!--chrome:head--> …  <!--/chrome:head-->   サイトヘッダーと言語切替
<!--chrome:foot--> …  <!--/chrome:foot-->   サイトフッター
```

```
python3 tools/i18n.py           # 全ページに書き戻す
python3 tools/i18n.py --check   # ずれていたら異常終了
```

手で書くのは `<title>` と `<meta name="description">`、そして本文だけです。
更新日は `<div class="meta" data-updated="YYYY-MM-DD">` の日付だけ直せば、
13言語ぶんの書き方（`2026年9月4日` / `September 4, 2026` / `4. September 2026` …）が揃います。

**言語を足す／減らすときは3か所を同時に直します。**
`tools/i18n.py` の `LANGS`、アプリの `NBackApp/App/SiteLinks.swift`、
`fastlane/metadata/<locale>/marketing_url.txt`（と `support_url.txt`）。

### 文章の正本は日本語

本文を変えるときは **日本語（repo 直下の4ページ）を直してから、12言語へ反映**します。
法務3ページの翻訳には「本翻訳は参考用であり、相違がある場合は日本語版が優先する」旨の
注記（`.i18n-note`）を各言語で入れてあります。
