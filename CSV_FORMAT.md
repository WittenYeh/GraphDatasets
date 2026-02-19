# Graph Dataset CSV Format Specification

This document describes the CSV format for graph datasets after conversion from various source formats.

## 1. MTX Format (Matrix Market) Conversion

### Source Format
Matrix Market format is a text-based format for sparse matrices:
- Lines starting with `%` are comments
- First non-comment line: `rows cols entries`
- Following lines: `row col [value]` (1-indexed)

### Output Format

#### nodes.csv
Simple node list with 0-indexed IDs:
```csv
node_id
0
1
2
3
...
```

**Fields:**
- `node_id`: Integer, 0-indexed node identifier

#### edges.csv (Unweighted)
Basic edge list without weights:
```csv
src,dst
0,1
0,2
1,3
...
```

**Fields:**
- `src`: Integer, source node ID (0-indexed)
- `dst`: Integer, destination node ID (0-indexed)

#### edges.csv (Weighted)
Edge list with weight values:
```csv
src,dst,weight
0,1,0.5
0,2,1.0
1,3,0.75
...
```

**Fields:**
- `src`: Integer, source node ID (0-indexed)
- `dst`: Integer, destination node ID (0-indexed)
- `weight`: Float, edge weight from MTX value field

**Note:** Current implementation (`mtx2csv.py`) does not preserve weights. To support weighted graphs, the script needs to be modified to:
1. Check if MTX has 3 columns (row, col, value)
2. Add weight column to edges.csv
3. Store the weight value from the third column

## 2. Property Graph Format Conversion

Property graphs contain nodes and edges with attributes/properties.

### 2.1 OGB Format (ogbn-products)

#### nodes.csv
```csv
node_id
0
1
2
...
```

**Fields:**
- `node_id`: Integer, 0-indexed node identifier

**Note:** Node features are available in the original OGB format but not exported to CSV.

#### edges.csv
```csv
src,dst
0,1
0,5
1,3
...
```

**Fields:**
- `src`: Integer, source node ID
- `dst`: Integer, destination node ID

### 2.2 Yelp Format

#### nodes.csv
Bipartite graph with node types:
```csv
node_id,type
0,business
1,business
2,business
150000,user
150001,user
...
```

**Fields:**
- `node_id`: Integer, 0-indexed node identifier
- `type`: String, node type (`business` or `user`)

#### edges.csv
Review relationships:
```csv
src,dst
150000,0
150001,5
150002,0
...
```

**Fields:**
- `src`: Integer, user node ID (reviewer)
- `dst`: Integer, business node ID (reviewed business)

**Note:** Edge direction represents "user reviews business". Additional review properties (rating, text, date) are available in the original JSON but not exported to CSV.

## 3. General Conventions

### Common Rules
1. **Indexing**: All node IDs are 0-indexed
2. **Headers**: First line always contains column names
3. **Encoding**: UTF-8 encoding
4. **Delimiter**: Comma (`,`)
5. **No quotes**: Values are not quoted unless they contain special characters

### File Naming
- Node file: `nodes.csv`
- Edge file: `edges.csv`

### Data Types
- Node IDs: Non-negative integers starting from 0
- Weights: Floating-point numbers
- Types: String values (lowercase)

## 4. Extending the Format

### Adding Node Properties
To include node properties, add columns to nodes.csv:
```csv
node_id,type,label,feature_dim
0,business,restaurant,128
1,business,cafe,128
...
```

### Adding Edge Properties
To include edge properties, add columns to edges.csv:
```csv
src,dst,weight,timestamp,label
0,1,0.5,1609459200,friend
0,2,1.0,1609545600,colleague
...
```

### Recommendations
- Keep the basic `node_id` and `src,dst` columns as the first columns
- Add property columns after the basic columns
- Use descriptive column names
- Document the meaning and range of each property

## 5. Current Implementation Status

### Supported Features
- ✅ MTX to CSV (unweighted)
- ✅ OGB to CSV (basic structure)
- ✅ Yelp to CSV (with node types)
- ✅ Progress bars (tqdm)
- ✅ Skip download if files exist

### Not Yet Implemented
- ❌ MTX weighted graph support
- ❌ Node feature export from OGB
- ❌ Edge properties from Yelp (ratings, timestamps)
- ❌ Multi-graph support (multiple edge types)

## 6. Example Usage

### Reading in Python
```python
import pandas as pd

# Read nodes
nodes = pd.read_csv('nodes.csv')
print(f"Nodes: {len(nodes)}")

# Read edges
edges = pd.read_csv('edges.csv')
print(f"Edges: {len(edges)}")

# For typed nodes (like Yelp)
if 'type' in nodes.columns:
    print(nodes['type'].value_counts())
```

### Reading in C++
```cpp
#include <fstream>
#include <sstream>
#include <vector>

struct Edge {
    int src, dst;
    double weight;  // optional
};

std::vector<Edge> read_edges(const std::string& filename) {
    std::vector<Edge> edges;
    std::ifstream file(filename);
    std::string line;

    // Skip header
    std::getline(file, line);

    while (std::getline(file, line)) {
        std::istringstream iss(line);
        Edge e;
        char comma;
        iss >> e.src >> comma >> e.dst;
        edges.push_back(e);
    }

    return edges;
}
```
