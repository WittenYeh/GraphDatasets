# ogbn-products Dataset

## Description
The ogbn-products dataset is an Amazon product co-purchasing network from the Open Graph Benchmark (OGB).

- **Nodes**: Products (2,449,029)
- **Edges**: Co-purchasing relationships (61,859,140 undirected edges)
- **Source**: [OGB - ogbn-products](https://ogb.stanford.edu/docs/nodeprop/#ogbn-products)

## Dataset Details
- Nodes represent Amazon products
- Edges indicate items frequently bought together
- Node features: 100-dimensional bag-of-words vectors from product descriptions
- Task: Multi-class classification into 47 product categories

## Usage

### Download and Setup
```bash
make
```

This will:
1. Install the OGB library if not present
2. Download the dataset using the official OGB loader
3. Generate `nodes.csv` and `edges.csv`

### Output Files
- `nodes.csv`: List of node IDs (one per line)
- `edges.csv`: Edge list with source and destination columns

### Clean
```bash
make clean      # Remove generated CSV files
make realclean  # Remove all files including downloaded data
```

## Requirements
- Python 3
- ogb library (automatically installed if missing)
