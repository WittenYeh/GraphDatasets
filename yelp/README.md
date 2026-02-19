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

## Manual Download Required

This dataset requires manual download:

1. Visit: https://www.yelp.com/dataset/download
2. Sign up and agree to the Yelp Dataset License
3. Download the dataset (tar file, ~10GB compressed)
4. Extract the tar file to this directory

Expected files after extraction:
- `yelp_academic_dataset_business.json`
- `yelp_academic_dataset_review.json`
- `yelp_academic_dataset_user.json`
- `yelp_academic_dataset_checkin.json` (optional)
- `yelp_academic_dataset_tip.json` (optional)

## Usage

### Convert to CSV
After downloading and extracting the dataset:
```bash
make
```

This will generate:
- `nodes.csv`: All nodes (businesses and users) with type labels
- `edges.csv`: All edges (reviews from users to businesses)

### Clean
```bash
make clean      # Remove generated CSV files
make realclean  # Remove all files including JSON data
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
