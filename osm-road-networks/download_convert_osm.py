#!/usr/bin/env python3
"""
Download and convert an OSM road network to CSV format using osmnx.

Usage:
    python3 download_convert_osm.py [--place "Singapore"] [--output-dir .]

Outputs per place (in a subdirectory named after the place):
    nodes.csv  - node_id, lat, lon
    edges.csv  - src, dst, length, speed_kph, travel_time, name, highway, oneway, maxspeed, lanes
"""

import argparse
import os
import re
import sys
import csv
import osmnx as ox
from tqdm import tqdm


def slugify(name: str) -> str:
    """Convert a place name to a safe directory name."""
    name = name.lower()
    name = re.sub(r"[^\w\s-]", "", name)
    name = re.sub(r"[\s]+", "_", name.strip())
    return name


def download_and_convert(place: str, output_dir: str, name: str = None) -> None:
    city_slug = name if name else slugify(place)
    city_dir = os.path.join(output_dir, city_slug)
    os.makedirs(city_dir, exist_ok=True)

    nodes_file = os.path.join(city_dir, "nodes.csv")
    edges_file = os.path.join(city_dir, "edges.csv")

    if os.path.exists(nodes_file) and os.path.exists(edges_file):
        print(f"  Already exists: {city_dir}, skipping download.")
        return

    print(f"Downloading road network for: {place}")
    G = ox.graph_from_place(place, network_type="drive")
    G = ox.add_edge_speeds(G)
    G = ox.add_edge_travel_times(G)

    nodes_gdf, edges_gdf = ox.graph_to_gdfs(G)

    # --- Build contiguous 0-based node ID mapping ---
    osm_ids = list(nodes_gdf.index)
    id_map = {osm_id: idx for idx, osm_id in enumerate(osm_ids)}
    num_nodes = len(osm_ids)

    # --- Write nodes.csv ---
    print(f"  Writing {nodes_file} ({num_nodes:,} nodes)...")
    with open(nodes_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["node_id", "lat", "lon"])
        for osm_id, row in tqdm(nodes_gdf.iterrows(), total=num_nodes, desc="  nodes", unit="nodes"):
            writer.writerow([id_map[osm_id], row["y"], row["x"]])

    # --- Write edges.csv ---
    # Columns to export (all available road attributes)
    EDGE_PROPS = ["length", "speed_kph", "travel_time", "name", "highway", "oneway", "maxspeed", "lanes"]

    num_edges = len(edges_gdf)
    print(f"  Writing {edges_file} ({num_edges:,} edges)...")
    with open(edges_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["src", "dst"] + EDGE_PROPS)
        for (u, v, _key), row in tqdm(edges_gdf.iterrows(), total=num_edges, desc="  edges", unit="edges"):
            src = id_map.get(u)
            dst = id_map.get(v)
            if src is None or dst is None:
                continue
            props = []
            for col in EDGE_PROPS:
                val = row.get(col, "")
                # Lists (e.g. multiple highway types) -> join with |
                if isinstance(val, list):
                    val = "|".join(str(x) for x in val)
                props.append("" if val != val else str(val))  # NaN -> ""
            writer.writerow([src, dst] + props)

    print(f"  Done: {city_dir}")
    print(f"    Nodes: {num_nodes:,}")
    print(f"    Edges: {num_edges:,}")


def main():
    parser = argparse.ArgumentParser(description="Download OSM road network and convert to CSV")
    parser.add_argument(
        "--place",
        default="Singapore",
        help='Place name for osmnx (default: "Singapore")',
    )
    parser.add_argument(
        "--output-dir",
        default=".",
        help="Output directory (a subdirectory per place will be created)",
    )
    parser.add_argument(
        "--name",
        default=None,
        help="Custom output subdirectory name (default: slugified place name)",
    )
    args = parser.parse_args()

    download_and_convert(args.place, args.output_dir, args.name)


if __name__ == "__main__":
    main()
