# syntax=docker/dockerfile:1

###############################################################################
# Train service Dockerfile
# Builds a container that trains the Lightroom-style model and drops the       #
# resulting checkpoint into the shared /mnt/models volume.                     #
#                                                                              #
# A build-arg lets you switch between CPU-only and CUDA base images:           #
#   docker compose build train --build-arg BASE_IMAGE=pytorch/pytorch:2.2.0-cuda12.1-cudnn8-runtime
###############################################################################

# ------- 1. Choose a base image (default = CPU-only) -------------------------
# ARG BASE_IMAGE=pytorch/pytorch:2.7.0-cuda12.8-cudnn9-runtime
ARG BASE_IMAGE=armswdev/pytorch-arm-neoverse:r24.07-torch-2.3.0-openblas
FROM ${BASE_IMAGE}

# ------- 2. System setup -----------------------------------------------------
# Reduce image size and make Python behave well in containers
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# ------- Python dependencies ---------------------------------------------
# Copy requirements early to leverage Docker layer caching
COPY train/requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# ------- Training code ----------------------------------------------
COPY common/ /app/common/
COPY train/train.py .
# If you later add a src/ package or data augmentation utils, copy that too:
# COPY src/ ./src

# ------- 5. Entry point ------------------------------------------------------
ENTRYPOINT ["python", "train.py"]
