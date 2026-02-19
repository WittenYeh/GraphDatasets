GRAPH_NAME = yelp

all: setup

setup: nodes.csv edges.csv

# Convert Yelp dataset to CSV format
nodes.csv edges.csv:
	@echo "Converting $(GRAPH_NAME) dataset to CSV format..."
	@echo "Note: Dataset must be downloaded manually from https://www.yelp.com/dataset/download"
	python3 download_yelp.py
	@echo "✓ Dataset ready: nodes.csv and edges.csv"

fetch: nodes.csv edges.csv

clean:
	rm -f nodes.csv edges.csv

realclean: clean
	rm -f yelp_academic_dataset_*.json
	@echo "✓ All files cleaned"
