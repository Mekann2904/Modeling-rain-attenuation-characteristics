# Modeling-rain-attenuation-characteristics

# 降雨減衰特性のモデリング(1)

課題 1: データをダウンロードし、ファイルの中⾝を確認せよ。

課題 2: 2 秒毎に記録されている測定値を、10 秒毎のデータに作りかえよ。


## 使用方法

git cloneする。
path.pyの# 対象のディレクトリを変更する。

path.pyを実行し設定した対象のディレクトリ以下の`.log`ファイルを取得しリスト化する。実行後にpath.txtが生成される。
main.pyを実行すると自動でpath.txtを読み込まれ、結果が出力される。
terminalにはoutput_file_pathが出力される。

```
output_file_name = os.path.splitext(os.path.basename(file_path))[0] + "_output.txt"
output_file_path = os.path.join(os.path.dirname(file_path), output_file_name)
```

エラーが発生した場合は`error_log.txt`に保存される。


## 備考
~~自分の環境では全て変換するのに17分かかった。~~

コードの見直しにより変換にかかる時間が20秒程度に短縮された。

高速化って凄い ヮ(ﾟдﾟ)ォ!


