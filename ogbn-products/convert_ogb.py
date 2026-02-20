#!/usr/bin/env python3
"""
Convert OGB ogbn-products dataset to CSV format.
Expects the dataset to be already downloaded in the current directory.
Generates two files: nodes.csv (with labels) and edges.csv
"""

import os
import sys
import csv

try:
    from ogb.nodeproppred import NodePropPredDataset
except ImportError:
    print("Error: ogb library not found. Install with: pip install ogb", file=sys.stderr)
    sys.exit(1)

try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iterable, **kwargs):
        return iterable
    print("Note: Install tqdm for progress bars (pip install tqdm)")


def convert_to_csv(dataset_name="ogbn-products", output_dir="."):
    print(f"Loading {dataset_name} dataset...")
    dataset = NodePropPredDataset(name=dataset_name, root=output_dir)

    graph, labels = dataset[0]
    edge_index = graph['edge_index']
    num_nodes = graph['num_nodes']

    if len(labels.shape) == 2 and labels.shape[1] == 1:
        labels = labels.flatten()

    nodes_file = os.path.join(output_dir, "nodes.csv")
    print(f"Writing nodes to {nodes_file}...")
    with open(nodes_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["node_id", "label"])
        node_data = zip(range(num_nodes), labels)
        writer.writerows(tqdm(node_data, total=num_nodes, desc="Writing nodes", unit="nodes"))

    edges_file = os.path.join(output_dir, "edges.csv")
    print(f"Writing edges to {edges_file}...")
    with open(edges_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["src", "dst"])
        edges_t = edge_index.T
        writer.writerows(tqdm(edges_t, total=edges_t.shape[0], desc="Writing edges", unit="edges"))

    print(f"Dataset converted successfully")
    print(f"  Nodes: {num_nodes:,}")
    print(f"  Edges: {edge_index.shape[1]:,}")


if __name__ == "__main__":
    convert_to_csv()
