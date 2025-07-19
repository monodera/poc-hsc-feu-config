## HSC FEU Configuration ページの改定案のサンプルプロジェクト

西澤さんとのメールのやりとりをみて、FEUの情報をCSVファイルにしておいて、MkDocsではそれを単に読み込んで表として表示すれば、CSVファイルを取得してプログラマティックにどのスロットにフィルターが入っているかを取得できるのでよいのではないかと考えた。MkDocsで利用可能な `mkdocs-table-reader-plugin` というプラグインがあるので、これを利用して、CSVファイルを読み込んで表示するようにする。

### サンプル

https://www.naoj.org/staff/monodera/hsc_feu_config/

### mkdocs-table-reader-plugin のインストール

村松さんなどを通して、[mkdocs-table-reader-plugin](https://timvink.github.io/mkdocs-table-reader-plugin/) パッケージをインストールしてもらう

### mkdocs.yml の編集

```yaml
plugins:
  - table-reader
```

を追加する。

### CSVファイルの作成

`HSC_FEU_config.md` のテーブルを CSV ファイルに変換する。このリポジトリでは `docs/hsc_feu_configuration.csv` としてある。

```csv
"Date Begin","Date End",Opt-Top,Opt-Mid,Opt_Bot,IR-Top,IR-Mid,IR-Bot
2025-07-08," ",HSC-r2,NB816,EB-gri,HSC-g,HSC-z,HSC-i2
2025-04-28,2025-07-08,NB395,NB430,EB-gri,HSC-g,HSC-z,HSC-r2
2025-04-16,2025-04-28,NB656,NB816,NB872,HSC-g,HSC-z,HSC-r2
2025-02-27,2025-04-16,NB395,NB515,NB872,HSC-g,HSC-z,HSC-i2
2025-02-10,2025-02-27,HSC-r2,NB816,HSC-Y,HSC-g,HSC-z,HSC-i2
2024-12-11,2025-02-10,HSC-g,NB816,NB926,NB872,HSC-z,HSC-r2
2024-11-15,2024-12-11,EB-gri,NB515,NB527,HSC-g,HSC-i2,HSC-r2
2024-09-18,2024-11-15,NB395,NB515,HSC-g,HSC-z,HSC-i2,HSC-r2
2024-07-22,2024-09-18," N/A",EB-gri,HSC-z,HSC-g,HSC-i2,HSC-r2
```

### MkDocs用のMarkdownファイルの編集

```markdown
{{ read_csv('hsc_feu_configuration.csv') }}%
```

とするだけでよい。

#### 注意点
- `Date Begin` および `Date End` で、空欄のところは、`" "` としておく。 なにも記載しないと `nan` と表示される。
- `"N/A"` という文字列はCSVファイルを読み込むときに `nan` として扱われるので、`" N/A"` などとしておく。


### 日付からフィルターセットを取得する

```console
# python3 ./scripts/fetch_hsc_feu_config.py 2025-07-08
# or
$ uv run scripts/fetch_hsc_feu_config.py 2025-07-08
Fetching configuration for date: 2025-07-08
From URL: https://www.naoj.org/staff/monodera/hsc_feu_config/hsc_feu_configuration.csv

Successfully fetched 99 configuration entries.

HSC FEU Configuration:
==============================
Date Begin  : 2025-07-08
Date End    : N/A
Opt-Top     : HSC-r2
Opt-Mid     : NB816
Opt_Bot     : EB-gri
IR-Top      : HSC-g
IR-Mid      : HSC-z
IR-Bot      : HSC-i2
```