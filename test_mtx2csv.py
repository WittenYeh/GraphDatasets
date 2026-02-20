#!/usr/bin/env python3
"""
Tests for mtx2csv.py
"""

import os
import sys
import csv
import random
import textwrap
import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mtx2csv import parse_mtx_to_csv, WRITE_CHUNK


def _write_mtx(path, edges, num_nodes=None):
    """Write a coordinate-pattern MTX file from a list of (src, dst) 1-indexed pairs."""
    n = num_nodes or max(max(s, d) for s, d in edges)
    with open(path, 'w') as f:
        f.write("%%MatrixMarket matrix coordinate pattern general\n")
        f.write(f"{n} {n} {len(edges)}\n")
        for s, d in edges:
            f.write(f"{s} {d}\n")


def _read_csv(path):
    with open(path, newline='') as f:
        return list(csv.DictReader(f))


def _make_large_edges(num_nodes, num_edges, seed=42):
    """Generate random 1-indexed edges spanning num_nodes nodes."""
    rng = random.Random(seed)
    return [(rng.randint(1, num_nodes), rng.randint(1, num_nodes)) for _ in range(num_edges)]


# ---------------------------------------------------------------------------
# Small / correctness tests
# ---------------------------------------------------------------------------

def test_basic_triangle(tmp_path):
    """3-node triangle: nodes 1-2-3 become 0-1-2."""
    mtx = tmp_path / "tri.mtx"
    _write_mtx(str(mtx), [(1, 2), (2, 3), (1, 3)])
    parse_mtx_to_csv(str(mtx), str(tmp_path))

    nodes = _read_csv(str(tmp_path / "nodes.csv"))
    edges = _read_csv(str(tmp_path / "edges.csv"))

    node_ids = {int(r["node_id"]) for r in nodes}
    assert node_ids == {0, 1, 2}
    assert len(edges) == 3
    for e in edges:
        assert int(e["src"]) in node_ids
        assert int(e["dst"]) in node_ids


def test_node_ids_contiguous_zero_based(tmp_path):
    """Sparse original IDs (1, 5, 10) must be remapped to 0, 1, 2."""
    mtx = tmp_path / "sparse.mtx"
    _write_mtx(str(mtx), [(1, 5), (5, 10)], num_nodes=10)
    parse_mtx_to_csv(str(mtx), str(tmp_path))

    nodes = _read_csv(str(tmp_path / "nodes.csv"))
    node_ids = sorted(int(r["node_id"]) for r in nodes)
    assert node_ids == list(range(len(node_ids))), "Node IDs must be contiguous 0-based"


def test_self_loops(tmp_path):
    """Self-loops (src == dst) should be preserved."""
    mtx = tmp_path / "loop.mtx"
    _write_mtx(str(mtx), [(1, 1), (2, 3)])
    parse_mtx_to_csv(str(mtx), str(tmp_path))

    edges = _read_csv(str(tmp_path / "edges.csv"))
    assert len(edges) == 2
    self_loops = [e for e in edges if e["src"] == e["dst"]]
    assert len(self_loops) == 1


def test_csv_headers(tmp_path):
    """nodes.csv must have 'node_id' header; edges.csv must have 'src,dst'."""
    mtx = tmp_path / "hdr.mtx"
    _write_mtx(str(mtx), [(1, 2)])
    parse_mtx_to_csv(str(mtx), str(tmp_path))

    with open(tmp_path / "nodes.csv") as f:
        assert f.readline().strip() == "node_id"
    with open(tmp_path / "edges.csv") as f:
        assert f.readline().strip() == "src,dst"


def test_missing_file_exits(tmp_path):
    """parse_mtx_to_csv should call sys.exit(1) for a missing file."""
    with pytest.raises(SystemExit) as exc_info:
        parse_mtx_to_csv(str(tmp_path / "nonexistent.mtx"), str(tmp_path))
    assert exc_info.value.code == 1


# ---------------------------------------------------------------------------
# Large dataset test (forces multiple WRITE_CHUNK chunks)
# ---------------------------------------------------------------------------

def test_large_dataset_multi_chunk(tmp_path):
    """
    Generate a dataset large enough to produce multiple write chunks,
    verify correctness of node count, edge count, ID remapping, and
    that no temp files are left behind.
    """
    num_nodes = 10_000
    num_edges = WRITE_CHUNK * 3 + 7  # guaranteed to span >3 chunks

    raw_edges = _make_large_edges(num_nodes, num_edges)
    mtx = tmp_path / "large.mtx"
    _write_mtx(str(mtx), raw_edges, num_nodes=num_nodes)

    parse_mtx_to_csv(str(mtx), str(tmp_path))

    # All nodes referenced in edges
    referenced = {s for s, _ in raw_edges} | {d for _, d in raw_edges}
    expected_node_count = len(referenced)

    nodes = _read_csv(str(tmp_path / "nodes.csv"))
    edges = _read_csv(str(tmp_path / "edges.csv"))

    # Node count matches unique referenced nodes
    assert len(nodes) == expected_node_count

    # Node IDs are contiguous 0-based
    node_ids = sorted(int(r["node_id"]) for r in nodes)
    assert node_ids == list(range(expected_node_count))

    # Edge count matches
    assert len(edges) == num_edges

    # All edge endpoints are valid node IDs
    valid_ids = set(node_ids)
    for e in edges:
        assert int(e["src"]) in valid_ids
        assert int(e["dst"]) in valid_ids

    # No temp files left
    leftover = list(tmp_path.glob("*.part*"))
    assert leftover == [], f"Temp files not cleaned up: {leftover}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
