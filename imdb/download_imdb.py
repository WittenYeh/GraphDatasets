#!/usr/bin/env python3
"""
Download and convert IMDB dataset to CSV format.
Generates two files: nodes.csv (with features) and edges.csv

Graph model (bipartite):
  - Nodes: titles (movies/shows) + people (actors/directors/etc.)
  - Edges: title.principals (person participated in title)
  - Node properties: type, primary info, ratings
"""

import os
import sys
import csv
import gzip
import urllib.request

IMDB_BASE_URL = "https://datasets.imdbws.com/"
DATASETS = [
    "name.basics.tsv.gz",
    "title.basics.tsv.gz",
    "title.principals.tsv.gz",
    "title.ratings.tsv.gz",
]


def download_file(filename, output_dir="."):
    """Download a single IMDB dataset file if not already present."""
    filepath = os.path.join(output_dir, filename)
    if os.path.exists(filepath):
        print(f"Already exists: {filepath}")
        return filepath

    url = IMDB_BASE_URL + filename
    print(f"Downloading {url}...")
    try:
        from tqdm import tqdm
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        })
        with urllib.request.urlopen(req) as response, open(filepath, 'wb') as out:
            total = int(response.headers.get('Content-Length', 0))
            with tqdm(total=total, unit='B', unit_scale=True, desc=filename) as pbar:
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    out.write(chunk)
                    pbar.update(len(chunk))
    except ImportError:
        urllib.request.urlretrieve(url, filepath)
    print(f"  Downloaded: {filepath}")
    return filepath


def read_tsv_gz(filepath):
    """Yield rows from a gzipped TSV file as dicts."""
    with gzip.open(filepath, 'rt', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t', quoting=csv.QUOTE_NONE)
        yield from reader


def convert_to_csv(output_dir="."):
    """Convert IMDB TSV files to nodes.csv and edges.csv."""
    try:
        from tqdm import tqdm
    except ImportError:
        tqdm = lambda iterable, **kwargs: iterable

    # --- Pass 1: Read title.principals to find referenced titles and people ---
    print("Pass 1: Scanning title.principals for referenced IDs...")
    principals_file = os.path.join(output_dir, "title.principals.tsv.gz")
    referenced_titles = set()
    referenced_people = set()
    edge_pairs = []

    for row in tqdm(read_tsv_gz(principals_file), desc="Scanning principals", unit="rows"):
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

    # Load ratings into a lookup dict
    print("Loading title ratings...")
    ratings_file = os.path.join(output_dir, "title.ratings.tsv.gz")
    ratings = {}
    for row in tqdm(read_tsv_gz(ratings_file), desc="Reading ratings", unit="rows"):
        ratings[row['tconst']] = row.get('averageRating', '')

    nodes_file = os.path.join(output_dir, "nodes.csv")
    print(f"Writing nodes to {nodes_file}...")

    with open(nodes_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["node_id", "type", "name", "year", "rating"])

        # Process titles
        print("Processing titles...")
        title_count = 0
        title_file = os.path.join(output_dir, "title.basics.tsv.gz")
        for row in tqdm(read_tsv_gz(title_file), desc="Reading titles", unit="rows"):
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

        # Process people
        print("Processing people...")
        people_count = 0
        name_file = os.path.join(output_dir, "name.basics.tsv.gz")
        for row in tqdm(read_tsv_gz(name_file), desc="Reading people", unit="rows"):
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
    output_dir = "."
    for ds in DATASETS:
        download_file(ds, output_dir)
    convert_to_csv(output_dir)
