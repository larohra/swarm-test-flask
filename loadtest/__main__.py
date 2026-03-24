"""
Main entry point for the load testing tool.

Coordinates all components and orchestrates test execution flow:
1. Parse CLI arguments using click-based CLI
2. Create and validate configuration
3. Initialize async HTTP engine
4. Execute load test with real-time progress display
5. Collect and calculate metrics
6. Generate formatted report
7. Optionally save results to file

Usage:
    python -m loadtest --url http://example.com --requests 100 --concurrency 10
    
The module integrates:
- CLI: Command-line argument parsing (click)
- Config: Parameter validation and management
- Engine: Async HTTP request execution (aiohttp)
- Metrics: Statistics collection and calculation
- Reporter: Formatted output generation (rich)
"""
import asyncio
import sys
from typing import Optional

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn

from loadtest.cli import cli as cli_command
from loadtest.config import Config
from loadtest.engine import Engine
from loadtest.metrics import MetricsCollector
from loadtest.reporter import Reporter


async def run_load_test(config: Config, console: Console) -> MetricsCollector:
    """Execute the load test with progress display.
    
    Args:
        config: Configuration object with test parameters
        console: Rich console for output
        
    Returns:
        MetricsCollector with test results
    """
    # Initialize components
    engine = Engine(
        url=config.url,
        method=config.method,
        timeout=config.timeout,
        headers=config.headers,
        body=config.body
    )
    
    metrics = MetricsCollector()
    
    # Display test configuration
    console.print()
    console.print(f"[bold cyan]Starting load test...[/bold cyan]")
    console.print(f"  URL: [bold]{config.url}[/bold]")
    console.print(f"  Method: [bold]{config.method}[/bold]")
    console.print(f"  Requests: [bold]{config.requests}[/bold]")
    console.print(f"  Concurrency: [bold]{config.concurrency}[/bold]")
    console.print()
    
    # Start metrics collection
    metrics.start()
    
    # Execute requests with progress display
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeRemainingColumn(),
        console=console
    ) as progress:
        task = progress.add_task(
            "[cyan]Executing requests...",
            total=config.requests
        )
        
        # Run the engine and get results
        results = await engine.run(config.requests, config.concurrency)
        
        # Update progress to completion
        progress.update(task, completed=config.requests)
        
        # Add results to metrics collector
        for result in results:
            metrics.add_result(result)
    
    # End metrics collection
    metrics.end()
    
    return metrics


def main():
    """Main entry point for the load testing tool."""
    console = Console()
    
    try:
        # Parse CLI arguments
        ctx = cli_command.make_context('loadtest', sys.argv[1:])
        
        # Get config and output path from context
        config = ctx.obj.get('config')
        output_path = ctx.obj.get('output')
        
        # Run the load test
        metrics = asyncio.run(run_load_test(config, console))
        
        # Generate statistics
        statistics = metrics.get_statistics()
        
        # Generate report
        reporter = Reporter(console=console)
        reporter.generate_report(statistics)
        
        # Optionally save report to file
        if output_path:
            import json
            with open(output_path, 'w') as f:
                json.dump(statistics, f, indent=2)
            console.print(f"[green]Report saved to {output_path}[/green]")
            console.print()
        
        # Exit with appropriate code based on results
        if statistics.get('failed_requests', 0) > 0:
            sys.exit(1)
        else:
            sys.exit(0)
            
    except click.ClickException as e:
        # Click will handle its own exceptions
        e.show()
        sys.exit(1)
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Load test interrupted by user[/yellow]")
        sys.exit(130)
        
    except Exception as e:
        console.print(f"\n[red]Error: {str(e)}[/red]")
        if '--debug' in sys.argv:
            raise
        sys.exit(1)


if __name__ == "__main__":
    main()
