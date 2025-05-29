# syntax=docker/dockerfile:1

###############################################################################
# UI service Dockerfile
# 1. Build front‑end (React/Vite/Next) in a multi‑arch Node image
# 2. Copy the static bundle into a minimal Nginx runtime image
#
# Adjust the build command if you’re not using Vite/React.
###############################################################################

########## 1. Build stage #####################################################
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package metadata and install dependencies
COPY package.json package-lock.json ./
RUN npm ci

# Copy source files
COPY src/ ./src
COPY public/ ./public
COPY index.html ./
COPY docker/nginx.conf ./docker/nginx.conf

# Build the production bundle (change to `next build` if you use Next.js)
RUN npm run build

########## 2. Runtime stage ###################################################
FROM nginx:1.25-alpine

# Copy build output to Nginx html directory
COPY --from=builder /app/dist /usr/share/nginx/html

# Remove default Nginx config & drop in a tiny one with gzip + caching
RUN rm /etc/nginx/conf.d/default.conf
COPY --from=builder /app/docker/nginx.conf /etc/nginx/conf.d/app.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]





