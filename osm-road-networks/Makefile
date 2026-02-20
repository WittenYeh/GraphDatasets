# OSM Road Networks Makefile
# Downloads and converts OpenStreetMap road networks to CSV format using osmnx.
#
# Usage:
#   make                              # download Pasadena, CA (default)
#   make PLACE="Beijing, China"       # download a specific city
#   make clean PLACE="Beijing, China" # clean a specific city's output
#   make realclean                    # remove all city subdirectories

PLACE ?= Pasadena, California, USA
CITY_SLUG := $(shell python3 -c "import re, sys; n=sys.argv[1].lower(); n=re.sub(r'[^\w\s-]','',n); n=re.sub(r'[\s]+','_',n.strip()); print(n)" "$(PLACE)")
CITY_DIR  := $(CITY_SLUG)

.PHONY: all fetch setup clean realclean

all: setup

setup: $(CITY_DIR)/nodes.csv $(CITY_DIR)/edges.csv

$(CITY_DIR)/nodes.csv $(CITY_DIR)/edges.csv:
	@echo "Downloading OSM road network for: $(PLACE)"
	python3 download_convert_osm.py --place "$(PLACE)" --output-dir .
	@echo "✓ Dataset ready: $(CITY_DIR)/nodes.csv and $(CITY_DIR)/edges.csv"

fetch: setup

clean:
	@if [ -d "$(CITY_DIR)" ]; then \
		rm -f "$(CITY_DIR)/nodes.csv" "$(CITY_DIR)/edges.csv"; \
		echo "✓ Cleaned CSV files for: $(PLACE)"; \
	fi

realclean:
	rm -rf */
	@echo "✓ Removed all city subdirectories"
