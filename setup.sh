#!/bin/bash

# Make the script exit on any error
set -e

# Print commands as they are executed
set -x

# Check R installation
R --version

# Run R requirements and save output to a log file
Rscript r_requirements.R 2>&1 | tee r_install.log

# List installed R packages
Rscript -e "installed.packages()" 2>&1 | tee installed_packages.log

# Try to load epidatr specifically
Rscript -e "library(epidatr)" 2>&1 | tee epidatr_test.log
