# 🐍 Ekans

A FastAPI-based system monitoring API that provides health checks and system metrics endpoints.

## Features

- System health monitoring
  - Disk space usage
  - Memory utilization
  - Component status checks
- System information
  - OS details
  - Python environment
  - CPU information
  - Memory statistics
- Real-time metrics
  - System uptime
  - CPU usage (total and per-core)
  - Memory utilization
  - Disk I/O statistics
  - Network metrics

## Requirements

- Python 3.12+
- Poetry for dependency management

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ekans.git
   cd ekans
   ```

2. Install dependencies using Poetry:
   ```bash
   poetry install
   ```

## Usage

1. Start the server:
   ```bash
   poetry run python -m app.main
   ```
   The server will start on `http://localhost:8000`

2. Access the API documentation at:
   - Swagger UI: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Health Check
