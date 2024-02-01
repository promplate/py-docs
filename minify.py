import gzip
from pathlib import Path

import brotli
from minify_html import minify


def compress_file(file: Path):
    print(file)
    if file.suffix == ".html":
        original_data = minify(file.read_text("utf-8")).encode("utf-8")
        file.write_bytes(original_data)
    else:
        original_data = file.read_bytes()
    gzip_data = gzip.compress(original_data)
    brotli_data = brotli.compress(original_data)
    if len(brotli_data) < len(gzip_data) < len(original_data):
        file.with_name(f"{file.name}.br").write_bytes(brotli_data)


def main():
    for file in Path("./site").rglob("*"):
        if file.is_file():
            compress_file(file)


if __name__ == "__main__":
    main()
