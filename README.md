# GraphDatasets

Scripts for Downloading Graph Datasets

## SNAP Dataset Downloader and Overview

This project includes a Python script (`download_datasets.py`) to automatically download, decompress, and manage a collection of popular graph datasets from the Stanford Network Analysis Project (SNAP).

### Dataset Overview

The table below provides a detailed overview of the properties for each dataset downloaded by the script. All data is sourced from the [Stanford Network Analysis Project (SNAP)](https://snap.stanford.edu/data/).

**Note**: The term `ungraph` in a filename indicates that the graph has been processed as **undirected** (i.e., if an edge from node A to B exists, an edge from B to A is also considered to exist).

| Dataset Name | Filename | Nodes | Edges | Graph Type | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **DBLP Collaboration** | `com-dblp.ungraph.txt` | 317,080 | 1,049,866 | Undirected | A scientific collaboration network. Nodes represent authors, and an edge connects two authors if they have co-authored at least one paper. |
| **LiveJournal** | `com-lj.ungraph.txt` | 3,997,962 | 34,681,189 | Undirected | A social network from the LiveJournal online community. Nodes are users, and edges represent friendships. |
| **Orkut** | `com-orkut.ungraph.txt` | 3,072,441 | 117,185,083 | Undirected | A social network from the Orkut online community. Nodes are users, and edges represent friendships. |
| **Friendster** | `com-friendster.ungraph.txt` | 65,608,366 | 1,806,067,135 | Undirected | A social network from the Friendster online gaming community. This is one of the largest graphs in this collection. |
| **Patent Citations** | `cit-Patents.txt` | 3,774,768 | 16,518,948 | **Directed** | A citation network. Nodes represent U.S. patents, and a directed edge from patent A to patent B indicates that A cites B. |
| **Twitter-2010** | `twitter-2010.txt` | 41,652,230 | 1,468,365,182 | **Directed** | A social network representing user relationships on Twitter from 2010. A directed edge from A to B means user A follows user B. |

### Important Notes

*   **Disk Space**: Be aware that the `com-friendster` and `twitter-2010` datasets are extremely large. The decompressed `.txt` files will consume a significant amount of disk space (tens of gigabytes). Please ensure you have adequate storage available.
*   **Data Format**: All dataset files are formatted as an **edge list**. Each line represents a single edge, consisting of two node IDs separated by a space or a tab. For example:

```
# Represents an edge from node 0 to node 1
0 1
# Represents an edge from node 0 to node 2
0 2
```

> Lines beginning with `#` are typically comments containing metadata about the file.