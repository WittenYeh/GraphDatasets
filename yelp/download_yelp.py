#!/usr/bin/env python3
"""
Download and convert Yelp Open Dataset to CSV format.
Generates two files: nodes.csv and edges.csv

The Yelp Open Dataset contains:
- Businesses (nodes)
- Users (nodes)
- Reviews (edges: user -> business)

Dataset must be downloaded manually from:
https://www.yelp.com/dataset/download
"""

import json
import os
import sys

def check_dataset_files(output_dir="."):
    """Check if Yelp dataset files exist."""

    required_files = [
        "yelp_academic_dataset_business.json",
        "yelp_academic_dataset_review.json",
        "yelp_academic_dataset_user.json"
    ]

    missing_files = [f for f in required_files if not os.path.exists(os.path.join(output_dir, f))]

    if missing_files:
        print("=" * 70)
        print("Yelp Open Dataset - Manual Download Required")
        print("=" * 70)
        print()
        print("Please download the Yelp Open Dataset manually:")
        print()
        print("1. Visit: https://www.yelp.com/dataset/download")
        print("2. Sign up and agree to the terms")
        print("3. Download the dataset (tar file)")
        print("4. Extract the tar file to this directory")
        print("5. Run 'make' again")
        print()
        print("Expected files:")
        for f in required_files:
            print(f"  - {f}")
        print()
        print(f"Missing: {', '.join(missing_files)}")
        print("=" * 70)
        sys.exit(1)

    return True

def convert_to_csv(output_dir="."):
    """Convert Yelp JSON files to CSV format."""

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
        for line in f:
            business = json.loads(line)
            business_ids[business['business_id']] = node_counter
            node_counter += 1

    # Process users
    print("Processing users...")
    with open(user_file, 'r', encoding='utf-8') as f:
        for line in f:
            user = json.loads(line)
            user_ids[user['user_id']] = node_counter
            node_counter += 1

    # Write nodes.csv
    nodes_file = os.path.join(output_dir, "nodes.csv")
    print(f"Writing nodes to {nodes_file}...")
    with open(nodes_file, 'w') as f:
        f.write("node_id,type\n")
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

    # Check if dataset files exist
    check_dataset_files(output_dir)

    # Convert to CSV
    convert_to_csv(output_dir)
