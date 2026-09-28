import os
import argparse
from dotenv import load_dotenv
from src.pipeline import ETLPipeline


def main():
    # Cargar variables de entorno si existen (.env)
    load_dotenv()
    github_token = os.getenv("GITHUB_TOKEN")

    parser = argparse.ArgumentParser(
        description="Data Pipeline ETL & Profiler - High-performance data ingestion engine."
    )
    parser.add_argument(
        "--query",
        type=str,
        default="stars:>10000",
        help="Search query to fetch repositories from GitHub API (default: stars:>10000)",
    )
    parser.add_argument(
        "--pages",
        type=int,
        default=2,
        help="Number of pages to ingest (default: 2)",
    )
    parser.add_argument(
        "--per-page",
        type=int,
        default=25,
        help="Records per API page (default: 25)",
    )

    args = parser.parse_args()

    pipeline = ETLPipeline(token=github_token)
    pipeline.run(
        query=args.query,
        max_pages=args.pages,
        per_page=args.per_page,
    )


if __name__ == "__main__":
    main()