import os
import pandas as pd
import numpy as np
from datetime import datetime, time
from concurrent.futures import ProcessPoolExecutor
from numba import njit

# Pandasの出力設定を変更（省略せず全て表示）
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.expand_frame_repr', False)

# path.txt からファイルパスを取得
with open("path.txt", 'r') as file:
    file_paths = [line.strip() for line in file.readlines()]

# 時間を秒に変換（Numba対応）
@njit
def time_to_seconds_numba(h, m, s):
    return h * 3600 + m * 60 + s

# 秒を時間に変換（Numba対応）
@njit
def seconds_to_time_numba(seconds):
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return h, m, s

# 時間範囲を生成
@njit
def generate_time_ranges_seconds(start_sec, end_sec, interval_seconds=10):
    return np.arange(start_sec, end_sec + 1, interval_seconds)

# 時間範囲でデータをフィルタリングし平均値を計算（Numba最適化）
@njit
def calculate_means(times, values, time_ranges):
    results = np.zeros(len(time_ranges) - 1, dtype=np.float64)
    for i in range(len(time_ranges) - 1):
        start = time_ranges[i]
        end = time_ranges[i + 1]
        mask = (times >= start) & (times < end)
        filtered_values = values[mask]
        if len(filtered_values) > 0:
            results[i] = filtered_values.mean()
        else:
            results[i] = 0.0  # データが存在しない場合は0
    return results

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

        # NumPy配列に変換
        times = np.array([time_to_seconds_numba(t.hour, t.minute, t.second) for t in df['time']])
        values = df['MX_RX_LEVEL'].to_numpy()

        # 時間範囲を秒単位で生成
        start_sec = time_to_seconds_numba(0, 0, 0)
        end_sec = time_to_seconds_numba(23, 59, 59)
        time_ranges = generate_time_ranges_seconds(start_sec, end_sec)

        # 平均値を計算
        results = calculate_means(times, values, time_ranges)

        # 結果をDataFrameに変換
        result_times = [seconds_to_time_numba(s) for s in time_ranges[:-1]]
        result_df = pd.DataFrame({
            "time": [f"{h:02}:{m:02}:{s:02}" for h, m, s in result_times],
            "MX_RX_LEVEL": results
        })

        # 結果を保存
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

