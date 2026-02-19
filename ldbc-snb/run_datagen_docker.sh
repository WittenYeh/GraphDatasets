#!/bin/bash
# Script to run LDBC SNB datagen in Docker
# Usage: ./run_datagen_docker.sh <scale_factor> <output_dir>

set -e

SCALE=${1:-1}
OUTPUT_DIR=${2:-ldbc-snb-sf${SCALE}}
IMAGE_NAME="ldbc-snb-datagen"

echo "=== LDBC SNB Data Generator (Docker) ==="
echo "Scale Factor: ${SCALE}"
echo "Output Directory: ${OUTPUT_DIR}"
echo ""

# Build Docker image if it doesn't exist
if ! docker images | grep -q "${IMAGE_NAME}"; then
    echo "Building Docker image (first time only, may take several minutes)..."
    docker build -t ${IMAGE_NAME} .
    echo "✓ Docker image built"
fi

# Create output directory
mkdir -p "${OUTPUT_DIR}"

# Get absolute path
OUTPUT_ABS=$(cd "${OUTPUT_DIR}" && pwd)

echo ""
echo "Running datagen in Docker..."
echo "Output will be saved to: ${OUTPUT_ABS}"

# Run the generator using Spark submit with HOME set
docker run --rm \
    -e HOME=/tmp \
    -v "${OUTPUT_ABS}:/workspace/output" \
    ${IMAGE_NAME} \
    -c "cd /workspace/ldbc_snb_datagen_spark && \
        JAR=\$(ls target/*-jar-with-dependencies.jar) && \
        spark-submit --class ldbc.snb.datagen.LdbcDatagen \
        --master 'local[*]' \
        --driver-memory 4G \
        \$JAR \
        --scale-factor ${SCALE} \
        --output-dir /workspace/output"

echo ""
echo "✓ Data generation complete!"
echo "Output directory: ${OUTPUT_DIR}"









