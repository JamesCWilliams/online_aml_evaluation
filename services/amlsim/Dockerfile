FROM python:3.7-slim-bullseye

# install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    openjdk-11-jdk \ 
    maven \
    graphviz \
    libgraphviz-dev \
    pkg-config \
    gcc \
    libc6-dev \
    wget \
    unzip \
    git \
    git-lfs \
    && rm -rf /var/lib/apt/lists/*

# set up java
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV MAVEN_OPTS="-Dmaven.repo.local=/tmp/.m2/repository"

WORKDIR /amlsim

# set up python
COPY vendor/requirements.txt .
RUN pip install --no-cache-dir "matplotlib>=3.1.2,<3.6" \
    && pip install --no-cache-dir -r requirements.txt

# download and build mason
RUN git clone --depth 1 --branch v20 https://github.com/eclab/mason.git mason-src \
    && cd mason-src \
    && git lfs pull \
    && mvn package -DskipTests -q \
    && cd .. \
    && mvn install:install-file \
        -Dfile=mason-src/mason/target/mason-20.jar \
        -DgroupId=mason \
        -DartifactId=mason \
        -Dversion=20 \
        -Dpackaging=jar \
        -q \
    && rm -rf mason-src/

COPY vendor/ .
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# build java
RUN mvn clean package -DskipTests -q

# declare volumes
VOLUME ["/amlsim/paramFiles", "/amlsim/outputs"]

RUN chmod -R a+rw /tmp/.m2 && chmod -R a+rw /amlsim

ENTRYPOINT ["/amlsim/entrypoint.sh"]
