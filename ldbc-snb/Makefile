# LDBC Social Network Benchmark Dataset Generator
# Uses official ldbc_snb_datagen_spark from https://github.com/ldbc/ldbc_snb_datagen_spark
#
# Usage:
#   make                    # Generate default scale (SF=1)
#   make SCALE=10           # Generate scale factor 10
#   make SCALE=100          # Generate scale factor 100
#   make clean              # Remove generated files
#   make realclean          # Remove everything including generator

SCALE ?= 1
GRAPH_NAME = ldbc-snb-sf$(SCALE)
DATAGEN_DIR = ldbc_snb_datagen_spark
DATAGEN_REPO = https://github.com/ldbc/ldbc_snb_datagen_spark.git
OUTPUT_DIR = $(GRAPH_NAME)

.PHONY: all setup fetch clean realclean

all: setup

setup: $(OUTPUT_DIR)

# Clone the official LDBC datagen repository (submodule should already exist)
$(DATAGEN_DIR):
	@echo "Initializing LDBC SNB datagen submodule..."
	git submodule update --init --recursive
	@echo "✓ Submodule initialized"

# Generate the dataset using Docker
$(OUTPUT_DIR): $(DATAGEN_DIR) run_datagen_docker.sh Dockerfile
	@echo "Generating LDBC SNB dataset with scale factor $(SCALE)..."
	bash run_datagen_docker.sh $(SCALE) $(OUTPUT_DIR)
	@echo "✓ Dataset generated in $(OUTPUT_DIR)"

fetch: $(DATAGEN_DIR)

clean:
	rm -rf ldbc-snb-sf*

realclean: clean
	docker rmi ldbc-snb-datagen 2>/dev/null || true
	@echo "✓ Cleaned (submodule preserved)"

