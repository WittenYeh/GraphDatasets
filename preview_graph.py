#!/usr/bin/env python3
"""
Graph dataset preview tool.

Usage:
  python preview_graph.py <directory>   Show dataset statistics with Rich visualization
"""

import argparse
import math
import os
from collections import Counter
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map

NUM_WORKERS = 64
CHUNK_SIZE = 1 * 1024 * 1024  # 1MB per chunk


def _file_chunk_ranges(filepath):
    """Split a file into byte ranges aligned to line boundaries.
    Returns list of (filepath, start, end) tuples."""
    file_size = os.path.getsize(filepath)
    if file_size == 0:
        return []
    ranges = []
    with open(filepath, 'rb') as f:
        f.readline()  # skip header
        data_start = f.tell()
        start = data_start
        while start < file_size:
            end = min(start + CHUNK_SIZE, file_size)
            if end < file_size:
                f.seek(end)
                f.readline()  # align to next line boundary
                end = f.tell()
            ranges.append((filepath, start, end))
            start = end
    return ranges


def _count_lines_chunk(args):
    """Count lines in a byte range of a file."""
    filepath, start, end = args
    count = 0
    with open(filepath, 'rb') as f:
        f.seek(start)
        remaining = end - start
        while remaining > 0:
            chunk = f.read(min(1024 * 1024, remaining))
            if not chunk:
                break
            count += chunk.count(b'\n')
            remaining -= len(chunk)
    return count


def _read_edges_chunk(args):
    """Read edges in a byte range and return (count, degree_counter)."""
    filepath, start, end = args
    degree = Counter()
    count = 0
    with open(filepath, 'r') as f:
        f.seek(start)
        pos = start
        while pos < end:
            line = f.readline()
            if not line:
                break
            pos = f.tell()
            line = line.strip()
            if not line:
                continue
            parts = line.split(',')
            src, dst = int(parts[0]), int(parts[1])
            degree[src] += 1
            degree[dst] += 1
            count += 1
    return count, degree


def show_dataset_stats(directory):
    """Show dataset statistics with Rich terminal visualization."""
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel

    console = Console()

    nodes_file = os.path.join(directory, "nodes.csv")
    edges_file = os.path.join(directory, "edges.csv")

    for path in (nodes_file, edges_file):
        if not os.path.exists(path):
            console.print(f"[red]Error: {path} not found[/red]")
            return

    # Read CSV headers
    def _read_header(filepath):
        with open(filepath, 'r') as f:
            return f.readline().strip()

    nodes_header = _read_header(nodes_file)
    edges_header = _read_header(edges_file)

    # Read nodes (count lines in parallel)
    node_ranges = _file_chunk_ranges(nodes_file)
    node_counts = process_map(_count_lines_chunk, node_ranges,
                              max_workers=NUM_WORKERS, desc="Reading nodes")
    node_count = sum(node_counts)

    # Read edges (parse and compute degrees in parallel — multiprocess to bypass GIL)
    edge_ranges = _file_chunk_ranges(edges_file)
    edge_results = process_map(_read_edges_chunk, edge_ranges,
                               max_workers=NUM_WORKERS, desc="Reading edges")
    edge_count = 0
    degree = Counter()
    for count, deg in tqdm(edge_results, desc="Merging degrees", unit="chunks"):
        edge_count += count
        degree += deg

    # Compute stats
    degrees = list(degree.values())
    isolated = node_count - len(degree)
    if isolated > 0:
        degrees.extend([0] * isolated)

    avg_degree = sum(degrees) / node_count if node_count else 0
    max_deg = max(degrees) if degrees else 0
    min_deg = min(degrees) if degrees else 0

    # File sizes
    def _human_size(size):
        for unit in ('B', 'KB', 'MB', 'GB', 'TB'):
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} PB"

    nodes_size = os.path.getsize(nodes_file)
    edges_size = os.path.getsize(edges_file)
    total_size = nodes_size + edges_size

    # Stats panel
    dataset_name = os.path.basename(os.path.abspath(directory))
    stats = Table(show_header=False, box=None, padding=(0, 2))
    stats.add_column(style="bold cyan")
    stats.add_column(style="white")
    stats.add_row("File Size", f"{_human_size(total_size)} (nodes: {_human_size(nodes_size)}, edges: {_human_size(edges_size)})")
    stats.add_row("Nodes Header", nodes_header)
    stats.add_row("Edges Header", edges_header)
    stats.add_row("Nodes", f"{node_count:,}")
    stats.add_row("Edges", f"{edge_count:,}")
    stats.add_row("Avg Degree", f"{avg_degree:.2f}")
    stats.add_row("Max Degree", f"{max_deg:,}")
    stats.add_row("Min Degree", f"{min_deg:,}")

    console.print()
    console.print(Panel(stats, title=f"[bold]{dataset_name}[/bold]", border_style="blue"))

    if not degrees:
        return

    # Degree distribution — log2 buckets
    buckets = {}
    for d in degrees:
        if d == 0:
            key = (0, 0)
        else:
            exp = int(math.log2(d))
            key = (2 ** exp, 2 ** (exp + 1) - 1)
        buckets[key] = buckets.get(key, 0) + 1

    sorted_buckets = sorted(buckets.items(), key=lambda x: x[0][0])
    max_count = max(buckets.values())
    BAR_WIDTH = 40

    hist = Table(title="Degree Distribution", border_style="blue")
    hist.add_column("Degree", style="cyan", justify="right")
    hist.add_column("Count", style="white", justify="right")
    hist.add_column("Distribution", style="green", no_wrap=True)

    for (lo, hi), count in sorted_buckets:
        label = f"{lo}" if lo == hi else f"{lo}-{hi}"
        bar_len = int(count / max_count * BAR_WIDTH)
        bar = "█" * max(bar_len, 1)
        pct = count / node_count * 100
        hist.add_row(label, f"{count:,}", f"{bar} {pct:.5f}%")

    console.print(hist)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Graph dataset preview tool",
    )
    parser.add_argument("directory", help="Path to dataset directory containing nodes.csv and edges.csv")

    args = parser.parse_args()
    show_dataset_stats(args.directory)
