# LDBC Social Network Benchmark Dataset

This directory contains scripts to generate LDBC SNB (Social Network Benchmark) datasets using the official [ldbc_snb_datagen_spark](https://github.com/ldbc/ldbc_snb_datagen_spark) tool.

## Prerequisites

- Git
- Java 8 or higher
- Maven (for building the datagen tool)
- Python 3 (optional, for Hadoop mode)

## Quick Start

### Generate default scale (SF=1)
```bash
make
```

### Generate specific scale factor
```bash
make SCALE=10    # Scale factor 10
make SCALE=100   # Scale factor 100
```

### Clean generated data
```bash
make clean       # Remove generated datasets
make realclean   # Remove everything including the datagen tool
```

## Scale Factors

The scale factor determines the size of the generated dataset:

| Scale Factor | Persons | Edges (approx) | Disk Size (approx) |
|--------------|---------|----------------|-------------------|
| SF=1         | ~11K    | ~180K          | ~100 MB           |
| SF=3         | ~27K    | ~540K          | ~300 MB           |
| SF=10        | ~73K    | ~1.8M          | ~1 GB             |
| SF=30        | ~182K   | ~5.4M          | ~3 GB             |
| SF=100       | ~499K   | ~18M           | ~10 GB            |
| SF=300       | ~1.2M   | ~54M           | ~30 GB            |
| SF=1000      | ~3.6M   | ~180M          | ~100 GB           |

## Output Format

The generated dataset will be in CSV format with the following structure:

```
ldbc-snb-sf<SCALE>/
├── dynamic/
│   ├── person/
│   ├── forum/
│   ├── post/
│   ├── comment/
│   └── ...
└── static/
    ├── organisation/
    ├── place/
    └── tag/
```

## Dataset Schema

The LDBC SNB dataset includes:

- **Entities**: Person, Forum, Post, Comment, Organisation, Place, Tag
- **Relationships**: knows, likes, hasCreator, isLocatedIn, hasTag, etc.
- **Properties**: Each entity and relationship has multiple properties (timestamps, text content, etc.)

## Notes

- First-time generation will clone the repository and build the tool (may take several minutes)
- Large scale factors (SF≥100) require significant memory and disk space
- Generation time varies: SF=1 takes ~1-2 minutes, SF=100 can take 30+ minutes

## References

- [LDBC SNB Specification](https://ldbcouncil.org/benchmarks/snb/)
- [Datagen Repository](https://github.com/ldbc/ldbc_snb_datagen_spark)
