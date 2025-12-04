"""Post-process llms.txt files to reduce size."""

from pathlib import Path

base_path = Path(__file__).parent.parent / "site"


def patch_llms_full_txt():
    llms_full_path = base_path / "llms-full.txt"
    llms_path = base_path / "llms.txt"

    full_content = llms_full_path.read_text("utf-8")
    llms_content = llms_path.read_text("utf-8")

    full_lines = full_content.splitlines()
    llms_lines = llms_content.splitlines()

    full_api_index = full_lines.index("# API References")
    llms_api_index = llms_lines.index("## API References")

    del full_lines[full_api_index:]
    full_lines.append("\n# API References")
    full_lines += llms_lines[llms_api_index + 1 :]

    llms_full_path.write_text(new_content := "\n".join(full_lines), encoding="utf-8")

    original = len(full_content)
    new = len(new_content)
    diff = original - new

    print("✓ Processed llms-full.txt")
    print(f"  {original:,} -> {new:,} bytes ({diff / original:.1%} reduction)")


def patch_each_file():
    for file in base_path / "llms-full.txt", *base_path.rglob("*.md"):
        lines = file.read_text("utf-8").splitlines()
        new_lines = ["---" if i and i.replace("_", "") == "" else i for i in lines]
        file.write_text("\n".join(new_lines), encoding="utf-8")


def main():
    patch_llms_full_txt()
    patch_each_file()


if __name__ == "__main__":
    main()
