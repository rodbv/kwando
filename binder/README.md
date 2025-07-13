# Binder Configuration for KWANDO

This directory contains the configuration files needed to run KWANDO on [Binder](https://mybinder.org/).

## Files

- `environment.yml`: Defines the conda environment with all required dependencies
- `postBuild`: Script that runs after the environment is built to start the Panel dashboard
- `start`: Alternative start script for manual launch

## How it works

1. When someone visits the Binder URL, Binder creates a new environment based on `environment.yml`
2. After the environment is ready, `postBuild` automatically starts the Panel dashboard
3. The dashboard runs on port 8888 and is accessible via the Binder proxy

## Usage

1. Push your code to GitHub
2. Update the Binder URL in the main README files with your GitHub username
3. Share the Binder URL with others

## Local Testing

To test the Binder setup locally:

```bash
# Install conda if you don't have it
conda env create -f binder/environment.yml
conda activate kwando
./binder/start
```

## Troubleshooting

- Make sure all dependencies are listed in `environment.yml`
- The Panel dashboard must be configured to run on port 8888 for Binder
- Use `--address 0.0.0.0` to allow external connections
- Use `--allow-websocket-origin=*` to allow Binder's proxy
