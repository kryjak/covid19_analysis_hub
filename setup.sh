#!/bin/bash

# Make the script exit on any error
set -e

# Print commands as they are executed
set -x

echo "=============== Installing system dependencies ==============="
apt-get update && apt-get install -y \
    r-base \
    r-base-dev \
    libcurl4-openssl-dev \
    libssl-dev \
    libxml2-dev

echo "=============== Installing Delphi R packages ==============="
# First install devtools as it's needed for some dependencies
R -e "install.packages('devtools', repos='https://cloud.r-project.org/')"

# Install all required Delphi packages
R -e "install.packages(c('epidatr', 'epiprocess', 'epidatasets', 'epipredict'), repos=c('https://cmu-delphi.github.io/delphi.github.io/r', 'https://cloud.r-project.org/'), dependencies=TRUE)"

echo "=============== Verifying installations ==============="
R -e "library(epidatr); library(epiprocess); library(epidatasets); library(epipredict)"
