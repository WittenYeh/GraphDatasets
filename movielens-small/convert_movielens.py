#!/usr/bin/env python3
"""
Convert MovieLens dataset to graph CSV format.
Expects extracted MovieLens directory with ratings.csv and movies.csv.

Graph model (bipartite):
  - Nodes: users + movies
  - Edges: ratings (user rated movie)
  - Node properties: type, title/genres (movies), rating count (users)
"""

import csv
import os
import sys
from collections import Counter
from tqdm import tqdm


def count_lines(filepath):
    """Count lines in a file (excluding header)."""
    with open(filepath, 'r', encoding='utf-8') as f:
        f.readline()
        return sum(1 for _ in f)


def convert_to_csv(data_dir, output_dir="."):
    """Convert MovieLens CSV files to nodes.csv and edges.csv."""

    ratings_file = os.path.join(data_dir, "ratings.csv")
    movies_file = os.path.join(data_dir, "movies.csv")

    for path in (ratings_file, movies_file):
        if not os.path.exists(path):
            print(f"Error: {path} not found", file=sys.stderr)
            sys.exit(1)

    # --- Pass 1: Read ratings to collect users, movies, and edges ---
    print("Pass 1: Scanning ratings...")
    total_ratings = count_lines(ratings_file)
    user_ids = set()
    movie_ids = set()
    edge_pairs = []

    with open(ratings_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in tqdm(reader, total=total_ratings, desc="Scanning ratings", unit="rows"):
            uid = int(row['userId'])
            mid = int(row['movieId'])
            user_ids.add(uid)
            movie_ids.add(mid)
            edge_pairs.append((uid, mid, row['rating'], row['timestamp']))

    print(f"  Users: {len(user_ids):,}")
    print(f"  Movies: {len(movie_ids):,}")
    print(f"  Ratings: {len(edge_pairs):,}")

    # --- Pass 2: Load movie metadata ---
    print("Loading movie metadata...")
    movie_meta = {}
    with open(movies_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            mid = int(row['movieId'])
            if mid in movie_ids:
                movie_meta[mid] = (row.get('title', ''), row.get('genres', ''))

    # --- Pass 3: Build ID map and write nodes ---
    id_map = {}
    next_id = 0

    # Count ratings per user for node property
    user_rating_count = Counter()
    for uid, _, _, _ in edge_pairs:
        user_rating_count[uid] += 1

    nodes_file = os.path.join(output_dir, "nodes.csv")
    print(f"Writing nodes to {nodes_file}...")

    with open(nodes_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["node_id", "type", "name", "genres", "rating_count"])

        # Movies
        for mid in sorted(movie_ids):
            id_map[('movie', mid)] = next_id
            title, genres = movie_meta.get(mid, ('', ''))
            writer.writerow([next_id, "movie", title, genres, ""])
            next_id += 1

        # Users
        for uid in sorted(user_ids):
            id_map[('user', uid)] = next_id
            writer.writerow([next_id, "user", "", "", user_rating_count[uid]])
            next_id += 1

    # --- Pass 4: Write edges ---
    edges_file = os.path.join(output_dir, "edges.csv")
    print(f"Writing edges to {edges_file}...")
    BATCH_SIZE = 100000
    batch = []

    with open(edges_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["src", "dst", "rating", "timestamp"])

        for uid, mid, rating, timestamp in tqdm(edge_pairs, desc="Writing edges", unit="edges"):
            batch.append([id_map[('user', uid)], id_map[('movie', mid)], rating, timestamp])
            if len(batch) >= BATCH_SIZE:
                writer.writerows(batch)
                batch.clear()
        if batch:
            writer.writerows(batch)

    total_nodes = len(user_ids) + len(movie_ids)
    print(f"Dataset converted successfully")
    print(f"  Movies: {len(movie_ids):,}")
    print(f"  Users: {len(user_ids):,}")
    print(f"  Total nodes: {total_nodes:,}")
    print(f"  Edges: {len(edge_pairs):,}")


if __name__ == "__main__":
    # data_dir is the extracted MovieLens directory (e.g., ml-latest-small/)
    if len(sys.argv) < 2:
        print("Usage: convert_movielens.py <data_dir> [output_dir]", file=sys.stderr)
        sys.exit(1)
    data_dir = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "."
    convert_to_csv(data_dir, output_dir)
