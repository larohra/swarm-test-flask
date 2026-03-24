# Load Testing Tool

A Python-based HTTP load testing tool that simulates concurrent users making requests to web services, measures performance metrics, and generates detailed reports. Perfect for testing the performance and reliability of your HTTP/HTTPS endpoints.

## Features

- 🚀 **Concurrent Request Execution**: Simulate multiple users with configurable concurrency levels
- 📊 **Comprehensive Metrics**: Track response times, throughput, error rates, and status code distribution
- 🎨 **Beautiful Reports**: Rich, color-coded console output with tables and progress indicators
- 🔧 **Flexible Configuration**: Configure via CLI arguments or YAML configuration files
- 💾 **Export Results**: Save detailed reports in JSON format for further analysis
- 🌐 **Full HTTP Support**: Support for GET, POST, PUT, DELETE, PATCH, HEAD, and OPTIONS methods
- 🔐 **Custom Headers**: Add authentication tokens, content types, and other custom headers
- ⚡ **Async Architecture**: Built on aiohttp for efficient concurrent request handling

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
  - [Command Line Interface](#command-line-interface)
  - [Configuration File](#configuration-file)
- [CLI Options](#cli-options)
- [Examples](#examples)
- [Interpreting Results](#interpreting-results)
- [Advanced Usage](#advanced-usage)
- [Testing](#testing)

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Install Dependencies

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

   This will install:
   - `flask>=2.0` - Web framework (for the sample API)
   - `aiohttp>=3.8.0` - Async HTTP client
   - `click>=8.0.0` - CLI framework
   - `rich>=13.0.0` - Terminal formatting
   - `pytest>=7.0` - Testing framework
   - `pytest-asyncio>=0.21.0` - Async test support
   - `pyyaml>=6.0` - YAML parsing

## Quick Start

Get started with load testing in under 1 minute!

### 1. Start the Sample Flask API

```bash
python app.py
```

This starts a simple Flask API on `http://localhost:5000` with the following endpoints:
- `/health` - Health check endpoint
- `/api/items` - GET/POST endpoint for items

### 2. Run Your First Load Test

In a new terminal, run a basic load test against the health endpoint:

```bash
python -m loadtest --url http://localhost:5000/health --requests 100 --concurrency 10
```

You'll see a real-time progress bar followed by a detailed report showing:
- Success/failure rates
- Response time statistics (min, max, mean, percentiles)
- Throughput (requests per second)
- Status code distribution

That's it! You're now load testing! 🎉

## Usage

### Command Line Interface

The simplest way to run a load test is using CLI arguments:

```bash
python -m loadtest --url <target-url> [options]
```

**Basic example:**
```bash
python -m loadtest --url http://localhost:5000/health --requests 100 --concurrency 10
```

**With custom headers and POST data:**
```bash
python -m loadtest \
  --url http://localhost:5000/api/items \
  --method POST \
  --header "Content-Type: application/json" \
  --data '{"name": "test", "description": "Load test item"}' \
  --requests 50 \
  --concurrency 5
```

**Save results to a file:**
```bash
python -m loadtest \
  --url http://localhost:5000/health \
  --requests 100 \
  --output results.json
```

### Configuration File

For more complex scenarios or to save configurations for reuse, use a YAML configuration file:

1. Create a config file (or use the sample in `examples/sample_config.yaml`):

```yaml
url: "http://localhost:5000/api/items"
method: "POST"
requests: 200
concurrency: 20
timeout: 30
headers:
  Content-Type: "application/json"
  Authorization: "Bearer your-token-here"
body: '{"name": "test", "description": "test item"}'
```

2. Run the load test with the config file:

```bash
python -m loadtest --config config.yaml
```

## CLI Options

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--url` | `-u` | TEXT | *required* | Target URL for load testing. Must include scheme (http:// or https://). |
| `--method` | `-m` | TEXT | `GET` | HTTP method to use. Valid: GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS. |
| `--requests` | `-n` | INTEGER | `100` | Total number of requests to send. |
| `--concurrency` | `-c` | INTEGER | `10` | Number of concurrent requests. Cannot exceed total requests. |
| `--timeout` | `-t` | INTEGER | `30` | Request timeout in seconds. |
| `--header` | `-H` | TEXT | - | Custom HTTP header in format "Key: Value". Can be specified multiple times. |
| `--data` | `-d` | TEXT | - | Request body data. Typically used with POST/PUT requests. |
| `--output` | `-o` | PATH | - | Output file path for saving the report. If not specified, prints to console. |
| `--help` | - | - | - | Show help message and exit. |

## Examples

### Example 1: Basic Health Check

Test a health check endpoint with moderate load:

```bash
python -m loadtest \
  --url http://localhost:5000/health \
  --requests 200 \
  --concurrency 20
```

### Example 2: API Endpoint with Authentication

Test an authenticated API endpoint:

```bash
python -m loadtest \
  --url https://api.example.com/v1/users \
  --method GET \
  --header "Authorization: Bearer eyJhbGc..." \
  --header "Accept: application/json" \
  --requests 100 \
  --concurrency 10
```

### Example 3: POST Request with JSON Body

Create resources via POST:

```bash
python -m loadtest \
  --url http://localhost:5000/api/items \
  --method POST \
  --header "Content-Type: application/json" \
  --data '{"name": "Load Test Item", "description": "Created during load test"}' \
  --requests 50 \
  --concurrency 5
```

### Example 4: High Concurrency Stress Test

Push your service to the limit:

```bash
python -m loadtest \
  --url http://localhost:5000/health \
  --requests 1000 \
  --concurrency 100 \
  --timeout 60
```

### Example 5: Save Results for Analysis

Export results to JSON for later review:

```bash
python -m loadtest \
  --url http://localhost:5000/api/items \
  --requests 500 \
  --concurrency 50 \
  --output load_test_results.json
```

The JSON file will contain:
```json
{
  "total_requests": 500,
  "successful_requests": 495,
  "failed_requests": 5,
  "error_rate": 1.0,
  "response_times": {
    "min": 0.012,
    "max": 0.543,
    "mean": 0.089,
    "median": 0.078,
    "p95": 0.234,
    "p99": 0.412
  },
  "throughput": 112.36,
  "duration": 4.45,
  "status_codes": {
    "200": 495,
    "500": 5
  }
}
```

### Example 6: PUT Request to Update Resources

```bash
python -m loadtest \
  --url http://localhost:5000/api/items/1 \
  --method PUT \
  --header "Content-Type: application/json" \
  --data '{"name": "Updated Name", "description": "Updated Description"}' \
  --requests 30 \
  --concurrency 3
```

### Example 7: DELETE Request

```bash
python -m loadtest \
  --url http://localhost:5000/api/items/1 \
  --method DELETE \
  --requests 10 \
  --concurrency 2
```

## Interpreting Results

After running a load test, you'll see a comprehensive report with three main sections:

### 1. Summary Statistics

```
┌─────────────────── Summary Statistics ───────────────────┐
│ Total Requests: 100                                      │
│ Successful: 98                                           │
│ Failed: 2                                                │
│ Error Rate: 2.00%                                        │
│ Duration: 4.52s                                          │
│ Throughput: 22.12 req/s                                  │
└──────────────────────────────────────────────────────────┘
```

**Key Metrics:**
- **Total Requests**: Total number of requests sent to the server
- **Successful**: Requests that completed with 2xx status codes and no errors
- **Failed**: Requests that failed due to errors or non-2xx status codes
- **Error Rate**: Percentage of failed requests (should be close to 0% for healthy services)
- **Duration**: Total time taken to complete all requests
- **Throughput**: Average requests per second (higher is better)

### 2. Response Time Statistics

```
┌───────────── Response Time Statistics ──────────────┐
│ Metric           │               Value (ms)        │
├──────────────────┼─────────────────────────────────┤
│ Minimum          │                          12.34  │
│ Mean             │                          89.76  │
│ Median           │                          78.45  │
│ 95th Percentile  │                         234.56  │
│ 99th Percentile  │                         412.78  │
│ Maximum          │                         543.21  │
└──────────────────┴─────────────────────────────────┘
```

**Understanding Response Times:**
- **Minimum**: Fastest response time (best case scenario)
- **Mean**: Average response time across all requests
- **Median**: Middle value when all response times are sorted (50th percentile)
- **95th Percentile (p95)**: 95% of requests were faster than this
- **99th Percentile (p99)**: 99% of requests were faster than this
- **Maximum**: Slowest response time (worst case scenario)

**What to Look For:**
- **Low and consistent values** indicate good performance
- **Large gap between median and p95/p99** suggests inconsistent performance or occasional slow requests
- **Very high p99** may indicate timeout issues or resource contention

### 3. Status Code Distribution

```
┌─────────── Status Code Distribution ───────────┐
│ Status Code │ Count │           Percentage    │
├─────────────┼───────┼─────────────────────────┤
│ 200         │    98 │                 98.0%   │
│ 500         │     2 │                  2.0%   │
└─────────────┴───────┴─────────────────────────┘
```

**HTTP Status Code Ranges:**
- **2xx (Green)**: Success - Request was successful
  - 200 OK, 201 Created, 204 No Content
- **3xx (Yellow)**: Redirection - Further action needed
  - 301 Moved Permanently, 302 Found
- **4xx (Orange)**: Client Error - Request has an error
  - 400 Bad Request, 401 Unauthorized, 404 Not Found
- **5xx (Red)**: Server Error - Server failed to fulfill request
  - 500 Internal Server Error, 503 Service Unavailable

**Ideal Distribution:**
- **100% 2xx codes** for endpoints that should always succeed
- **Some 4xx codes** are normal if testing error handling
- **5xx codes** indicate server problems that need investigation

### Performance Benchmarks

**General Guidelines:**

| Metric | Excellent | Good | Acceptable | Poor |
|--------|-----------|------|------------|------|
| Error Rate | 0% | < 0.1% | < 1% | > 1% |
| P95 Response Time | < 100ms | < 200ms | < 500ms | > 500ms |
| P99 Response Time | < 200ms | < 500ms | < 1000ms | > 1000ms |
| Throughput | > 1000 req/s | > 100 req/s | > 10 req/s | < 10 req/s |

*Note: These are general guidelines. Actual acceptable values depend on your specific use case and requirements.*

## Advanced Usage

### Progressive Load Testing

Start with low concurrency and gradually increase to find performance limits:

```bash
# Low load
python -m loadtest -u http://localhost:5000/health -n 100 -c 10

# Medium load
python -m loadtest -u http://localhost:5000/health -n 500 -c 50

# High load
python -m loadtest -u http://localhost:5000/health -n 1000 -c 100
```

### Testing Different Endpoints

Create multiple configuration files for different endpoints:

**config_health.yaml:**
```yaml
url: "http://localhost:5000/health"
method: "GET"
requests: 200
concurrency: 20
```

**config_api.yaml:**
```yaml
url: "http://localhost:5000/api/items"
method: "GET"
requests: 200
concurrency: 20
headers:
  Accept: "application/json"
```

Then run each test:
```bash
python -m loadtest --config config_health.yaml
python -m loadtest --config config_api.yaml
```

### Automated Testing in CI/CD

Integrate load testing into your CI/CD pipeline:

```bash
#!/bin/bash
# run_load_tests.sh

# Start the application
python app.py &
APP_PID=$!

# Wait for app to be ready
sleep 2

# Run load tests
python -m loadtest -u http://localhost:5000/health -n 100 -c 10 -o results.json

# Check results
ERROR_RATE=$(python -c "import json; data=json.load(open('results.json')); print(data['error_rate'])")

# Cleanup
kill $APP_PID

# Fail if error rate is too high
if (( $(echo "$ERROR_RATE > 1.0" | bc -l) )); then
    echo "Load test failed: Error rate too high ($ERROR_RATE%)"
    exit 1
fi

echo "Load test passed: Error rate $ERROR_RATE%"
```

## Testing

Run the test suite to verify the tool works correctly:

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_config.py -v

# Run with coverage
python -m pytest tests/ --cov=loadtest --cov-report=html
```

## Project Structure

```
/repo
├── loadtest/              # Main package
│   ├── __init__.py       # Package initialization
│   ├── __main__.py       # Entry point
│   ├── cli.py            # CLI interface
│   ├── config.py         # Configuration management
│   ├── engine.py         # Request execution engine
│   ├── metrics.py        # Metrics collection
│   └── reporter.py       # Report generation
├── tests/                 # Test suite
│   ├── test_config.py
│   ├── test_engine.py
│   ├── test_metrics.py
│   ├── test_reporter.py
│   └── test_integration.py
├── examples/             
│   └── sample_config.yaml # Sample configuration
├── app.py                # Sample Flask API
├── requirements.txt      # Dependencies
└── README.md            # This file
```

## Troubleshooting

### Common Issues

**1. "ModuleNotFoundError: No module named 'click'"**
```bash
# Install dependencies
pip install -r requirements.txt
```

**2. "Error: URL must include a scheme (http:// or https://)"**
```bash
# Make sure URL includes http:// or https://
python -m loadtest --url http://localhost:5000/health  # ✓ Correct
python -m loadtest --url localhost:5000/health         # ✗ Wrong
```

**3. "Concurrency cannot exceed total requests"**
```bash
# Reduce concurrency or increase requests
python -m loadtest -u http://localhost:5000/health -n 100 -c 10  # ✓ Correct
python -m loadtest -u http://localhost:5000/health -n 10 -c 100  # ✗ Wrong
```

**4. High error rates or timeouts**
- Increase timeout: `--timeout 60`
- Reduce concurrency to avoid overwhelming the server
- Check if the target server is running and accessible
- Verify firewall and network settings

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is provided as-is for educational and testing purposes.

## Sample Flask API

The repository includes a simple Flask API (`app.py`) for testing purposes:

**Endpoints:**
- `GET /health` - Returns `{"status": "ok"}`
- `GET /api/items` - Returns list of items
- `POST /api/items` - Creates a new item (requires `name` and `description` in JSON body)

**Start the API:**
```bash
python app.py
```

The API will run on `http://localhost:5000`.