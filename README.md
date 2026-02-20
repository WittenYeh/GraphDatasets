# Graph Datasets

```
   ____                 _       ____        _                  _
  / ___|_ __ __ _ _ __ | |__   |  _ \  __ _| |_ __ _ ___  ___| |_ ___
 | |  _| '__/ _` | '_ \| '_ \  | | | |/ _` | __/ _` / __|/ _ \ __/ __|
 | |_| | | | (_| | |_) | | | | | |_| | (_| | || (_| \__ \  __/ |_\__ \
  \____|_|  \__,_| .__/|_| |_| |____/ \__,_|\__\__,_|___/\___|\__|___/
                 |_|
```

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Format: CSV](https://img.shields.io/badge/format-CSV-green.svg)](https://en.wikipedia.org/wiki/Comma-separated_values)

A collection of scripts to download and convert popular graph datasets into a **unified CSV format** for benchmarking graph databases and algorithms.

## ✨ Features

- 🎯 **Unified Format**: All datasets converted to consistent `nodes.csv` + `edges.csv` format
- 📊 **30+ Datasets**: From small test graphs to billion-edge networks
- 🚀 **Easy to Use**: Simple `make` commands to download and convert
- 🔄 **Multiple Sources**: Support for MTX, OGB, Yelp, and more
- 📈 **Progress Tracking**: Built-in progress bars for large downloads
- 💾 **Smart Caching**: Skip downloads if files already exist

## 🚀 Quick Start

```bash
# Build all datasets
make

# Build one or more specific datasets directly
make ak2010
make ak2010 belgium_osm soc-LiveJournal1

# Other targets work the same way
make fetch ak2010 belgium_osm   # download only, no conversion
make clean ak2010               # clean a specific dataset
```

## 📋 Unified CSV Format

All datasets are converted to a **consistent, simple format** for easy integration:

### nodes.csv
```csv
node_id
0
1
2
...
```

### edges.csv (Basic)
```csv
src,dst
0,1
0,2
1,3
...
```

### edges.csv (Weighted)
```csv
src,dst,weight
0,1,0.5
0,2,1.0
...
```

### Key Conventions
- ✅ **Contiguous 0-based node IDs**: All node IDs are remapped to a contiguous sequence starting from 0
- ✅ **UTF-8 encoded**: Universal compatibility
- ✅ **Header row**: Column names in first line
- ✅ **Comma-delimited**: Standard CSV format
- ✅ **Optional properties**: Extensible with additional columns (e.g., `type`, `label`)

**Note**: Node IDs are always remapped to a contiguous 0-based sequence [0, 1, 2, ..., N-1], regardless of the original IDs in the source dataset. This ensures consistent and efficient indexing across all datasets.

## 📚 Supported Datasets

### Social Networks
- `soc-LiveJournal1` - LiveJournal social network
- `soc-orkut` - Orkut social network
- `soc-twitter-2010` - Twitter follower network
- `soc-sinaweibo` - Sina Weibo social network

### Citation Networks
- `cit-Patents` - Patent citation network
- `coAuthorsDBLP` - DBLP co-authorship network

### Road Networks
- `roadNet-CA` - California road network
- `road_usa` - USA road network
- `road_central` - Central USA road network
- `belgium_osm` - Belgium OpenStreetMap
- `germany_osm` - Germany OpenStreetMap
- `europe_osm` - Europe OpenStreetMap
- `asia_osm` - Asia OpenStreetMap
- `osm-road-networks` - Any city via OpenStreetMap (osmnx), with road attributes (lat/lon, speed, travel time, highway type, etc.)

### Web Graphs
- `uk-2002` - UK web graph (2002)
- `uk-2005` - UK web graph (2005)
- `arabic-2005` - Arabic web graph
- `indochina-2004` - Indochina web graph
- `webbase-1M` - WebBase crawl (1M nodes)
- `webbase-2001` - WebBase crawl (2001)

### Synthetic Graphs
- `delaunay_n13` - Delaunay triangulation (2^13 nodes)
- `delaunay_n21` - Delaunay triangulation (2^21 nodes)
- `delaunay_n24` - Delaunay triangulation (2^24 nodes)
- `kron_g500-logn21` - Kronecker graph

### Property Graphs
- `ogbn-products` - Amazon product co-purchase network (OGB)
- `yelp` - Yelp user-business review network (bipartite)
- `imdb` - IMDB title-person bipartite network (movies, shows, cast & crew)
- `movielens-small` - MovieLens small rating dataset (~100K ratings)
- `movielens` - MovieLens full rating dataset (~33M ratings)
- `ldbc-snb` - LDBC Social Network Benchmark

### Other
- `hollywood-2009` - Hollywood actor collaboration network
- `ak2010` - Autonomous systems graph
- `geolocation` - Geolocation network

## 💻 Usage Examples

### Python
```python
import pandas as pd

# Load graph
nodes = pd.read_csv('nodes.csv')
edges = pd.read_csv('edges.csv')

print(f"Nodes: {len(nodes)}, Edges: {len(edges)}")

# For typed nodes (e.g., Yelp)
if 'type' in nodes.columns:
    print(nodes['type'].value_counts())
```

### C++
```cpp
#include <fstream>
#include <sstream>
#include <vector>

struct Edge { int src, dst; };

std::vector<Edge> read_edges(const std::string& filename) {
    std::vector<Edge> edges;
    std::ifstream file(filename);
    std::string line;

    std::getline(file, line);  // Skip header

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

## 🔧 Conversion Tools

- `mtx2csv.py` - Convert Matrix Market (.mtx) to CSV
- `ogbn-products/` - OGB dataset converter
- `yelp/` - Yelp dataset converter
- `osm-road-networks/` - OSM road network downloader (osmnx)
- `preview_graph.py` - Preview graph statistics

### OSM Road Networks

Download any city's road network using [osmnx](https://osmnx.readthedocs.io/):

```bash
# Default city (Pasadena, CA)
make osm-road-networks

# Custom city
make -C osm-road-networks PLACE="Beijing, China"
make -C osm-road-networks PLACE="Tokyo, Japan"
```

Output per city (in a subdirectory named after the place):

```
osm-road-networks/
  pasadena_california_usa/
    nodes.csv   # node_id, lat, lon
    edges.csv   # src, dst, length, speed_kph, travel_time, name, highway, oneway, maxspeed, lanes
  beijing_china/
    nodes.csv
    edges.csv
```

## 📖 Format Details

### Property Graphs
Some datasets include additional node/edge properties:

**Yelp** (bipartite graph):
```csv
node_id,type,stars,review_count
0,business,4.0,12
150346,user,3.72,15
...
```

**Extensible format** - add columns as needed:
```csv
src,dst,weight,timestamp,label
0,1,0.5,1609459200,friend
```

### Source Format Support
- ✅ MTX (Matrix Market)
- ✅ OGB (Open Graph Benchmark)
- ✅ Yelp JSON
- ✅ SNAP format
- ✅ Custom formats

## 🤝 Contributing

Contributions welcome! To add a new dataset:
1. Create a subdirectory with dataset name
2. Add a `Makefile` with download/conversion rules
3. Ensure output follows the unified CSV format
4. Update this README

## 📄 License

MIT License - see individual dataset sources for their respective licenses.

## 🔗 Dataset Sources

- [SNAP](http://snap.stanford.edu/data/)
- [Network Repository](http://networkrepository.com/)
- [SuiteSparse Matrix Collection](https://sparse.tamu.edu/)
- [OGB](https://ogb.stanford.edu/)
- [LDBC](https://ldbcouncil.org/)

---

**Note**: Dataset sizes range from thousands to billions of edges. Check individual dataset directories for specific statistics and download requirements.
