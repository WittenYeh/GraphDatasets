#!/usr/bin/env python3
"""
Convert Matrix Market (MTX) format to CSV format.
Generates two files: nodes.csv and edges.csv
"""

import sys
import os

def parse_mtx_to_csv(mtx_file, output_dir="."):
    """
    Parse MTX file and convert to nodes.csv and edges.csv.

    MTX format:
    - Lines starting with % are comments
    - First non-comment line: rows cols entries
    - Following lines: row col [value]
    """

    try:
        from tqdm import tqdm
        has_tqdm = True
    except ImportError:
        has_tqdm = False
        print("Note: Install tqdm for progress bars (pip install tqdm)")

    if not os.path.exists(mtx_file):
        print(f"Error: File {mtx_file} not found", file=sys.stderr)
        sys.exit(1)

    print(f"Parsing {mtx_file}...")

    nodes = set()
    edges = []

    with open(mtx_file, 'r') as f:
        # Skip comments
        for line in f:
            line = line.strip()
            if not line.startswith('%'):
                # First non-comment line: rows cols entries
                parts = line.split()
                num_rows = int(parts[0])
                num_cols = int(parts[1])
                num_entries = int(parts[2])
                print(f"  Matrix size: {num_rows} x {num_cols}, entries: {num_entries}")
                break

        # Read edges
        if has_tqdm:
            for line in tqdm(f, total=num_entries, desc="Reading edges", unit="edges"):
                line = line.strip()
                if not line or line.startswith('%'):
                    continue

                parts = line.split()
                if len(parts) >= 2:
                    # MTX format is 1-indexed, convert to 0-indexed
                    src = int(parts[0]) - 1
                    dst = int(parts[1]) - 1

                    nodes.add(src)
                    nodes.add(dst)
                    edges.append((src, dst))
        else:
            for line in f:
                line = line.strip()
                if not line or line.startswith('%'):
                    continue

                parts = line.split()
                if len(parts) >= 2:
                    # MTX format is 1-indexed, convert to 0-indexed
                    src = int(parts[0]) - 1
                    dst = int(parts[1]) - 1

                    nodes.add(src)
                    nodes.add(dst)
                    edges.append((src, dst))

    # Write nodes.csv
    nodes_file = os.path.join(output_dir, "nodes.csv")
    print(f"Writing nodes to {nodes_file}...")
    sorted_nodes = sorted(nodes)
    with open(nodes_file, 'w') as f:
        f.write("node_id\n")
        if has_tqdm:
            for node in tqdm(sorted_nodes, desc="Writing nodes", unit="nodes"):
                f.write(f"{node}\n")
        else:
            for node in sorted_nodes:
                f.write(f"{node}\n")

    # Write edges.csv
    edges_file = os.path.join(output_dir, "edges.csv")
    print(f"Writing edges to {edges_file}...")
    with open(edges_file, 'w') as f:
        f.write("src,dst\n")
        if has_tqdm:
            for src, dst in tqdm(edges, desc="Writing edges", unit="edges"):
                f.write(f"{src},{dst}\n")
        else:
            for src, dst in edges:
                f.write(f"{src},{dst}\n")

    print(f"✓ Conversion complete")
    print(f"  Nodes: {len(nodes):,}")
    print(f"  Edges: {len(edges):,}")
    print(f"  Output files:")
    print(f"    - {nodes_file}")
    print(f"    - {edges_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 mtx2csv.py <mtx_file>")
        sys.exit(1)

    mtx_file = sys.argv[1]
    output_dir = os.path.dirname(mtx_file) if os.path.dirname(mtx_file) else "."

    parse_mtx_to_csv(mtx_file, output_dir)
