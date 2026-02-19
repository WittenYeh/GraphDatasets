#!/bin/bash
# Script to run LDBC SNB datagen with specified scale factor
# Usage: ./run_datagen.sh <scale_factor> <output_dir>

set -e

SCALE=${1:-1}
OUTPUT_DIR=${2:-ldbc-snb-sf${SCALE}}
DATAGEN_DIR="ldbc_snb_datagen_spark"

echo "=== LDBC SNB Data Generator ==="
echo "Scale Factor: ${SCALE}"
echo "Output Directory: ${OUTPUT_DIR}"
echo ""

# Check if datagen directory exists
if [ ! -d "${DATAGEN_DIR}" ]; then
    echo "Error: ${DATAGEN_DIR} not found. Run 'make fetch' first."
    exit 1
fi

cd "${DATAGEN_DIR}"

# Check if we need to build (using sbt)
if [ ! -d "target/scala-2.12" ] || [ ! -f "target/scala-2.12/ldbc_snb_datagen*.jar" ]; then
    echo "Building datagen with sbt (first time only)..."
    if command -v sbt &> /dev/null; then
        sbt assembly
    else
        echo "Error: sbt not found. Please install sbt to build the datagen."
        echo "Visit: https://www.scala-sbt.org/download.html"
        exit 1
    fi
fi

# Find the assembled jar file
JAR_FILE=$(ls target/scala-2.12/ldbc_snb_datagen-assembly-*.jar 2>/dev/null | head -1)

if [ -z "${JAR_FILE}" ]; then
    echo "Error: Could not find assembled jar file"
    exit 1
fi

echo "✓ Found jar: ${JAR_FILE}"

# Run the generator using the scripts provided
echo ""
echo "Running datagen (this may take a while for large scale factors)..."

# Use the provided run script
if [ -f "tools/run.sh" ]; then
    echo "Using tools/run.sh..."
    bash tools/run.sh --scale-factor ${SCALE} --output-dir ../${OUTPUT_DIR}
else
    # Fallback to direct java execution
    echo "Using direct java execution..."
    java -Xmx4G -jar ${JAR_FILE} \
        --scale-factor ${SCALE} \
        --output-dir ../${OUTPUT_DIR} \
        --format csv \
        --mode raw
fi

cd ..

echo ""
echo "✓ Data generation complete!"
echo "Output directory: ${OUTPUT_DIR}"

