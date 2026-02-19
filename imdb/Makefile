GRAPH_NAME = imdb
IMDB_URL = https://datasets.imdbws.com

TSV_GZ_FILES = name.basics.tsv.gz title.basics.tsv.gz title.principals.tsv.gz title.ratings.tsv.gz
TSV_FILES = $(TSV_GZ_FILES:.tsv.gz=.tsv)

all: setup

setup: nodes.csv edges.csv

# Download .tsv.gz files
%.tsv.gz:
	wget -N $(IMDB_URL)/$@

# Decompress .tsv.gz -> .tsv
%.tsv: %.tsv.gz
	gunzip -k $<

# Convert to graph CSV
nodes.csv edges.csv: $(TSV_FILES)
	@echo "Converting $(GRAPH_NAME) dataset to CSV format..."
	python3 download_imdb.py
	@echo "Dataset ready: nodes.csv and edges.csv"

fetch: $(TSV_GZ_FILES)

clean:
	rm -f nodes.csv edges.csv $(TSV_FILES)
	@echo "CSV and TSV files cleaned"

realclean: clean
	rm -f $(TSV_GZ_FILES)
	@echo "Source archives removed"
