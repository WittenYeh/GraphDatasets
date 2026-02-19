#!/usr/bin/env python3
"""
Download OGB dataset using official loader and convert to CSV format.
Generates two files: nodes.csv and edges.csv
"""

import os
import sys

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

    print(f"Downloading {dataset_name} using OGB official loader...")
    dataset = NodePropPredDataset(name=dataset_name, root=output_dir)

    print("Processing graph data...")
    graph, labels = dataset[0]
    edge_index = graph['edge_index']
    num_nodes = graph['num_nodes']

    # Generate nodes.csv
    nodes_file = os.path.join(output_dir, "nodes.csv")
    print(f"Writing nodes to {nodes_file}...")
    with open(nodes_file, 'w') as f:
        f.write("node_id\n")
        for i in range(num_nodes):
            f.write(f"{i}\n")

    # Generate edges.csv
    edges_file = os.path.join(output_dir, "edges.csv")
    print(f"Writing edges to {edges_file}...")
    with open(edges_file, 'w') as f:
        f.write("src,dst\n")
        for i in range(edge_index.shape[1]):
            src = edge_index[0][i]
            dst = edge_index[1][i]
            f.write(f"{src},{dst}\n")

    print(f"✓ Dataset downloaded and converted")
    print(f"  Nodes: {num_nodes:,}")
    print(f"  Edges: {edge_index.shape[1]:,}")
    print(f"  Output files:")
    print(f"    - {nodes_file}")
    print(f"    - {edges_file}")

if __name__ == "__main__":
    download_and_convert()
