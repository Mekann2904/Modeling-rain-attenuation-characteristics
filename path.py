import os

def save_log_file_paths(directory, output_file):
    """ディレクトリ以下のすべての.logファイルのパスを探索して保存"""
    log_file_paths = []  # ログファイルのパスを格納

    for pathname, _, filenames in os.walk(directory):
        for filename in filenames:
            # .logファイルのみ対象
            if filename.endswith('.log'):
                log_file_paths.append(os.path.join(pathname, filename))
    
    # 結果を1.txtに保存
    with open(output_file, 'w') as f:
        for path in log_file_paths:
            f.write(path + '\n')
    
    print(f"Found {len(log_file_paths)} .log files. Paths saved to {output_file}")

# 実行
if __name__ == "__main__":
    directory_path = "/Users/mekann/github/tino4/Modeling-rain-attenuation-characteristics/RxData"  # 対象のディレクトリ
    output_file = "path.txt"  # 保存先のファイル
    save_log_file_paths(directory_path, output_file)
