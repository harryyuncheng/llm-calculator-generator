# LLM Calculator Generator

This project is an automated code generator that leverages Anthropic's Claude Sonnet LLM to create Python calculator applications from a prompt. It reads a project specification, sends it to Claude, parses the generated code blocks, writes them to files, installs dependencies, and launches the resulting application.

## Features

- **Automated code generation**: Uses Claude Sonnet to generate all required code files for a calculator project based on a prompt.
- **Dependency management**: Automatically updates and installs dependencies from generated `requirements.txt`.
- **Debugging support**: Saves raw Claude outputs with timestamps for easy debugging.
- **Seamless execution**: Runs the generated application immediately after setup.

## Requirements

- Python 3.8 or higher
- Anthropic API key
- Internet connection for AI calculations

## Installation & Setup

### 1. Clone or Download the Project

Ensure you have all the required files:

### 2. Set up your environment

- Create a `.env` file in the project root with your Anthropic API key:

  ```
  ANTHROPIC_API_KEY=your_api_key_here
  ```

- Install dependencies:

  ```sh
  pip install -r requirements.txt
  ```

### 3. Edit the prompt

Modify `prompt.txt` to describe the calculator project you want to generate.

### 4. Run the generator

Execute the main script:

```sh
python script.py
```

The script will:

- Call Claude Sonnet with your prompt
- Save the raw output in `claude_outputs/`
- Parse and write all generated code files
- Update/install dependencies
- Launch the generated application (via `run.py`)

## File Structure

- `script.py` — Main orchestrator script
- `run.py` — Entry point for the generated application
- `calculator.py` — (May be generated) Calculator logic
- `prompt.txt` — Project specification prompt
- `requirements.txt` — Python dependencies
- `claude_outputs/` — Saved raw Claude outputs for debugging

## Notes

- Requires Python 3.8+
- Requires an Anthropic API key
- Claude's output must follow the expected code block format for correct parsing

## License

See [LICENSE](LICENSE) for details.
