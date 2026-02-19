#!/usr/bin/env python3
"""
Download and convert Yelp Open Dataset to CSV format.
Generates two files: nodes.csv and edges.csv

The Yelp Open Dataset contains:
- Businesses (nodes)
- Users (nodes)
- Reviews (edges: user -> business)
"""

import json
import os
import sys
import urllib.request
import zipfile

YELP_DATASET_URL = "https://business.yelp.com/external-assets/files/Yelp-JSON.zip"

def download_dataset(output_dir="."):
    """Download Yelp dataset if not already present."""

    zip_file = os.path.join(output_dir, "Yelp-JSON.zip")

    # Check if already downloaded
    if os.path.exists(zip_file):
        print(f"Dataset archive already exists: {zip_file}")
        return zip_file

    print(f"Downloading Yelp dataset from {YELP_DATASET_URL}...")
    print("This may take a while (file size ~10GB)...")

    try:
        urllib.request.urlretrieve(YELP_DATASET_URL, zip_file)
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

    # Check if already extracted
    if all(os.path.exists(os.path.join(output_dir, f)) for f in required_files):
        print("Dataset files already extracted")
        return True

    print(f"Extracting {zip_file}...")
    try:
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(output_dir)
        print("✓ Extraction complete")
        return True
    except Exception as e:
        print(f"Error extracting dataset: {e}", file=sys.stderr)
        sys.exit(1)

def convert_to_csv(output_dir="."):
    """Convert Yelp JSON files to CSV format."""

    try:
        from tqdm import tqdm
        has_tqdm = True
    except ImportError:
        has_tqdm = False
        print("Note: Install tqdm for progress bars (pip install tqdm)")

    print("Processing Yelp dataset...")

    business_file = os.path.join(output_dir, "yelp_academic_dataset_business.json")
    user_file = os.path.join(output_dir, "yelp_academic_dataset_user.json")
    review_file = os.path.join(output_dir, "yelp_academic_dataset_review.json")

    # Create node ID mappings
    business_ids = {}
    user_ids = {}
    node_counter = 0

    # Process businesses
    print("Processing businesses...")
    with open(business_file, 'r', encoding='utf-8') as f:
        if has_tqdm:
            for line in tqdm(f, desc="Reading businesses", unit="lines"):
                business = json.loads(line)
                business_ids[business['business_id']] = node_counter
                node_counter += 1
        else:
            for line in f:
                business = json.loads(line)
                business_ids[business['business_id']] = node_counter
                node_counter += 1

    # Process users
    print("Processing users...")
    with open(user_file, 'r', encoding='utf-8') as f:
        if has_tqdm:
            for line in tqdm(f, desc="Reading users", unit="lines"):
                user = json.loads(line)
                user_ids[user['user_id']] = node_counter
                node_counter += 1
        else:
            for line in f:
                user = json.loads(line)
                user_ids[user['user_id']] = node_counter
                node_counter += 1

    # Write nodes.csv
    nodes_file = os.path.join(output_dir, "nodes.csv")
    print(f"Writing nodes to {nodes_file}...")
    with open(nodes_file, 'w') as f:
        f.write("node_id,type\n")
        if has_tqdm:
            for biz_id, node_id in tqdm(business_ids.items(), desc="Writing businesses", unit="nodes"):
                f.write(f"{node_id},business\n")
            for usr_id, node_id in tqdm(user_ids.items(), desc="Writing users", unit="nodes"):
                f.write(f"{node_id},user\n")
        else:
            for biz_id, node_id in business_ids.items():
                f.write(f"{node_id},business\n")
            for usr_id, node_id in user_ids.items():
                f.write(f"{node_id},user\n")

    # Process reviews and write edges.csv
    edges_file = os.path.join(output_dir, "edges.csv")
    print(f"Writing edges to {edges_file}...")
    edge_count = 0

    with open(edges_file, 'w') as f:
        f.write("src,dst\n")
        with open(review_file, 'r', encoding='utf-8') as rf:
            if has_tqdm:
                for line in tqdm(rf, desc="Writing edges", unit="reviews"):
                    review = json.loads(line)
                    user_id = review['user_id']
                    business_id = review['business_id']

                    if user_id in user_ids and business_id in business_ids:
                        src = user_ids[user_id]
                        dst = business_ids[business_id]
                        f.write(f"{src},{dst}\n")
                        edge_count += 1
            else:
                for line in rf:
                    review = json.loads(line)
                    user_id = review['user_id']
                    business_id = review['business_id']

                    if user_id in user_ids and business_id in business_ids:
                        src = user_ids[user_id]
                        dst = business_ids[business_id]
                        f.write(f"{src},{dst}\n")
                        edge_count += 1

    print(f"✓ Dataset converted successfully")
    print(f"  Businesses: {len(business_ids):,}")
    print(f"  Users: {len(user_ids):,}")
    print(f"  Total nodes: {node_counter:,}")
    print(f"  Reviews (edges): {edge_count:,}")
    print(f"  Output files:")
    print(f"    - {nodes_file}")
    print(f"    - {edges_file}")

if __name__ == "__main__":
    output_dir = "."

    # Download and extract dataset
    zip_file = download_dataset(output_dir)
    extract_dataset(zip_file, output_dir)

    # Convert to CSV
    convert_to_csv(output_dir)
