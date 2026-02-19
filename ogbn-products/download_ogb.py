#!/usr/bin/env python3
"""
Download OGB dataset using official loader and convert to CSV format.
Generates two files: nodes.csv (with labels) and edges.csv
"""

import os
import sys
import csv

# Monkey patch input to auto-confirm downloads
original_input = input
def auto_confirm_input(prompt):
    if "Will you proceed?" in prompt:
        print(prompt + "y (auto-confirmed)")
        return "y"
    return original_input(prompt)

import builtins
builtins.input = auto_confirm_input

def download_and_convert(dataset_name="ogbn-products", output_dir="."):
    """Download OGB dataset using official loader and convert to CSV format."""
    try:
        from ogb.nodeproppred import NodePropPredDataset
    except ImportError:
        print("Error: ogb library not found. Install with: pip install ogb", file=sys.stderr)
        sys.exit(1)

    try:
        from tqdm import tqdm
    except ImportError:
        tqdm = lambda iterable, **kwargs: iterable
        print("Note: Install tqdm for progress bars (pip install tqdm)")

    print(f"Downloading {dataset_name} using OGB official loader...")
    dataset = NodePropPredDataset(name=dataset_name, root=output_dir)

    print("Processing graph data...")
    # Optimization 1: Extract both graph and labels simultaneously
    graph, labels = dataset[0]
    edge_index = graph['edge_index']
    num_nodes = graph['num_nodes']

    # Flatten labels (OGB labels typically have shape [num_nodes, 1])
    if len(labels.shape) == 2 and labels.shape[1] == 1:
        labels = labels.flatten()

    # Generate nodes.csv
    nodes_file = os.path.join(output_dir, "nodes.csv")
    print(f"Writing nodes and labels to {nodes_file}...")
    with open(nodes_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["node_id", "label"])  # Add label header

        # Optimization 2: Use zip and writerows for fast batch writing, eliminating for-loop overhead
        node_data = zip(range(num_nodes), labels)
        writer.writerows(tqdm(node_data, total=num_nodes, desc="Writing nodes", unit="nodes"))

    # Generate edges.csv
    edges_file = os.path.join(output_dir, "edges.csv")
    print(f"Writing edges to {edges_file}...")
    with open(edges_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["src", "dst"])

        # Optimization 3: Transpose the edge matrix directly from (2, num_edges) to (num_edges, 2), then batch write
        edges_t = edge_index.T
        writer.writerows(tqdm(edges_t, total=edges_t.shape[0], desc="Writing edges", unit="edges"))

    print(f"✓ Dataset downloaded and converted")
    print(f"  Nodes: {num_nodes:,}")
    print(f"  Edges: {edge_index.shape[1]:,}")
    print(f"  Output files:\n    - {nodes_file}\n    - {edges_file}")

if __name__ == "__main__":
    download_and_convert()