#!/usr/bin/env python3
"""
Convert Matrix Market (MTX) format to CSV format.
Generates two files: nodes.csv and edges.csv
"""

import sys
import os
import csv
from tqdm import tqdm

def parse_mtx_to_csv(mtx_file, output_dir="."):
    """
    Parse MTX file and convert to nodes.csv and edges.csv.
    """
    if not os.path.exists(mtx_file):
        print(f"Error: File {mtx_file} not found", file=sys.stderr)
        sys.exit(1)

    print(f"Parsing {mtx_file}...")

    raw_nodes = set()
    raw_edges = []

    with open(mtx_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('%'):
                num_rows, num_cols, num_entries = map(int, line.split())
                print(f"  Matrix size: {num_rows} x {num_cols}, entries: {num_entries}")
                break

        # Read edge data (keep original 1-indexed IDs for now)
        for line in tqdm(f, total=num_entries, desc="Reading edges", unit="edges"):
            parts = line.split()
            if len(parts) >= 2:
                src, dst = int(parts[0]), int(parts[1])
                raw_nodes.update((src, dst))
                raw_edges.append((src, dst))

    # Build contiguous 0-based ID mapping
    id_map = {old_id: new_id for new_id, old_id in enumerate(sorted(raw_nodes))}

    nodes_file = os.path.join(output_dir, "nodes.csv")
    print(f"Writing nodes to {nodes_file}...")
    with open(nodes_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["node_id"])
        writer.writerows([[new_id] for new_id in tqdm(range(len(id_map)), desc="Writing nodes", unit="nodes")])

    edges_file = os.path.join(output_dir, "edges.csv")
    print(f"Writing edges to {edges_file}...")
    with open(edges_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["src", "dst"])
        writer.writerows(tqdm([(id_map[s], id_map[d]) for s, d in raw_edges], desc="Writing edges", unit="edges"))

    print(f"✓ Conversion complete")
    print(f"  Nodes: {len(id_map):,}")
    print(f"  Edges: {len(raw_edges):,}")
    print(f"  Output files:\n    - {nodes_file}\n    - {edges_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 mtx2csv.py <mtx_file>")
        sys.exit(1)

    mtx_path = sys.argv[1]
    # Default to the current directory if os.path.dirname returns an empty string
    out_dir = os.path.dirname(mtx_path) or "."

    parse_mtx_to_csv(mtx_path, out_dir)