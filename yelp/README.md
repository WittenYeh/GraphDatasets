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
```

## Output Format

### nodes.csv
```
node_id,type,stars,review_count
0,business,4.0,12
1,business,3.5,8
...
150346,user,3.72,15
150347,user,4.12,42
...
```

### edges.csv
```
src,dst
150346,0
150347,5
...
```

Node IDs are contiguous 0-based integers. Businesses are assigned IDs first, followed by users.

## Requirements
- Python 3
- ~15GB disk space for extracted JSON files
- ~2GB additional space for CSV files
