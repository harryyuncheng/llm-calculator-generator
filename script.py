import os
import sys
import subprocess
from pathlib import Path
from dotenv import load_dotenv
import anthropic
import time

def load_api_key():
    load_dotenv()
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY not found in .env")
        sys.exit(1)
    return api_key

def read_prompt():
    prompt_path = Path(__file__).parent / "prompt.txt"
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()

def call_claude(api_key, prompt):
    client = anthropic.Anthropic(api_key=api_key)
    system_prompt = (
        "You are an expert Python developer. "
        "Given the following project specification, generate all required code files. "
        "For each file, output a Markdown code block with the filename as a comment on the first line, "
        "followed by the code. Only output code blocks, no explanations."
    )
    user_prompt = f"{prompt}\n\n# Please generate all required code files as described above."
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=8192,
        temperature=0,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}]
    )
    return response.content[0].text

def update_requirements_from_claude(claude_output, req_file):
    import re
    # Find all requirements.txt code blocks from Claude's output
    req_blocks = re.findall(
        r"```pip-requirements\n// filepath: .+?requirements\.txt\n(.*?)```", claude_output, re.DOTALL
    )
    if not req_blocks:
        return  # No requirements.txt block found

    # Read current requirements
    if req_file.exists():
        with open(req_file, "r", encoding="utf-8") as f:
            current_reqs = set(
                line.strip() for line in f if line.strip() and not line.strip().startswith("#")
            )
    else:
        current_reqs = set()

    # Parse new requirements from Claude
    new_reqs = set()
    for block in req_blocks:
        for line in block.splitlines():
            dep = line.strip()
            if dep and not dep.startswith("#"):
                new_reqs.add(dep)

    # Find only new dependencies
    to_append = [dep for dep in new_reqs if dep not in current_reqs]
    if to_append:
        with open(req_file, "a", encoding="utf-8") as f:
            for dep in to_append:
                f.write(dep + "\n")
        print(f"Appended new dependencies to {req_file}: {to_append}")

def parse_and_write_files(claude_output, base_dir):
    import re

    # Match both // filepath: ... and # filename.py as the first line of the code block
    code_blocks = []
    # 1. Match // filepath: ... (original)
    code_blocks += re.findall(
        r"```[\w-]*\n// filepath: (.+?)\n(.*?)```", claude_output, re.DOTALL
    )
    # 2. Match # filename.py or # filename.txt or # filename.md as first line
    code_blocks += re.findall(
        r"```[\w-]*\n# ([^\n]+)\n(.*?)```", claude_output, re.DOTALL
    )

    if not code_blocks:
        print("No code blocks found in Claude's output.")
        sys.exit(1)
    for filepath, code in code_blocks:
        abs_path = Path(base_dir) / filepath.strip()
        abs_path.parent.mkdir(parents=True, exist_ok=True)
        with open(abs_path, "w", encoding="utf-8") as f:
            f.write(code.strip() + "\n")
        print(f"Wrote {abs_path}")

    # After writing files, update requirements.txt if needed
    req_file = Path(base_dir) / "requirements.txt"
    update_requirements_from_claude(claude_output, req_file)

def install_dependencies():
    req_file = Path(__file__).parent / "requirements.txt"
    if not req_file.exists():
        print("requirements.txt not found, skipping dependency installation.")
        return
    print("Installing dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(req_file)])

def run_main():
    run_py = Path(__file__).parent / "run.py"
    if not run_py.exists():
        print("run.py not found. Cannot launch application.")
        sys.exit(1)
    print("Launching application...")
    subprocess.run([sys.executable, str(run_py)])

def main():
    api_key = load_api_key()
    prompt = read_prompt()
    print("Calling Claude Sonnet to generate project code...")
    claude_output = call_claude(api_key, prompt)
    # Save Claude's raw output for debugging with a timestamped filename
    debug_dir = Path(__file__).parent / "claude_outputs"
    debug_dir.mkdir(exist_ok=True)
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    debug_file = debug_dir / f"claude_raw_output_{timestamp}.txt"
    with open(debug_file, "w", encoding="utf-8") as f:
        f.write(claude_output)
    print(f"Saved Claude output to {debug_file}")
    base_dir = Path(__file__).parent
    parse_and_write_files(claude_output, base_dir)
    install_dependencies()
    run_main()

if __name__ == "__main__":
    main()
