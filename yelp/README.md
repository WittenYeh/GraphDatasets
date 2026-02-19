# Yelp Open Dataset

## Description
The Yelp Open Dataset contains data about businesses, reviews, and users from Yelp.

- **Source**: [Yelp Open Dataset](https://www.yelp.com/dataset)
- **Format**: JSON (converted to CSV)
- **Graph Type**: Bipartite graph (users and businesses)

## Dataset Details
- Nodes: Businesses and Users
- Edges: Reviews (user -> business relationships)
- Typical size: ~150K businesses, ~2M users, ~8M reviews

## Usage

### Download and Convert
The dataset will be automatically downloaded from Yelp's public URL:
```bash
make
```

This will:
1. Download the Yelp-JSON.zip file (~10GB)
2. Extract the JSON files
3. Convert to CSV format (nodes.csv and edges.csv)

### Clean
```bash
make clean      # Remove generated CSV files
make realclean  # Remove all files including JSON data and zip
```

## Output Format

### nodes.csv
```
node_id,type
0,business
1,business
...
150000,user
150001,user
...
```

### edges.csv
```
src,dst
150000,0
150001,5
...
```

## Requirements
- Python 3
- ~15GB disk space for extracted JSON files
- ~2GB additional space for CSV files
