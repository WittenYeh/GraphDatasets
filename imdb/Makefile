GRAPH_NAME = imdb

all: setup

setup: nodes.csv edges.csv

# Convert IMDB dataset to CSV format
nodes.csv edges.csv:
	@echo "Downloading and converting $(GRAPH_NAME) dataset to CSV format..."
	python3 download_imdb.py
	@echo "Dataset ready: nodes.csv and edges.csv"

fetch: nodes.csv edges.csv

clean:
	rm -f nodes.csv edges.csv
	@echo "CSV files cleaned"

realclean: clean
	rm -f *.tsv.gz
	@echo "Source archives removed"
