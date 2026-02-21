# OSM Road Networks Makefile
# Downloads and converts OpenStreetMap road networks to CSV format using osmnx.
#
# Usage:
#   make                                        # download Singapore (default)
#   make PLACE="Tokyo, Japan"                   # download by place name with spaces
#   make Singapore                              # shorthand for single-word place names
#   make PLACE="Tokyo, Japan" OUTPUT_DIR=tokyo  # custom output subdirectory name
#   make clean PLACE="Tokyo, Japan"             # clean a specific place's output
#   make realclean                              # remove all place subdirectories

PLACE ?= Singapore
OUTPUT_DIR ?=
PLACE_SLUG := $(shell python3 -c "import re, sys; n=sys.argv[1].lower(); n=re.sub(r'[^\w\s-]','',n); n=re.sub(r'[\s]+','_',n.strip()); print(n)" "$(PLACE)")
PLACE_DIR  := $(if $(OUTPUT_DIR),$(OUTPUT_DIR),$(PLACE_SLUG))

.PHONY: all fetch setup clean realclean

all: setup

setup: $(PLACE_DIR)/nodes.csv $(PLACE_DIR)/edges.csv $(PLACE_DIR)/type_meta.json

$(PLACE_DIR)/nodes.csv $(PLACE_DIR)/edges.csv $(PLACE_DIR)/type_meta.json:
	python3 download_convert_osm.py --place "$(PLACE)" --output-dir . --name "$(PLACE_DIR)"

fetch: setup

clean:
	@if [ -d "$(PLACE_DIR)" ]; then \
		rm -f "$(PLACE_DIR)/nodes.csv" "$(PLACE_DIR)/edges.csv" "$(PLACE_DIR)/type_meta.json"; \
		echo "Cleaned: $(PLACE_DIR)/"; \
	fi

realclean:
	rm -rf */

# Shorthand targets: make Singapore, make Tokyo etc. (single-word place names)
%:
	$(MAKE) PLACE="$@"

