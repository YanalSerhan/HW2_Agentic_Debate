with open("docs/TODO.md", "r") as f:
    content = f.read()

# Mark Phase 10 as done in upcoming tasks
content = content.replace(
    "- [ ] Score timeline visualization (phase 10)",
    "- [x] Score timeline visualization (phase 10)"
)

# Add Phase 11 tasks
content = content.replace(
    "- [ ] Cinematic README (phase 11)",
    "- [ ] Cinematic README (phase 11)\n- [ ] Export HTML/Markdown features"
)

with open("docs/TODO.md", "w") as f:
    f.write(content)

with open("README.md", "r") as f:
    readme = f.read()

visualize_section = """
  # Visualize a debate transcript
  uv run python -m debate.sdk.sdk visualize --file results/your_file.json
"""

if "visualize --file" not in readme:
    readme = readme.replace(
        "uv run python -m debate.sdk.sdk run --topic \"...\" --verbose",
        "uv run python -m debate.sdk.sdk run --topic \"...\" --verbose\n" + visualize_section
    )
    with open("README.md", "w") as f:
        f.write(readme)
