GRAPH_NAME = ogbn-products

all: setup

setup: nodes.csv edges.csv

# Download and convert using OGB official loader
nodes.csv edges.csv:
	@echo "Downloading $(GRAPH_NAME) dataset using OGB loader..."
	@if ! python3 -c "import ogb" 2>/dev/null; then \
		echo "Error: ogb library not found. Installing..."; \
		pip install ogb; \
	fi
	python3 download_ogb.py
	@echo "✓ Dataset ready: nodes.csv and edges.csv"

fetch: nodes.csv edges.csv

clean:
	rm -f nodes.csv edges.csv
	rm -rf ./ogbn_products/

realclean: clean
	rm -rf ogbn_products_pyg ogbn_products_dgl
	@echo "✓ All files cleaned"
