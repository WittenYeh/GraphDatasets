#!/usr/bin/env python3
"""
Convert IMDB TSV dataset to CSV format.
Expects decompressed .tsv files in the current directory (handled by Makefile).
Generates two files: nodes.csv (with features) and edges.csv

Graph model (bipartite):
  - Nodes: titles (movies/shows) + people (actors/directors/etc.)
  - Edges: title.principals (person participated in title)
  - Node properties: type, primary info, ratings
"""

import csv
import os
from tqdm import tqdm


def count_lines(filepath):
    """Count lines in a file (excluding header)."""
    with open(filepath, 'r', encoding='utf-8') as f:
        f.readline()
        return sum(1 for _ in f)


def read_tsv(filepath, desc=None):
    """Yield rows from a TSV file as dicts, with progress bar."""
    total = count_lines(filepath) if desc else None
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t', quoting=csv.QUOTE_NONE)
        if desc:
            yield from tqdm(reader, total=total, desc=desc, unit="rows")
        else:
            yield from reader


def convert_to_csv(output_dir="."):
    """Convert IMDB TSV files to nodes.csv and edges.csv."""

    # --- Pass 1: Read title.principals to find referenced titles and people ---
    print("Pass 1: Scanning title.principals for referenced IDs...")
    referenced_titles = set()
    referenced_people = set()
    edge_pairs = []

    for row in read_tsv(os.path.join(output_dir, "title.principals.tsv"), desc="Scanning principals"):
        tconst = row['tconst']
        nconst = row['nconst']
        referenced_titles.add(tconst)
        referenced_people.add(nconst)
        edge_pairs.append((nconst, tconst))

    print(f"  Referenced titles: {len(referenced_titles):,}")
    print(f"  Referenced people: {len(referenced_people):,}")
    print(f"  Edge pairs: {len(edge_pairs):,}")

    # --- Pass 2: Build ID map and write nodes ---
    id_map = {}
    next_id = 0

    print("Loading title ratings...")
    ratings = {}
    for row in read_tsv(os.path.join(output_dir, "title.ratings.tsv"), desc="Reading ratings"):
        ratings[row['tconst']] = row.get('averageRating', '')

    nodes_file = os.path.join(output_dir, "nodes.csv")
    print(f"Writing nodes to {nodes_file}...")

    with open(nodes_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["node_id", "type", "name", "year", "rating"])

        title_count = 0
        for row in read_tsv(os.path.join(output_dir, "title.basics.tsv"), desc="Reading titles"):
            tconst = row['tconst']
            if tconst not in referenced_titles:
                continue
            id_map[tconst] = next_id
            name = row.get('primaryTitle', '')
            year = row.get('startYear', '')
            if year == '\\N':
                year = ''
            rating = ratings.get(tconst, '')
            writer.writerow([next_id, "title", name, year, rating])
            next_id += 1
            title_count += 1

        people_count = 0
        for row in read_tsv(os.path.join(output_dir, "name.basics.tsv"), desc="Reading people"):
            nconst = row['nconst']
            if nconst not in referenced_people:
                continue
            id_map[nconst] = next_id
            name = row.get('primaryName', '')
            birth = row.get('birthYear', '')
            if birth == '\\N':
                birth = ''
            writer.writerow([next_id, "person", name, birth, ""])
            next_id += 1
            people_count += 1

    # --- Pass 3: Write edges ---
    edges_file = os.path.join(output_dir, "edges.csv")
    print(f"Writing edges to {edges_file}...")
    edge_count = 0
    BATCH_SIZE = 100000
    batch = []

    with open(edges_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["src", "dst"])

        for nconst, tconst in tqdm(edge_pairs, desc="Writing edges", unit="edges"):
            if nconst in id_map and tconst in id_map:
                batch.append([id_map[nconst], id_map[tconst]])
                edge_count += 1
                if len(batch) >= BATCH_SIZE:
                    writer.writerows(batch)
                    batch.clear()
        if batch:
            writer.writerows(batch)

    print(f"Dataset converted successfully")
    print(f"  Titles: {title_count:,}")
    print(f"  People: {people_count:,}")
    print(f"  Total nodes: {title_count + people_count:,}")
    print(f"  Edges: {edge_count:,}")


if __name__ == "__main__":
    convert_to_csv(".")
