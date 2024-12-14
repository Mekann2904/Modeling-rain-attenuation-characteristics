import os
import pandas as pd
from datetime import datetime, time
from concurrent.futures import ProcessPoolExecutor

# Pandasの出力設定を変更（省略せず全て表示）
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.expand_frame_repr', False)

# path.txt からファイルパスを取得
with open("path.txt", 'r') as file:
    file_paths = [line.strip() for line in file.readlines()]

# 時間範囲を生成
def generate_time_ranges(start, end, interval_seconds=10):
    times = pd.date_range(start=start, end=end, freq=f'{interval_seconds}s').time
    return list(times)

# 時間範囲でデータをフィルタリングする関数
def filter_by_time_range(df, start_time):
    end_time = (datetime.combine(datetime.today(), start_time) + pd.Timedelta(seconds=10)).time()
    return df[(df['time'] >= start_time) & (df['time'] < end_time)]

# ファイルを処理するメイン関数
def process_file(file_path):
    try:
        # ファイルを DataFrame として読み込み
        header = pd.read_csv(file_path, skiprows=1, nrows=0).columns.str.strip()
        df = pd.read_csv(file_path, skiprows=2, names=header)

        # 列名の前後の空白を削除
        df.columns = df.columns.str.strip()

        # 列名のマッピング
        possible_columns = ["MX_RX_LEVEL", "1803_RX_LEVEL"]
        time_column = "time"
        target_column = None

        if time_column not in df.columns:
            raise ValueError(f"'time' column not found in {file_path}")

        for col in possible_columns:
            if col in df.columns:
                target_column = col
                break

        if target_column is None:
            raise ValueError(f"No valid RX_LEVEL column found in {file_path}. Available columns: {df.columns}")

        # 必要な列を抽出
        df = df[[time_column, target_column]].rename(columns={target_column: "MX_RX_LEVEL"})

        # データ型変換
        df['time'] = pd.to_datetime(df['time'], format='%H:%M:%S').dt.time
        df['MX_RX_LEVEL'] = pd.to_numeric(df['MX_RX_LEVEL'], errors='coerce')

        # 10秒ごとの時間範囲を生成
        time_ranges = generate_time_ranges("00:00:00", "23:59:59")

        # 各範囲でデータを取得し、計算
        results = []
        for start in time_ranges:
            range_data = filter_by_time_range(df, start)
            if not range_data.empty:
                count = range_data['MX_RX_LEVEL'].count()
                if count == 5:
                    out_value = range_data['MX_RX_LEVEL'].sum()
                else:
                    out_value = range_data['MX_RX_LEVEL'].mean() * 5
                results.append({
                    "time": start.strftime('%H:%M:%S'),  # 時間を文字列に変換
                    "MX_RX_LEVEL": out_value
                })

        # DataFrameに変換して保存
        result_df = pd.DataFrame(results)
        output_file_name = os.path.splitext(os.path.basename(file_path))[0] + "_output.txt"
        output_file_path = os.path.join(os.path.dirname(file_path), output_file_name)
        result_df.to_csv(output_file_path, index=False, header=True)
        print(f"Results saved to {output_file_path}")

    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
        return file_path, str(e)
    return None

# 全ファイルを並列処理
def main():
    error_log = []
    with ProcessPoolExecutor() as executor:
        results = executor.map(process_file, file_paths)

    # エラーログの記録
    for result in results:
        if result:
            error_log.append(result)

    if error_log:
        with open('error_log.txt', 'w') as log_file:
            for file_path, error_message in error_log:
                log_file.write(f"{file_path}: {error_message}\n")
        print("Errors logged to error_log.txt")

if __name__ == "__main__":
    main()

