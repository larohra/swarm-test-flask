"""
CLI interface for the load testing tool.

Handles command-line argument parsing and user-friendly interface for running tests.
"""
import json
import click
from typing import Optional, Dict

from loadtest.config import Config, ConfigError


def parse_headers(ctx, param, value):
    """Parse header arguments into a dictionary.
    
    Args:
        ctx: Click context
        param: Click parameter
        value: Tuple of header strings in format "Key: Value"
        
    Returns:
        Dictionary of headers
        
    Raises:
        click.BadParameter: If header format is invalid
    """
    if not value:
        return {}
    
    headers = {}
    for header in value:
        if ':' not in header:
            raise click.BadParameter(
                f"Invalid header format '{header}'. "
                "Headers must be in format 'Key: Value'"
            )
        
        key, _, val = header.partition(':')
        key = key.strip()
        val = val.strip()
        
        if not key:
            raise click.BadParameter(
                f"Invalid header format '{header}'. "
                "Header name cannot be empty"
            )
        
        headers[key] = val
    
    return headers


@click.command()
@click.option(
    '--config',
    type=click.Path(exists=True),
    help='Path to YAML configuration file. CLI arguments override file values.'
)
@click.option(
    '--url', '-u',
    help='Target URL for load testing. Must include scheme (http:// or https://). Required if --config is not provided.'
)
@click.option(
    '--method', '-m',
    help='HTTP method to use (default: GET). Valid: GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS.'
)
@click.option(
    '--requests', '-n',
    type=int,
    help='Number of requests to send (default: 100).'
)
@click.option(
    '--concurrency', '-c',
    type=int,
    help='Number of concurrent requests (default: 10). Cannot exceed total requests.'
)
@click.option(
    '--timeout', '-t',
    type=int,
    help='Request timeout in seconds (default: 30).'
)
@click.option(
    '--header', '-H',
    multiple=True,
    callback=parse_headers,
    help='Custom HTTP header in format "Key: Value". Can be specified multiple times.'
)
@click.option(
    '--data', '-d',
    default=None,
    help='Request body data. Typically used with POST/PUT requests.'
)
@click.option(
    '--output', '-o',
    default=None,
    type=click.Path(),
    help='Output file path for saving the report. If not specified, prints to console.'
)
def cli(
    config: Optional[str],
    url: Optional[str],
    method: Optional[str],
    requests: Optional[int],
    concurrency: Optional[int],
    timeout: Optional[int],
    header: Dict[str, str],
    data: Optional[str],
    output: Optional[str]
) -> Config:
    """Load testing tool for HTTP/HTTPS endpoints.
    
    This tool simulates concurrent users making requests to web services,
    measures performance metrics, and generates detailed reports.
    
    Examples:
    
      # Basic usage
      loadtest --url http://localhost:5000/health --requests 100 --concurrency 10
    
      # POST request with headers and body
      loadtest -u http://localhost:5000/api/items -m POST \\
        -H "Content-Type: application/json" \\
        -d '{"name": "test", "description": "test"}' \\
        -n 50 -c 5
    
      # Using config file
      loadtest --config loadtest.yaml
    
      # Using config file with CLI overrides
      loadtest --config loadtest.yaml --requests 200 --concurrency 20
    
      # Save report to file
      loadtest -u http://localhost:5000/health -n 100 -o report.json
    """
    try:
        # If config file is provided, load it and merge with CLI args
        if config:
            file_config = Config.from_yaml_file(config)
            
            # Merge CLI overrides (only non-None values override file config)
            config_obj = Config.merge(
                file_config,
                url=url,
                method=method,
                requests=requests,
                concurrency=concurrency,
                timeout=timeout,
                headers=header if header else None,
                body=data
            )
        else:
            # No config file, URL is required from CLI
            if not url:
                raise click.BadParameter(
                    "Either --config file or --url must be provided"
                )
            
            # Create Config object with CLI parameters only
            config_obj = Config(
                url=url,
                method=method,
                requests=requests,
                concurrency=concurrency,
                timeout=timeout,
                headers=header,
                body=data
            )
        
        # Store output file path in context for later use
        ctx = click.get_current_context()
        ctx.obj = {'config': config_obj, 'output': output}
        
        return config_obj
        
    except ConfigError as e:
        raise click.BadParameter(str(e))


if __name__ == '__main__':
    cli()
