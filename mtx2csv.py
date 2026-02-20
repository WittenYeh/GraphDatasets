#!/usr/bin/env python3
"""
Convert Matrix Market (MTX) format to CSV format.
Generates two files: nodes.csv and edges.csv

Uses fast_matrix_market for fast parallel MTX reading,
and process_map for parallel CSV writing.
"""

import sys
import os
import csv
import numpy as np
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map

import fast_matrix_market as fmm

NUM_WORKERS = 8
WRITE_CHUNK = 500_000  # rows per chunk for parallel CSV writing


def _write_edges_chunk(args):
    """Write a chunk of edges to a temp file, return the temp file path."""
    edges_file, chunk_idx, src_chunk, dst_chunk = args
    tmp_path = f"{edges_file}.part{chunk_idx}"
    with open(tmp_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(zip(src_chunk.tolist(), dst_chunk.tolist()))
    return tmp_path


def parse_mtx_to_csv(mtx_file, output_dir="."):
    if not os.path.exists(mtx_file):
        print(f"Error: File {mtx_file} not found", file=sys.stderr)
        sys.exit(1)

    print(f"Reading {mtx_file}...")
    (_, (rows, cols)), shape = fmm.read_coo(mtx_file, parallelism=NUM_WORKERS)
    print(f"  Matrix shape: {shape[0]} x {shape[1]}, entries: {len(rows):,}")

    # Build contiguous 0-based ID mapping from 1-indexed MTX IDs
    unique_ids = np.unique(np.concatenate([rows, cols]))
    id_map = np.empty(int(unique_ids.max()) + 1, dtype=np.int64)
    id_map[unique_ids] = np.arange(len(unique_ids), dtype=np.int64)
    num_nodes = len(unique_ids)

    nodes_file = os.path.join(output_dir, "nodes.csv")
    print(f"Writing nodes to {nodes_file}...")
    with open(nodes_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["node_id"])
        writer.writerows(
            tqdm(([i] for i in range(num_nodes)), total=num_nodes, desc="Writing nodes", unit="nodes")
        )

    # Remap edge IDs
    src_mapped = id_map[rows]
    dst_mapped = id_map[cols]

    # Split into chunks for parallel writing
    num_edges = len(src_mapped)
    chunk_args = []
    edges_file = os.path.join(output_dir, "edges.csv")
    for i, start in enumerate(range(0, num_edges, WRITE_CHUNK)):
        end = min(start + WRITE_CHUNK, num_edges)
        chunk_args.append((edges_file, i, src_mapped[start:end], dst_mapped[start:end]))

    print(f"Writing edges to {edges_file}...")
    tmp_files = process_map(
        _write_edges_chunk, chunk_args,
        max_workers=NUM_WORKERS, desc="Writing edges", unit="chunks"
    )

    # Concatenate temp files into final edges.csv
    with open(edges_file, 'w', newline='') as f_out:
        f_out.write("src,dst\n")
        for tmp_path in tmp_files:
            with open(tmp_path, 'r') as f_in:
                f_out.write(f_in.read())
            os.remove(tmp_path)

    print(f"Conversion complete")
    print(f"  Nodes: {num_nodes:,}")
    print(f"  Edges: {num_edges:,}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 mtx2csv.py <mtx_file>")
        sys.exit(1)

    mtx_path = sys.argv[1]
    out_dir = os.path.dirname(mtx_path) or "."
    parse_mtx_to_csv(mtx_path, out_dir)
