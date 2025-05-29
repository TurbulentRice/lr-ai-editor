# syntax=docker/dockerfile:1

###############################################################################
# Serve service Dockerfile
# Runs the FastAPI inference micro-service that predicts Lightroom sliders.   #
#                                                                             #
# Swap BASE_IMAGE to a CUDA runtime if you want GPU inference:                #
#   docker-compose up --build serve --build-arg BASE_IMAGE=pytorch/pytorch:2.2.0-cuda12.1-cudnn8-runtime
###############################################################################
ARG BASE_IMAGE=python:3.11-slim

# Build the UI
FROM node:20-alpine AS ui-builder
WORKDIR /app/ui
COPY ui/package.json ui/package-lock.json ./
RUN npm ci
COPY ui/ .
RUN npm run build

# Build the server
FROM ${BASE_IMAGE} AS builder

# Prevent Python from writing .pyc files and enable unbuffered stdout/err
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# ---------- System dependencies (only what we need) -------------------------
RUN apt-get update \
 && apt-get install -y --no-install-recommends gcc \
 && rm -rf /var/lib/apt/lists/*

# ---------- Python dependencies --------------------------------------------
# Copy first to leverage layer caching
COPY serve/requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
&& pip install --no-cache-dir -r requirements.txt

# ---------- Application code ------------------------------------------------
COPY --from=ui-builder /app/ui/dist /app/ui/dist
COPY common/ /app/common/
COPY serve/app.py .

# ---------- Network ---------------------------------------------------------
EXPOSE 8000

# ---------- Entrypoint ------------------------------------------------------
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
