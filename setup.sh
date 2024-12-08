#!/bin/bash

# Make the script exit on any error
set -e

# Print commands as they are executed
set -x

echo "=============== Checking R installation ==============="
R --version

echo "=============== Installing R packages ==============="
Rscript r_requirements.R

echo "=============== Listing installed R packages ==============="
Rscript -e "installed.packages()"

echo "=============== Testing epidatr installation ==============="
Rscript -e "library(epidatr)"
