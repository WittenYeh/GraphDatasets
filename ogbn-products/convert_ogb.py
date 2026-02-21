#!/usr/bin/env python3
"""
Convert OGB ogbn-products dataset to CSV format.
Expects the dataset to be already downloaded in the current directory.
Generates two files: nodes.csv (with labels) and edges.csv
"""

import json
import os
import sys
import csv
import torch

# Import type inference from parent directory
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from type_inference import generate_type_meta

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

# Fix PyTorch 2.6 weights_only issue
original_torch_load = torch.load
def patched_torch_load(*args, **kwargs):
    kwargs['weights_only'] = False
    return original_torch_load(*args, **kwargs)
torch.load = patched_torch_load


def convert_to_csv(dataset_name="ogbn-products", output_dir="."):
    # Check what files are missing
    nodes_file = os.path.join(output_dir, "nodes.csv")
    edges_file = os.path.join(output_dir, "edges.csv")
    type_meta_path = os.path.join(output_dir, "type_meta.json")

    # If only type_meta is missing and CSVs exist, just generate type_meta
    if os.path.exists(nodes_file) and os.path.exists(edges_file) and not os.path.exists(type_meta_path):
        print(f"CSVs exist, generating type_meta.json...")
        generate_type_meta(nodes_file, edges_file, type_meta_path)
        print(f"type_meta.json generated successfully")
        return

    # If CSVs exist, skip conversion
    if os.path.exists(nodes_file) and os.path.exists(edges_file):
        print(f"CSVs already exist, skipping conversion")
        return

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

    # Generate type_meta.json using type inference
    type_meta_path = os.path.join(output_dir, "type_meta.json")
    generate_type_meta(nodes_file, edges_file, type_meta_path)

    print(f"Dataset converted successfully")
    print(f"  Nodes: {num_nodes:,}")
    print(f"  Edges: {edge_index.shape[1]:,}")


if __name__ == "__main__":
    convert_to_csv()
