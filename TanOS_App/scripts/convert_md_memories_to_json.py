import argparse
import json
from pathlib import Path


def convert_file(md_path: Path, json_path: Path) -> None:
    """Convert a Markdown memory file to a simple JSON structure."""
    content = md_path.read_text(encoding="utf-8")
    json_path.parent.mkdir(parents=True, exist_ok=True)
    data = {"content": content}
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Converted {md_path} -> {json_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert MEMORIES Markdown files to JSON.")
    parser.add_argument("md_dir", nargs="?", default="../MEMORIES_markdown", help="Directory with Markdown memories")
    parser.add_argument("json_dir", nargs="?", default="../tanos_data/memories", help="Output directory for JSON files")
    args = parser.parse_args()

    md_dir = Path(args.md_dir)
    json_dir = Path(args.json_dir)

    for md_file in md_dir.glob("*.md"):
        json_file = json_dir / f"{md_file.stem}.json"
        convert_file(md_file, json_file)


if __name__ == "__main__":
    main()
