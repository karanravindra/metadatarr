# metadatarr

A tool for managing and enriching metadata using qBittorrent. This tool automatically downloads metadata for torrents that are missing it.

## Features

- Monitors qBittorrent for torrents missing metadata
- Automatically starts download to fetch metadata
- Stops download once metadata is acquired
- Configurable check intervals
- Docker support with GitHub Container Registry publishing

## Configuration

Copy `.env.example` to `.env` and configure:

```bash
HOST=192.168.2.51      # qBittorrent host
PORT=8080              # qBittorrent port
USERNAME=admin         # qBittorrent username
PASSWORD=password      # qBittorrent password
INTERVAL=60           # Check interval in seconds
```

## Usage

### Local Development

```bash
# Install dependencies
uv sync

# Run the application
python main.py
```

### Docker

#### Using GitHub Container Registry

```bash
# Pull and run the latest image
docker run -d \
  --name metadatarr \
  --env-file .env \
  ghcr.io/username/metadatarr:latest
```

#### Building locally

```bash
# Build the image
docker build -t metadatarr .

# Run the container
docker run -d \
  --name metadatarr \
  --env-file .env \
  metadatarr
```

## Docker Publishing

This project automatically publishes Docker images to GitHub Container Registry via GitHub Actions:

- **On main branch push**: Tagged as `latest`
- **On version tags** (v1.0.0): Tagged with version numbers
- **On pull requests**: Tagged with PR number

The workflow requires no additional setup - it uses the built-in `GITHUB_TOKEN` for authentication.

## Requirements

- Python 3.13+
- qBittorrent with Web UI enabled
- Docker (optional)
