#!/usr/bin/env python3
"""
Download and convert Yelp Open Dataset to CSV format.
Generates two files: nodes.csv (with features) and edges.csv
"""

import os
import sys
import urllib.request
import zipfile
import tarfile
import csv
import ujson as json

YELP_DATASET_URL = "https://business.yelp.com/external-assets/files/Yelp-JSON.zip"

def download_dataset(output_dir="."):
    """Download Yelp dataset if not already present."""
    zip_file = os.path.join(output_dir, "Yelp-JSON.zip")
    if os.path.exists(zip_file):
        print(f"Dataset archive already exists: {zip_file}")
        return zip_file

    print(f"Downloading Yelp dataset from {YELP_DATASET_URL}...")
    print("This may take a while (file size ~10GB)...")
    try:
        from tqdm import tqdm
        req = urllib.request.Request(YELP_DATASET_URL, headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })
        with urllib.request.urlopen(req) as response, open(zip_file, 'wb') as out:
            total = int(response.headers.get('Content-Length', 0))
            with tqdm(total=total, unit='B', unit_scale=True, desc="Downloading") as pbar:
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    out.write(chunk)
                    pbar.update(len(chunk))
        print(f"✓ Downloaded to {zip_file}")
        return zip_file
    except Exception as e:
        print(f"Error downloading dataset: {e}", file=sys.stderr)
        sys.exit(1)

def extract_dataset(zip_file, output_dir="."):
    """Extract Yelp dataset from zip file."""
    required_files = [
        "yelp_academic_dataset_business.json",
        "yelp_academic_dataset_review.json",
        "yelp_academic_dataset_user.json"
    ]
    if all(os.path.exists(os.path.join(output_dir, f)) for f in required_files):
        print("Dataset files already extracted")
        return True

    print(f"Extracting {zip_file}...")
    try:
        # Step 1: Extract zip to get the tar file
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(output_dir)

        # Step 2: Extract the tar file inside "Yelp JSON/" subdirectory
        tar_path = os.path.join(output_dir, "Yelp JSON", "yelp_dataset.tar")
        if os.path.exists(tar_path):
            print(f"Extracting {tar_path}...")
            with tarfile.open(tar_path, 'r') as tar_ref:
                tar_ref.extractall(output_dir)

        print("✓ Extraction complete")
        return True
    except Exception as e:
        print(f"Error extracting dataset: {e}", file=sys.stderr)
        sys.exit(1)

def convert_to_csv(output_dir="."):
    """Convert Yelp JSON files to CSV format with memory & speed optimization."""
    try:
        from tqdm import tqdm
    except ImportError:
        tqdm = lambda iterable, **kwargs: iterable

    print("Processing Yelp dataset...")

    business_file = os.path.join(output_dir, "yelp_academic_dataset_business.json")
    user_file = os.path.join(output_dir, "yelp_academic_dataset_user.json")
    review_file = os.path.join(output_dir, "yelp_academic_dataset_review.json")

    # Map original string IDs to contiguous 0-based integer IDs
    id_map = {}
    next_id = 0

    nodes_file = os.path.join(output_dir, "nodes.csv")
    print(f"Writing nodes and labels to {nodes_file}...")

    with open(nodes_file, 'w', newline='', encoding='utf-8') as f_nodes:
        writer = csv.writer(f_nodes)
        writer.writerow(["node_id", "type", "stars", "review_count"])

        # Process businesses
        print("Processing businesses...")
        business_count = 0
        with open(business_file, 'r', encoding='utf-8') as f:
            for line in tqdm(f, desc="Reading businesses", unit="lines"):
                obj = json.loads(line)
                b_id = obj['business_id']
                id_map[b_id] = next_id
                writer.writerow([next_id, "business", obj.get('stars', ''), obj.get('review_count', '')])
                next_id += 1
                business_count += 1

        # Process users
        print("Processing users...")
        user_count = 0
        with open(user_file, 'r', encoding='utf-8') as f:
            for line in tqdm(f, desc="Reading users", unit="lines"):
                obj = json.loads(line)
                u_id = obj['user_id']
                id_map[u_id] = next_id
                writer.writerow([next_id, "user", obj.get('average_stars', ''), obj.get('review_count', '')])
                next_id += 1
                user_count += 1

    edges_file = os.path.join(output_dir, "edges.csv")
    print(f"Writing edges to {edges_file}...")
    edge_count = 0

    # Optimization: Chunked writing to balance memory and disk I/O
    BATCH_SIZE = 100000
    batch = []

    with open(edges_file, 'w', newline='') as f_edges:
        writer = csv.writer(f_edges)
        writer.writerow(["src", "dst", "stars", "date", "useful", "funny", "cool"])

        with open(review_file, 'r', encoding='utf-8') as rf:
            for line in tqdm(rf, desc="Writing edges", unit="reviews"):
                review = json.loads(line)
                u_id = review['user_id']
                b_id = review['business_id']

                if u_id in id_map and b_id in id_map:
                    batch.append([
                        id_map[u_id], id_map[b_id],
                        review.get('stars', ''),
                        review.get('date', ''),
                        review.get('useful', ''),
                        review.get('funny', ''),
                        review.get('cool', ''),
                    ])
                    edge_count += 1

                    # Execute disk write when batch size is reached
                    if len(batch) >= BATCH_SIZE:
                        writer.writerows(batch)
                        batch.clear()  # Clear list to release memory

            # Write any remaining edges
            if batch:
                writer.writerows(batch)

    print(f"✓ Dataset converted successfully")
    print(f"  Businesses: {business_count:,}")
    print(f"  Users: {user_count:,}")
    print(f"  Total nodes: {business_count + user_count:,}")
    print(f"  Reviews (edges): {edge_count:,}")

if __name__ == "__main__":
    output_dir = "."
    zip_file = download_dataset(output_dir)
    extract_dataset(zip_file, output_dir)
    convert_to_csv(output_dir)