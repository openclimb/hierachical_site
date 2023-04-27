# hierachical_site

サイトの階層構造を確認できるプログラム
ドメイン名を指定することで、そのドメインかつ遷移先aタグのhrefを読み取り、それを一覧化（階層構造ディレクトリも作る）
さらに、レスポンスエラーがおきるurl
タイトルがないurlとそこに遷移しようとする遷移元url
は別ファイルで作成するようにしている

## コマンドの実行方法
```
# variables_example.pyに設定する情報をいれvariables.pyを作成しておく

$ python hierachical_site.py

# 記載してあるライブラリを入れる必要がある
$ pip install bs4
or
$ python -m pip install bs4
```
