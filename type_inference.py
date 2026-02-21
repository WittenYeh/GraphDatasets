#!/usr/bin/env python3
"""
Shared utility for inferring property types from CSV files and generating type_meta.json.
Uses pandas dtype inference to map CSV columns to simple type strings.
"""

import json
import os
import pandas as pd


def pandas_dtype_to_type_string(dtype):
    """
    Map pandas dtype to simple type string: 'integer', 'long', 'float', 'double', 'boolean', 'string'.
    """
    dtype_str = str(dtype)

    # Integer types
    if dtype_str in ['int8', 'int16', 'int32']:
        return 'integer'
    elif dtype_str in ['int64', 'Int64']:
        return 'long'

    # Float types
    elif dtype_str in ['float32']:
        return 'float'
    elif dtype_str in ['float64', 'Float64']:
        return 'double'

    # Boolean
    elif dtype_str == 'bool':
        return 'boolean'

    # Default to string for object, string, and unknown types
    else:
        return 'string'


def infer_types_from_csv(csv_path, skip_columns=0):
    """
    Read a CSV file and infer types for each column using pandas.

    Args:
        csv_path: Path to the CSV file
        skip_columns: Number of leading columns to skip (e.g., node_id, src/dst)

    Returns:
        dict: {column_name: type_string} for property columns only
    """
    # Read just a sample to infer types (first 10000 rows should be enough)
    df = pd.read_csv(csv_path, nrows=10000)

    type_map = {}
    for i, col in enumerate(df.columns):
        if i < skip_columns:
            continue  # Skip ID columns

        type_str = pandas_dtype_to_type_string(df[col].dtype)
        type_map[col] = type_str

    return type_map


def generate_type_meta(nodes_csv, edges_csv, output_path):
    """
    Generate type_meta.json from nodes.csv and edges.csv.

    Args:
        nodes_csv: Path to nodes.csv (first column is node_id)
        edges_csv: Path to edges.csv (first two columns are src, dst)
        output_path: Path to write type_meta.json
    """
    node_types = {}
    edge_types = {}

    if os.path.exists(nodes_csv):
        node_types = infer_types_from_csv(nodes_csv, skip_columns=1)

    if os.path.exists(edges_csv):
        edge_types = infer_types_from_csv(edges_csv, skip_columns=2)

    meta = {
        "node_properties": node_types,
        "edge_properties": edge_types
    }

    with open(output_path, 'w') as f:
        json.dump(meta, f, indent=2)

    print(f"Generated {output_path}")
    print(f"  Node properties: {len(node_types)}")
    print(f"  Edge properties: {len(edge_types)}")

    return meta


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: type_inference.py <dataset_dir>")
        print("  Generates type_meta.json from nodes.csv and edges.csv in dataset_dir")
        sys.exit(1)

    dataset_dir = sys.argv[1]
    nodes_csv = os.path.join(dataset_dir, "nodes.csv")
    edges_csv = os.path.join(dataset_dir, "edges.csv")
    output_path = os.path.join(dataset_dir, "type_meta.json")

    generate_type_meta(nodes_csv, edges_csv, output_path)
