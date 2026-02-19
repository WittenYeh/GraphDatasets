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

# Check if we need to build
if [ ! -f "target/ldbc_snb_datagen-*-jar-with-dependencies.jar" ]; then
    echo "Building datagen (first time only)..."
    if command -v mvn &> /dev/null; then
        mvn clean package -DskipTests
    else
        echo "Error: Maven not found. Please install Maven to build the datagen."
        exit 1
    fi
fi

# Create params directory if it doesn't exist
mkdir -p params

# Generate params file for the specified scale
cat > params/params-sf${SCALE}.ini << EOF
# LDBC SNB Data Generator Parameters
# Scale Factor: ${SCALE}

ldbc.snb.datagen.generator.scaleFactor:snb.interactive.${SCALE}

# Output format
ldbc.snb.datagen.serializer.outputDir:../$(basename ${OUTPUT_DIR})
ldbc.snb.datagen.serializer.dynamicActivitySerializer:ldbc.snb.datagen.serializer.snb.csv.dynamicserializer.activity.CsvMergeForeignDynamicActivitySerializer
ldbc.snb.datagen.serializer.dynamicPersonSerializer:ldbc.snb.datagen.serializer.snb.csv.dynamicserializer.person.CsvMergeForeignDynamicPersonSerializer
ldbc.snb.datagen.serializer.staticSerializer:ldbc.snb.datagen.serializer.snb.csv.staticserializer.CsvMergeForeignStaticSerializer

# Generator options
ldbc.snb.datagen.generator.numThreads:4
ldbc.snb.datagen.generator.numUpdatePartitions:1

# Hadoop options
ldbc.snb.datagen.hadoop.numThreads:4
EOF

echo "✓ Generated params file: params/params-sf${SCALE}.ini"

# Run the generator
echo ""
echo "Running datagen (this may take a while for large scale factors)..."

# Find the jar file
JAR_FILE=$(ls target/ldbc_snb_datagen-*-jar-with-dependencies.jar | head -1)

if [ -z "${JAR_FILE}" ]; then
    echo "Error: Could not find datagen jar file"
    exit 1
fi

# Run with Hadoop (if available) or standalone
if command -v hadoop &> /dev/null; then
    echo "Using Hadoop mode..."
    hadoop jar ${JAR_FILE} params/params-sf${SCALE}.ini
else
    echo "Using standalone mode (Hadoop not found)..."
    java -cp ${JAR_FILE} ldbc.snb.datagen.LdbcDatagen params/params-sf${SCALE}.ini
fi

cd ..

echo ""
echo "✓ Data generation complete!"
echo "Output directory: ${OUTPUT_DIR}"
