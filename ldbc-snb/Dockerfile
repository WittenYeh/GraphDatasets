FROM eclipse-temurin:11-jdk

# Install sbt and dependencies
RUN apt-get update && \
    apt-get install -y gnupg2 curl wget && \
    echo "deb https://repo.scala-sbt.org/scalasbt/debian all main" | tee /etc/apt/sources.list.d/sbt.list && \
    echo "deb https://repo.scala-sbt.org/scalasbt/debian /" | tee /etc/apt/sources.list.d/sbt_old.list && \
    curl -sL "https://keyserver.ubuntu.com/pks/lookup?op=get&search=0x2EE0EA64E40A89B84B2DF73499E82A75642AC823" | apt-key add && \
    apt-get update && \
    apt-get install -y sbt && \
    rm -rf /var/lib/apt/lists/*

# Install Spark 3.2.2
ENV SPARK_VERSION=3.2.2
ENV HADOOP_VERSION=3.2
ENV SPARK_HOME=/opt/spark
RUN wget -q https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz && \
    tar -xzf spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz && \
    mv spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION} ${SPARK_HOME} && \
    rm spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz

ENV PATH="${SPARK_HOME}/bin:${PATH}"

# Set working directory
WORKDIR /workspace

# Copy the datagen source
COPY ldbc_snb_datagen_spark /workspace/ldbc_snb_datagen_spark

# Build the datagen with 64 parallel threads
WORKDIR /workspace/ldbc_snb_datagen_spark
RUN sbt -J-Xmx8G "set Global / concurrentRestrictions := Seq(Tags.limitAll(64))" assembly

# Set entrypoint
WORKDIR /workspace
ENTRYPOINT ["/bin/bash"]



