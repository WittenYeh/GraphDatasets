#!/usr/bin/env python3
"""
Convert Matrix Market (MTX) format to CSV format.
Generates two files: nodes.csv and edges.csv

Safely handles isolated nodes and bipartite graphs using MTX header shapes.
Uses fast_matrix_market for fast parallel MTX reading,
and process_map for parallel CSV writing.
"""

import sys
import os
import csv
import shutil
import numpy as np
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map

import fast_matrix_market as fmm

NUM_WORKERS = 8
WRITE_CHUNK = 500_000  # Rows per chunk for parallel CSV writing


def _write_edges_chunk(args):
    """Write a chunk of edges to a temporary file, return the temp file path."""
    edges_file, chunk_idx, src_chunk, dst_chunk = args
    tmp_path = f"{edges_file}.part{chunk_idx}"

    # Enforce newline='\n' to prepare for safe binary concatenation later
    with open(tmp_path, 'w', newline='\n') as f:
        writer = csv.writer(f)
        writer.writerows(zip(src_chunk.tolist(), dst_chunk.tolist()))
    return tmp_path


def parse_mtx_to_csv(mtx_file, output_dir="."):
    if not os.path.exists(mtx_file):
        print(f"Error: File {mtx_file} not found", file=sys.stderr)
        sys.exit(1)

    print(f"Reading {mtx_file}...")

    # fmm returns 0-indexed rows and cols in Python by default
    (_, (rows, cols)), shape = fmm.read_coo(mtx_file, parallelism=NUM_WORKERS)
    print(f"  Matrix shape: {shape[0]} x {shape[1]}, entries: {len(rows):,}")

    num_rows, num_cols = shape[0], shape[1]

    # 1. Core Logic: Handle isolated nodes and graph structures safely based on shape
    if num_rows == num_cols:
        print("  Detected square matrix (Homogeneous Graph).")
        num_nodes = num_rows
        src_mapped = rows
        dst_mapped = cols
    else:
        print(f"  Detected non-square matrix (Bipartite Graph). Offsetting col IDs by {num_rows}.")
        # For bipartite graphs, shift column entity IDs to avoid collision with row entities
        num_nodes = num_rows + num_cols
        src_mapped = rows
        dst_mapped = cols + num_rows

    # 2. Write nodes.csv (Isolated nodes are perfectly preserved due to shape usage)
    nodes_file = os.path.join(output_dir, "nodes.csv")
    print(f"Writing nodes to {nodes_file}...")
    with open(nodes_file, 'w', newline='\n') as f:
        f.write("node_id\n")
        # Generate continuous IDs from 0 to num_nodes - 1
        # Using string formatting directly is faster than csv.writer for single columns
        for i in tqdm(range(num_nodes), desc="Writing nodes", unit="nodes"):
            f.write(f"{i}\n")

    # 3. Split edges into chunks for parallel writing
    num_edges = len(src_mapped)
    chunk_args = []
    edges_file = os.path.join(output_dir, "edges.csv")

    for i, start in enumerate(range(0, num_edges, WRITE_CHUNK)):
        end = min(start + WRITE_CHUNK, num_edges)
        # CRITICAL: Use .copy() to prevent multiprocessing from pickling the entire original array view
        chunk_args.append((edges_file, i, src_mapped[start:end].copy(), dst_mapped[start:end].copy()))

    print(f"Writing edges to {edges_file}...")
    tmp_files = process_map(
        _write_edges_chunk, chunk_args,
        max_workers=NUM_WORKERS, desc="Writing edges", unit="chunks"
    )

    # 4. Concatenate temporary files into the final edges.csv
    print("Concatenating edge chunks...")
    # Use binary mode (wb/rb) and shutil.copyfileobj for zero-overhead, memory-efficient merging
    with open(edges_file, 'wb') as f_out:
        f_out.write(b"src,dst\n")
        for tmp_path in tmp_files:
            with open(tmp_path, 'rb') as f_in:
                shutil.copyfileobj(f_in, f_out)
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