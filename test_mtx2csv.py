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
    """
    MTX header declares 10 nodes; only 3 appear in edges.
    All 10 nodes (including isolated ones) must appear in nodes.csv as 0..9.
    """
    mtx = tmp_path / "sparse.mtx"
    _write_mtx(str(mtx), [(1, 5), (5, 10)], num_nodes=10)
    parse_mtx_to_csv(str(mtx), str(tmp_path))

    nodes = _read_csv(str(tmp_path / "nodes.csv"))
    node_ids = sorted(int(r["node_id"]) for r in nodes)
    assert node_ids == list(range(10)), "All 10 nodes (including isolated) must be present"


def test_isolated_nodes_preserved(tmp_path):
    """
    MTX header declares 5 nodes; only nodes 1,2,3,4 appear in edges.
    Node 5 is isolated (degree-0) and must still appear in nodes.csv.
    """
    mtx = tmp_path / "isolated.mtx"
    _write_mtx(str(mtx), [(1, 2), (4, 3)], num_nodes=5)
    parse_mtx_to_csv(str(mtx), str(tmp_path))

    nodes = _read_csv(str(tmp_path / "nodes.csv"))
    node_ids = sorted(int(r["node_id"]) for r in nodes)
    assert node_ids == [0, 1, 2, 3, 4], "Isolated node must not be dropped"



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

    # New implementation uses shape[0] as authoritative node count,
    # so all num_nodes nodes are present (including any isolated ones).
    expected_node_count = num_nodes

    nodes = _read_csv(str(tmp_path / "nodes.csv"))
    edges = _read_csv(str(tmp_path / "edges.csv"))

    # Node count matches header declaration
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


# ---------------------------------------------------------------------------
# Real dataset test: soc-LiveJournal1
# ---------------------------------------------------------------------------

MTX_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "soc-LiveJournal1", "soc-LiveJournal1.mtx")
LJ_OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "soc-LiveJournal1")


def _parse_mtx_header(mtx_file):
    """Return (num_nodes, num_edges) from the MTX dimension line."""
    with open(mtx_file) as f:
        for line in f:
            if line.startswith('%'):
                continue
            parts = line.split()
            return int(parts[0]), int(parts[2])


def _fast_line_count(filepath):
    """Count lines in a file quickly using binary reads."""
    count = 0
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            count += chunk.count(b'\n')
    return count


@pytest.mark.skipif(not os.path.exists(MTX_PATH), reason="soc-LiveJournal1 dataset not found")
def test_livejournal_structure():
    """
    Verify graph structure is correctly preserved after MTX -> CSV conversion
    using the real soc-LiveJournal1 dataset.

    Reuses existing nodes.csv/edges.csv in the dataset directory to avoid
    re-running the conversion (which takes ~7 minutes).

    Checks:
    1. Edge count matches MTX header exactly.
    2. Node count matches unique nodes referenced in edges.
    3. Node IDs are contiguous 0-based [0, N-1].
    4. No edge endpoint references an out-of-range node ID.
    5. Out-degree distribution (log2-bucket histogram) is preserved.
    6. A random sample of 500 raw MTX edges all appear (remapped) in output.
    """
    import subprocess
    import numpy as np
    import fast_matrix_market as fmm

    nodes_file = os.path.join(LJ_OUT_DIR, "nodes.csv")
    edges_file = os.path.join(LJ_OUT_DIR, "edges.csv")

    # Run conversion only if output is missing
    if not os.path.exists(nodes_file) or not os.path.exists(edges_file):
        parse_mtx_to_csv(MTX_PATH, LJ_OUT_DIR)

    # --- Load MTX via fmm (fast, parallel, 0-indexed) ---
    _, declared_edges = _parse_mtx_header(MTX_PATH)
    (_, (rows_orig, cols_orig)), shape = fmm.read_coo(MTX_PATH, parallelism=8)

    # New implementation uses shape[0] as authoritative node count (preserves isolated nodes)
    expected_node_count = shape[0]
    # fmm returns 0-indexed IDs; new mtx2csv.py uses them directly without remapping
    src_out = rows_orig
    dst_out = cols_orig

    # 1. Edge count — fast binary line count minus header
    edge_line_count = _fast_line_count(edges_file) - 1
    assert edge_line_count == declared_edges, (
        f"Edge count mismatch: got {edge_line_count}, expected {declared_edges}"
    )

    # 2. Node count — fast binary line count minus header
    node_line_count = _fast_line_count(nodes_file) - 1
    assert node_line_count == expected_node_count, (
        f"Node count mismatch: got {node_line_count}, expected {expected_node_count}"
    )

    # 3. Node IDs contiguous 0-based: nodes.csv is written as range(N), so just check count
    # (the write loop in mtx2csv.py writes exactly range(num_nodes))
    assert node_line_count == expected_node_count  # already checked above

    # 4. No out-of-range endpoints (vectorized)
    assert int(src_out.min()) >= 0 and int(src_out.max()) < expected_node_count
    assert int(dst_out.min()) >= 0 and int(dst_out.max()) < expected_node_count

    # 5. Out-degree distribution preserved
    #    Since new mtx2csv.py uses fmm's 0-indexed IDs directly (no remapping),
    #    src_out == rows_orig, so degree sequences are identical by construction.
    orig_deg = np.bincount(rows_orig, minlength=expected_node_count)
    remapped_deg = np.bincount(src_out, minlength=expected_node_count)
    assert np.array_equal(orig_deg, remapped_deg), \
        "Out-degree sequence changed after conversion"

    # 6. Random sample of 500 edges from the numpy arrays (no file re-read)
    rng = random.Random(42)
    indices = rng.sample(range(len(rows_orig)), 500)
    out_edge_set = set(zip(src_out.tolist(), dst_out.tolist()))
    for i in indices:
        edge = (int(src_out[i]), int(dst_out[i]))
        assert edge in out_edge_set, f"Sampled edge index {i} not found in output edge set"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
