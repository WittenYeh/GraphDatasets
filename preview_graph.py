#!/usr/bin/env python3
"""
Graph dataset preview tool.

Usage:
  python preview_graph.py stats <directory>   Show dataset statistics with Rich visualization
  python preview_graph.py count <file>        Count edges in a graph file
"""

import argparse
import csv
import math
import os
import sys
from collections import Counter


def count_graph_edges(filename):
    """Count edges in a graph file (MTX header or line count)."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            first_line = f.readline()
            if first_line.startswith('%%MatrixMarket'):
                for line in f:
                    if line.startswith('%'):
                        continue
                    parts = line.split()
                    if len(parts) >= 3:
                        print(f"Matrix Market format — entries: {parts[2]}")
                    else:
                        print("Error: Malformed MTX header.", file=sys.stderr)
                    return
            else:
                count = 0
                if first_line.strip() and not first_line.startswith(('#', '%')):
                    count += 1
                for line in f:
                    if line.strip() and not line.startswith(('#', '%')):
                        count += 1
                print(f"Edge list format — lines: {count}")
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.", file=sys.stderr)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)


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

    # Read nodes
    with console.status("[bold cyan]Reading nodes..."):
        node_count = 0
        with open(nodes_file, 'r') as f:
            reader = csv.reader(f)
            next(reader)  # skip header
            for _ in reader:
                node_count += 1

    # Read edges and compute degrees
    with console.status("[bold cyan]Reading edges..."):
        degree = Counter()
        edge_count = 0
        with open(edges_file, 'r') as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                src, dst = int(row[0]), int(row[1])
                degree[src] += 1
                degree[dst] += 1
                edge_count += 1

    # Compute stats
    degrees = list(degree.values())
    isolated = node_count - len(degree)
    if isolated > 0:
        degrees.extend([0] * isolated)

    avg_degree = sum(degrees) / node_count if node_count else 0
    max_deg = max(degrees) if degrees else 0
    min_deg = min(degrees) if degrees else 0

    # Stats panel
    dataset_name = os.path.basename(os.path.abspath(directory))
    stats = Table(show_header=False, box=None, padding=(0, 2))
    stats.add_column(style="bold cyan")
    stats.add_column(style="white")
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
        hist.add_row(label, f"{count:,}", f"{bar} {pct:.1f}%")

    console.print(hist)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Graph dataset preview tool",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command")

    # stats
    p_stats = sub.add_parser("stats", help="Show dataset statistics (nodes, edges, degree distribution)")
    p_stats.add_argument("directory", help="Path to dataset directory containing nodes.csv and edges.csv")

    # count
    p_count = sub.add_parser("count", help="Count edges in a graph file")
    p_count.add_argument("filename", help="Path to the graph file")

    args = parser.parse_args()

    if args.command == "stats":
        show_dataset_stats(args.directory)
    elif args.command == "count":
        count_graph_edges(args.filename)
    else:
        parser.print_help()
