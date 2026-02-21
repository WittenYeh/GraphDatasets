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

import os
import sys
import pandas as pd
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map

# Import type inference from parent directory
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from type_inference import generate_type_meta

NUM_WORKERS = 8
CHUNK_ROWS = 500_000


def _read_tsv(filepath, usecols=None, dtype=str):
    return pd.read_csv(
        filepath, sep='\t', dtype=dtype,
        usecols=usecols, na_values='\\N', keep_default_na=False,
        quoting=3,  # QUOTE_NONE
    )


def _scan_principals_chunk(args):
    """Process a chunk of title.principals, return (titles_set, people_set, edge_rows)."""
    chunk = args
    chunk = chunk.fillna('')
    titles = set(chunk['tconst'].unique())
    people = set(chunk['nconst'].unique())
    edges = chunk[['nconst', 'tconst', 'category', 'job', 'characters']].values.tolist()
    return titles, people, edges


def convert_to_csv(output_dir="."):
    """Convert IMDB TSV files to nodes.csv and edges.csv."""

    # Check what files are missing
    nodes_file = os.path.join(output_dir, "nodes.csv")
    edges_file = os.path.join(output_dir, "edges.csv")
    type_meta_path = os.path.join(output_dir, "type_meta.json")

    # If only type_meta is missing and CSVs exist, just generate type_meta
    if os.path.exists(nodes_file) and os.path.exists(edges_file) and not os.path.exists(type_meta_path):
        print(f"CSVs exist, generating type_meta.json...")
        generate_type_meta(nodes_file, edges_file, type_meta_path)
        print(f"type_meta.json generated successfully")
        return

    # If CSVs exist, skip conversion
    if os.path.exists(nodes_file) and os.path.exists(edges_file):
        print(f"CSVs already exist, skipping conversion")
        return

    principals_path = os.path.join(output_dir, "title.principals.tsv")
    ratings_path = os.path.join(output_dir, "title.ratings.tsv")
    title_basics_path = os.path.join(output_dir, "title.basics.tsv")
    name_basics_path = os.path.join(output_dir, "name.basics.tsv")

    # --- Pass 1: Scan principals in parallel chunks ---
    print("Pass 1: Scanning title.principals...")
    chunks = list(pd.read_csv(
        principals_path, sep='\t', dtype=str,
        usecols=['tconst', 'nconst', 'category', 'job', 'characters'],
        na_values='\\N', keep_default_na=False, quoting=3,
        chunksize=CHUNK_ROWS,
    ))
    results = process_map(
        _scan_principals_chunk, chunks,
        max_workers=NUM_WORKERS, desc="Scanning principals", unit="chunks"
    )
    referenced_titles = set()
    referenced_people = set()
    edge_pairs = []
    for ref_t, ref_p, pairs in results:
        referenced_titles |= ref_t
        referenced_people |= ref_p
        edge_pairs.extend(pairs)

    print(f"  Referenced titles: {len(referenced_titles):,}")
    print(f"  Referenced people: {len(referenced_people):,}")
    print(f"  Edge pairs: {len(edge_pairs):,}")

    # --- Load ratings ---
    print("Loading title ratings...")
    ratings_df = _read_tsv(ratings_path, usecols=['tconst', 'averageRating'])
    ratings = dict(zip(ratings_df['tconst'], ratings_df['averageRating']))
    del ratings_df

    # --- Pass 2: Build nodes ---
    print("Pass 2: Reading title.basics...")
    titles_df = _read_tsv(title_basics_path, usecols=['tconst', 'primaryTitle', 'startYear'])
    titles_df = titles_df[titles_df['tconst'].isin(referenced_titles)].copy()
    titles_df['rating'] = titles_df['tconst'].map(ratings).fillna('')
    titles_df['type'] = 'title'
    titles_df = titles_df.rename(columns={'primaryTitle': 'name', 'startYear': 'year'})

    print("Reading name.basics...")
    names_df = _read_tsv(name_basics_path, usecols=['nconst', 'primaryName', 'birthYear'])
    names_df = names_df[names_df['nconst'].isin(referenced_people)].copy()
    names_df['rating'] = ''
    names_df['type'] = 'person'
    names_df = names_df.rename(columns={'primaryName': 'name', 'birthYear': 'year'})

    # Assign contiguous node IDs
    titles_df = titles_df.reset_index(drop=True)
    titles_df['node_id'] = titles_df.index
    id_map_titles = dict(zip(titles_df['tconst'], titles_df['node_id']))

    offset = len(titles_df)
    names_df = names_df.reset_index(drop=True)
    names_df['node_id'] = names_df.index + offset
    id_map_names = dict(zip(names_df['nconst'], names_df['node_id']))

    id_map = {**id_map_titles, **id_map_names}

    nodes_file = os.path.join(output_dir, "nodes.csv")
    print(f"Writing nodes to {nodes_file}...")
    nodes_df = pd.concat([
        titles_df[['node_id', 'type', 'name', 'year', 'rating']],
        names_df[['node_id', 'type', 'name', 'year', 'rating']],
    ], ignore_index=True)
    nodes_df.to_csv(nodes_file, index=False)
    title_count = len(titles_df)
    people_count = len(names_df)
    del titles_df, names_df, nodes_df

    # --- Pass 3: Write edges ---
    edges_file = os.path.join(output_dir, "edges.csv")
    print(f"Writing edges to {edges_file}...")
    edges_df = pd.DataFrame(edge_pairs, columns=['nconst', 'tconst', 'category', 'job', 'characters'])
    edges_df = edges_df[edges_df['nconst'].isin(id_map) & edges_df['tconst'].isin(id_map)].copy()
    edges_df['src'] = edges_df['nconst'].map(id_map)
    edges_df['dst'] = edges_df['tconst'].map(id_map)
    edges_df[['src', 'dst', 'category', 'job', 'characters']].to_csv(edges_file, index=False)
    edge_count = len(edges_df)

    print(f"Dataset converted successfully")
    print(f"  Titles: {title_count:,}")
    print(f"  People: {people_count:,}")
    print(f"  Total nodes: {title_count + people_count:,}")
    print(f"  Edges: {edge_count:,}")

    # Generate type_meta.json
    type_meta_path = os.path.join(output_dir, "type_meta.json")
    generate_type_meta(nodes_file, edges_file, type_meta_path)


if __name__ == "__main__":
    convert_to_csv(".")
