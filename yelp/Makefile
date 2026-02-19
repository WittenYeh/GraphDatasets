GRAPH_NAME = yelp

all: setup

setup: nodes.csv edges.csv

# Convert Yelp dataset to CSV format
nodes.csv edges.csv:
	@echo "Downloading and converting $(GRAPH_NAME) dataset to CSV format..."
	python3 download_yelp.py
	@echo "✓ Dataset ready: nodes.csv and edges.csv"

fetch: nodes.csv edges.csv

clean:
	rm -f yelp_academic_dataset_*.json Yelp-JSON.zip
	@echo "✓ CSV files cleaned, JSON zip removed"
