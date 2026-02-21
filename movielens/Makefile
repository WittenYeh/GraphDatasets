GRAPH_NAME = movielens
ZIP_URL = https://files.grouplens.org/datasets/movielens/ml-latest.zip
ZIP_FILE = ml-latest.zip
DATA_DIR = ml-latest
CONVERT_SCRIPT = ../movielens-small/convert_movielens.py

all: setup

setup: nodes.csv edges.csv

$(ZIP_FILE):
	wget -N $(ZIP_URL)

$(DATA_DIR): $(ZIP_FILE)
	unzip -o $(ZIP_FILE)

nodes.csv edges.csv: $(DATA_DIR)
	@echo "Converting $(GRAPH_NAME) dataset to CSV format..."
	python3 $(CONVERT_SCRIPT) $(DATA_DIR)
	@echo "Dataset ready: nodes.csv, edges.csv, and type_meta.json"

fetch: $(ZIP_FILE)

clean:
	rm -f nodes.csv edges.csv
	rm -rf $(DATA_DIR)
	@echo "CSV files and extracted data cleaned"

realclean: clean
	rm -f $(ZIP_FILE)
	@echo "Source archive removed"
