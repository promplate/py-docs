from os import getenv
from pathlib import Path


def main():
    if site_url := getenv("SITE_URL"):
        path = Path("mkdocs.yml")

        path.write_text(f"site_url: {site_url}\n{path.read_text()}")


if __name__ == "__main__":
    main()
