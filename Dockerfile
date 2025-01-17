# Use a base image with Conda pre-installed
FROM continuumio/miniconda3

# Set the working directory
WORKDIR /app

# Copy the environment file into the container
COPY . .

# Create the Conda environment inside the container
RUN conda env create -f install_reqs.yml

# Activate the Conda environment
SHELL ["conda", "run", "-n", "env_lisa_premerger", "/bin/bash", "-c"]
