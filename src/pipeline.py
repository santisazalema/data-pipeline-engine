import time
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from src.extractor import GitHubExtractor
from src.transformer import DataTransformer
from src.database import DatabaseManager


class ETLPipeline:
    def __init__(self, db_path: str = "data/pipeline.db", token: Optional[str] = None):
        self.console = Console()
        self.extractor = GitHubExtractor(token=token)
        self.transformer = DataTransformer()
        self.db = DatabaseManager(db_path=db_path)

    def run(self, query: str = "stars:>5000", max_pages: int = 2, per_page: int = 25) -> None:
        self.console.print(Panel.fit("[bold blue]Starting Data Pipeline ETL & Profiler[/bold blue]"))

        # 1. Extracción
        start_extract = time.perf_counter()
        with self.console.status("[cyan]Extracting raw datasets via GitHub API...[/cyan]"):
            raw_data = self.extractor.fetch_repositories(
                query=query, max_pages=max_pages, per_page=per_page
            )
        extract_time = round(time.perf_counter() - start_extract, 2)
        self.console.print(f"[green]✔[/green] Extracted [bold]{len(raw_data)}[/bold] records ({extract_time}s)")

        if not raw_data:
            self.console.print("[yellow]⚠ No data fetched. Pipeline aborted.[/yellow]")
            return

        # 2. Transformación y validación
        start_transform = time.perf_counter()
        with self.console.status("[magenta]Transforming & sanitizing records...[/magenta]"):
            cleaned_data = self.transformer.transform_repositories(raw_data)
        transform_time = round(time.perf_counter() - start_transform, 4)
        self.console.print(f"[green]✔[/green] Transformed [bold]{len(cleaned_data)}[/bold] clean records ({transform_time}s)")

        # 3. Carga e indexación
        start_load = time.perf_counter()
        with self.console.status("[yellow]Executing batch upsert into database...[/yellow]"):
            rows_affected = self.db.bulk_upsert_repositories(cleaned_data)
        load_time = round(time.perf_counter() - start_load, 4)
        self.console.print(f"[green]✔[/green] Database upsert executed ({load_time}s)")

        # 4. Reporte analítico (Profiler)
        self._render_report(extract_time, transform_time, load_time)

    def _render_report(self, extract_t: float, transform_t: float, load_t: float) -> None:
        metrics = self.db.get_profiler_metrics()

        # Tabla de distribución por lenguaje
        lang_table = Table(title="Top Languages by Volume & Impact", show_header=True, header_style="bold magenta")
        lang_table.add_column("Language", style="dim", width=15)
        lang_table.add_column("Count", justify="right")
        lang_table.add_column("Avg Stars", justify="right")
        lang_table.add_column("Max Stars", justify="right")

        for lang in metrics.get("top_languages", []):
            lang_table.add_row(
                str(lang["language"]),
                str(lang["count"]),
                f"{lang['avg_stars']:,}",
                f"{lang['max_stars']:,}"
            )

        # Tabla de Top Repositorios
        repo_table = Table(title="Top Indexed Repositories", show_header=True, header_style="bold cyan")
        repo_table.add_column("Repository", style="dim", width=30)
        repo_table.add_column("Stars ⭐", justify="right")
        repo_table.add_column("Forks 🍴", justify="right")

        for repo in metrics.get("top_repos", []):
            repo_table.add_row(
                str(repo["full_name"]),
                f"{repo['stars']:,}",
                f"{repo['forks']:,}"
            )

        self.console.print("\n")
        self.console.print(lang_table)
        self.console.print("\n")
        self.console.print(repo_table)

        summary_text = (
            f"• [b]Total Records Persisted:[/b] {metrics['total_records']}\n"
            f"• [b]Pipeline Latency:[/b] E: {extract_t}s | T: {transform_t}s | L: {load_t}s"
        )
        self.console.print(Panel(summary_text, title="ETL Performance Summary", expand=False))