# Use Ubuntu 24.04 (Noble) base image
FROM ubuntu:24.04

# Avoid timezone prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies including python3-rpy2
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-dev \
    python3-venv \
    r-base \
    r-base-dev \
    libcurl4-openssl-dev \
    libssl-dev \
    libxml2-dev \
    git \
    build-essential \
    python3-setuptools \
    python3-rpy2 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Create and activate virtual environment with access to system packages
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV --system-site-packages
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install Python dependencies (excluding rpy2 since we installed it via apt)
COPY requirements.txt .
RUN grep -v "rpy2" requirements.txt > requirements_no_rpy2.txt && \
    pip install --no-cache-dir -r requirements_no_rpy2.txt

# Install R packages
RUN R -e '\
    install.packages(c("remotes", "devtools"), repos="https://cloud.r-project.org/"); \
    remotes::install_github("cmu-delphi/epidatr@main"); \
    remotes::install_github("cmu-delphi/epidatasets@main"); \
    remotes::install_github("cmu-delphi/epiprocess@main"); \
    remotes::install_github("cmu-delphi/epipredict@main"); \
    if (!require("epidatr")) stop("epidatr package not installed correctly")'

# Copy application files
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Command to run the application
CMD ["streamlit", "run", "Home.py", "--server.address=0.0.0.0"]