"""
Report generator for the load testing tool.

Formats metrics into human-readable reports, generates console output,
and creates file-based reports.
"""

from typing import Dict, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box


class Reporter:
    """Formats metrics into human-readable console output using rich library.
    
    The Reporter class takes metrics statistics and generates formatted output
    including summary statistics, status code distribution, and performance metrics.
    """
    
    def __init__(self, console: Console = None):
        """Initialize the reporter.
        
        Args:
            console: Rich Console instance for output (creates new if None)
        """
        self.console = console or Console()
    
    def generate_report(self, statistics: Dict[str, Any]) -> None:
        """Generate and print a complete report from statistics.
        
        Args:
            statistics: Dictionary containing test statistics with keys:
                - total_requests: Total number of requests
                - successful_requests: Number of successful requests
                - failed_requests: Number of failed requests
                - error_rate: Error rate as percentage
                - response_times: Dict with min, max, mean, median, p95, p99
                - throughput: Requests per second
                - duration: Total test duration in seconds
                - status_codes: Dict mapping status codes to counts
        """
        self.console.print()
        self._print_summary(statistics)
        self.console.print()
        self._print_response_times(statistics)
        self.console.print()
        self._print_status_codes(statistics)
        self.console.print()
    
    def _print_summary(self, statistics: Dict[str, Any]) -> None:
        """Print summary statistics panel.
        
        Args:
            statistics: Statistics dictionary
        """
        total = statistics.get('total_requests', 0)
        successful = statistics.get('successful_requests', 0)
        failed = statistics.get('failed_requests', 0)
        error_rate = statistics.get('error_rate', 0.0)
        throughput = statistics.get('throughput', 0.0)
        duration = statistics.get('duration', 0.0)
        
        summary_text = (
            f"[bold]Total Requests:[/bold] {total}\n"
            f"[bold]Successful:[/bold] [green]{successful}[/green]\n"
            f"[bold]Failed:[/bold] [red]{failed}[/red]\n"
            f"[bold]Error Rate:[/bold] {error_rate:.2f}%\n"
            f"[bold]Duration:[/bold] {duration:.2f}s\n"
            f"[bold]Throughput:[/bold] {throughput:.2f} req/s"
        )
        
        panel = Panel(
            summary_text,
            title="[bold cyan]Summary Statistics[/bold cyan]",
            border_style="cyan",
            box=box.ROUNDED
        )
        self.console.print(panel)
    
    def _print_response_times(self, statistics: Dict[str, Any]) -> None:
        """Print response time statistics table.
        
        Args:
            statistics: Statistics dictionary
        """
        response_times = statistics.get('response_times', {})
        
        table = Table(
            title="[bold cyan]Response Time Statistics[/bold cyan]",
            box=box.ROUNDED,
            border_style="cyan"
        )
        
        table.add_column("Metric", style="bold")
        table.add_column("Value (ms)", justify="right", style="green")
        
        metrics_order = ['min', 'mean', 'median', 'p95', 'p99', 'max']
        metric_labels = {
            'min': 'Minimum',
            'mean': 'Mean',
            'median': 'Median',
            'p95': '95th Percentile',
            'p99': '99th Percentile',
            'max': 'Maximum'
        }
        
        for metric in metrics_order:
            value = response_times.get(metric, 0.0)
            label = metric_labels.get(metric, metric)
            # Convert seconds to milliseconds
            table.add_row(label, f"{value * 1000:.2f}")
        
        self.console.print(table)
    
    def _print_status_codes(self, statistics: Dict[str, Any]) -> None:
        """Print status code distribution table.
        
        Args:
            statistics: Statistics dictionary
        """
        status_codes = statistics.get('status_codes', {})
        
        if not status_codes:
            return
        
        table = Table(
            title="[bold cyan]Status Code Distribution[/bold cyan]",
            box=box.ROUNDED,
            border_style="cyan"
        )
        
        table.add_column("Status Code", style="bold")
        table.add_column("Count", justify="right")
        table.add_column("Percentage", justify="right")
        
        total = sum(status_codes.values())
        
        # Sort by status code
        for status_code in sorted(status_codes.keys()):
            count = status_codes[status_code]
            percentage = (count / total * 100) if total > 0 else 0.0
            
            # Color code based on status code range
            if 200 <= status_code < 300:
                status_style = "[green]"
            elif 300 <= status_code < 400:
                status_style = "[yellow]"
            elif 400 <= status_code < 500:
                status_style = "[orange1]"
            else:
                status_style = "[red]"
            
            table.add_row(
                f"{status_style}{status_code}[/]",
                f"{count}",
                f"{percentage:.1f}%"
            )
        
        self.console.print(table)
