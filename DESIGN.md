# Design Document: Joke CLI

## Overview
Add a command-line interface (CLI) to the existing Flask API project that can fetch and display jokes. The CLI will be a separate module that can be run independently from the Flask API.

## Requirements
- Add a joke CLI that users can run from the command line
- The CLI should fetch jokes from a public joke API or use a local joke collection
- The CLI should be simple and easy to use

## Technical Approach

### Architecture
1. **CLI Module**: Create a new `joke_cli.py` file that implements the CLI functionality
2. **Joke Service**: Create a `joke_service.py` module to handle joke retrieval logic, separating concerns between CLI interface and joke fetching
3. **Configuration**: Add any necessary dependencies to `requirements.txt`
4. **Testing**: Add unit tests for the new functionality in `test_joke_cli.py`
5. **Documentation**: Update README.md with instructions for using the joke CLI

### Implementation Details

#### Joke Source
Use a free public API like JokeAPI (https://v2.jokeapi.dev/) or icanhazdadjoke API, or implement a simple local joke collection if network independence is preferred. For simplicity, we'll use a local collection to avoid external dependencies.

#### CLI Interface
The CLI will accept basic commands:
- Display a random joke
- Optional: filter by category or type
- Use Python's `argparse` module for command-line argument parsing

#### File Structure
```
/repo
├── app.py (existing Flask API)
├── joke_service.py (new - joke logic)
├── joke_cli.py (new - CLI interface)
├── test_app.py (existing tests)
├── test_joke_cli.py (new - CLI tests)
├── requirements.txt (updated)
└── README.md (updated)
```

## Task Breakdown

The work is decomposed into independent, parallel tasks where possible:

1. **Task 1**: Create joke service module with joke collection and retrieval logic
2. **Task 2**: Create CLI interface module with argument parsing and output formatting
3. **Task 3**: Add tests for joke service functionality
4. **Task 4**: Add tests for CLI functionality
5. **Task 5**: Update dependencies in requirements.txt (if needed)
6. **Task 6**: Update README with CLI usage instructions

Tasks 1 and 2 are independent core implementation tasks. Tasks 3 and 4 depend on their respective implementation tasks. Task 5 is independent. Task 6 should be done last to document the complete feature.

## Testing Strategy
- Unit tests for joke service (random selection, joke structure)
- Unit tests for CLI argument parsing and output
- Integration test to verify end-to-end CLI execution

## Success Criteria
- Users can run `python joke_cli.py` to get a random joke
- All tests pass
- Documentation is updated
- No breaking changes to existing Flask API functionality