GRAPH_NAME = ogbn-products
OGB_DATA_DIR = ogbn_products

all: setup

setup: nodes.csv edges.csv

# Download raw dataset using OGB official loader
$(OGB_DATA_DIR):
	@echo "Downloading $(GRAPH_NAME) dataset using OGB loader..."
	@if ! python3 -c "import ogb" 2>/dev/null; then \
		echo "Error: ogb library not found. Installing..."; \
		pip install ogb; \
	fi
	python3 download_ogb.py
	@echo "Download complete."

# Convert to CSV
nodes.csv edges.csv: $(OGB_DATA_DIR)
	@echo "Converting $(GRAPH_NAME) dataset to CSV format..."
	python3 convert_ogb.py
	@echo "Dataset ready: nodes.csv and edges.csv"

fetch: $(OGB_DATA_DIR)

clean:
	rm -f nodes.csv edges.csv

realclean: clean
	rm -rf $(OGB_DATA_DIR)
	@echo "All files cleaned"
