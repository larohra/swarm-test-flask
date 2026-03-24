# Flask API Project

A simple Flask API project with a command-line joke utility.

## Features

- **Flask API**: RESTful API with health check and item management endpoints
- **Joke CLI**: Command-line tool to display random jokes from various categories

## Joke CLI

### Overview

The joke CLI is a simple command-line tool that displays random jokes from a curated collection. It's perfect for adding some humor to your day or testing the joke service module.

### Installation

Install the required dependencies:

```bash
pip install -r requirements.txt
```

### Usage

Run the joke CLI from the command line:

```bash
python3 joke_cli.py
```

Each time you run the command, it will display a random joke from the collection.

### Example Output

The CLI displays jokes in two formats:

**Two-part jokes (setup and punchline):**
```
$ python3 joke_cli.py
Why do programmers prefer dark mode?
Because light attracts bugs!
```

**One-liner jokes:**
```
$ python3 joke_cli.py
There are only 10 types of people in the world: those who understand binary and those who don't.
```

### Joke Categories

The collection includes jokes from three categories:
- **Programming**: Tech and developer humor
- **Dad**: Classic dad jokes
- **General**: General humor and wordplay

The collection currently contains 15 jokes across these categories.

### Command-Line Options

```
usage: joke_cli.py [-h]

Display a random joke from the command line

options:
  -h, --help  show this help message and exit
```

## Flask API

The Flask API provides endpoints for health checking and item management.