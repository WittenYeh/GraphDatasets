#!/usr/bin/env python3
"""
Download OGB ogbn-products dataset using the official OGB loader.
The downloaded data is stored in the ogbn_products/ subdirectory.
"""

import builtins
import sys

try:
    from ogb.nodeproppred import NodePropPredDataset
except ImportError:
    print("Error: ogb library not found. Install with: pip install ogb", file=sys.stderr)
    sys.exit(1)

# Monkey patch input to auto-confirm downloads
_original_input = builtins.input
def _auto_confirm_input(prompt):
    if "Will you proceed?" in prompt:
        print(prompt + "y (auto-confirmed)")
        return "y"
    return _original_input(prompt)
builtins.input = _auto_confirm_input


def download(dataset_name="ogbn-products", output_dir="."):
    print(f"Downloading {dataset_name} using OGB official loader...")
    NodePropPredDataset(name=dataset_name, root=output_dir)
    print(f"Download complete.")


if __name__ == "__main__":
    download()
