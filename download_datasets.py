# download_datasets.py

import os
import requests
import gzip
import shutil
from tqdm.auto import tqdm

# --- 要下载的数据集URL列表 ---
DATASET_URLS = [
    "https://snap.stanford.edu/data/bigdata/communities/com-dblp.ungraph.txt.gz",
    "https://snap.stanford.edu/data/bigdata/communities/com-lj.ungraph.txt.gz",
    "https://snap.stanford.edu/data/bigdata/communities/com-orkut.ungraph.txt.gz",
    "https://snap.stanford.edu/data/bigdata/communities/com-friendster.ungraph.txt.gz",
    "https://snap.stanford.edu/data/cit-Patents.txt.gz",
    "https://snap.stanford.edu/data/twitter-2010.txt.gz",
]

def download_and_extract(url: str):
    """
    从给定的URL下载文件，主要功能包括：
    - 检查最终文件是否存在，如果存在则跳过。
    - 支持断点续传。
    - 显示下载和解压的进度条。
    - 成功解压后自动删除.gz压缩包。
    """
    # 1. 从URL派生文件名
    gz_filename = os.path.basename(url)
    txt_filename = gz_filename[:-3]  # 移除.gz后缀

    # --- 检查1: 如果最终解压文件已存在，则完全跳过 ---
    if os.path.exists(txt_filename):
        print(f"✅ '{txt_filename}' 已存在，跳过。")
        return

    print(f"\nProcessing: {gz_filename}")
    
    # 2. 准备下载，实现断点续传
    local_size = 0
    # 如果压缩文件已存在（但未完全下载），获取其大小
    if os.path.exists(gz_filename):
        local_size = os.path.getsize(gz_filename)

    try:
        # 使用HEAD请求预先获取文件总大小，避免下载
        head_response = requests.head(url, allow_redirects=True, timeout=10)
        head_response.raise_for_status()
        total_size = int(head_response.headers.get('content-length', 0))

        # --- 检查2: 如果压缩文件已完整下载，则跳过下载步骤 ---
        if local_size >= total_size > 0:
            print(f"📦 '{gz_filename}' 已完整下载，准备解压。")
        else:
            # 3. 执行下载
            print(f"Downloading '{gz_filename}'...")
            # 设置HTTP头，请求从上次中断的位置开始下载
            headers = {'Range': f'bytes={local_size}-'}
            
            with requests.get(url, stream=True, headers=headers, timeout=30) as r:
                # 如果服务器不支持断点续传(返回200)，则从头开始下载
                mode = 'ab' if r.status_code == 206 else 'wb'
                if mode == 'ab':
                    print(f"Resuming download from {local_size / 1024**2:.2f} MB...")
                
                r.raise_for_status()
                
                with open(gz_filename, mode) as f, tqdm(
                    desc=gz_filename,
                    initial=local_size,
                    total=total_size,
                    unit='B',
                    unit_scale=True,
                    unit_divisor=1024,
                ) as pbar:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                        pbar.update(len(chunk))

    except requests.exceptions.RequestException as e:
        print(f"❌ 下载 '{url}' 时出错: {e}")
        return

    # 4. 解压文件
    print(f"Decompressing '{gz_filename}'...")
    try:
        # 获取压缩文件的大小，用于解压进度条
        compressed_size = os.path.getsize(gz_filename)
        with gzip.open(gz_filename, 'rb') as f_in:
            with open(txt_filename, 'wb') as f_out, tqdm(
                desc=f"Extracting",
                total=compressed_size,
                unit='B',
                unit_scale=True,
                unit_divisor=1024,
            ) as pbar:
                # 为了在复制时更新进度条，我们分块读取和写入
                while True:
                    chunk = f_in.read(8192)
                    if not chunk:
                        break
                    f_out.write(chunk)
                    pbar.update(len(chunk))

        # 5. 清理下载的压缩包
        print(f"✅ 解压成功. 删除 '{gz_filename}'.")
        os.remove(gz_filename)

    except (gzip.BadGzipFile, EOFError) as e:
        print(f"❌ 解压 '{gz_filename}' 出错: {e}. 文件可能不完整，请重新运行脚本。")
    except Exception as e:
        print(f"❌ 解压过程中发生未知错误: {e}")


def main():
    """
    脚本主函数，遍历所有URL并执行下载解压任务。
    """
    print("--- 开始下载并处理SNAP数据集 ---")
    for url in DATASET_URLS:
        download_and_extract(url)
    print("\n--- 所有任务已完成 ---")


if __name__ == "__main__":
    main()