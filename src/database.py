import sqlite3
from typing import List, Dict, Any


class DatabaseManager:
    def __init__(self, db_path: str = "data/pipeline.db"):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        """Crea tablas e índices necesarios para el pipeline."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS repositories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    repo_id INTEGER UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    full_name TEXT NOT NULL,
                    owner_login TEXT NOT NULL,
                    stars INTEGER NOT NULL,
                    forks INTEGER NOT NULL,
                    open_issues INTEGER NOT NULL,
                    language TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            # Índices para optimizar filtros y ordenamientos analíticos
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_repo_lang ON repositories(language);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_repo_stars ON repositories(stars DESC);")
            conn.commit()

    def bulk_upsert_repositories(self, records: List[Dict[str, Any]]) -> int:
        """
        Inserta registros por lotes.
        Si el repositorio ya existe (por repo_id), actualiza sus métricas cambiantes.
        """
        if not records:
            return 0

        query = """
            INSERT INTO repositories (
                repo_id, name, full_name, owner_login, stars,
                forks, open_issues, language, created_at, updated_at
            ) VALUES (
                :repo_id, :name, :full_name, :owner_login, :stars,
                :forks, :open_issues, :language, :created_at, :updated_at
            )
            ON CONFLICT(repo_id) DO UPDATE SET
                stars = excluded.stars,
                forks = excluded.forks,
                open_issues = excluded.open_issues,
                updated_at = excluded.updated_at,
                processed_at = CURRENT_TIMESTAMP;
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany(query, records)
            conn.commit()
            return cursor.rowcount

    def get_profiler_metrics(self) -> Dict[str, Any]:
        """Obtiene métricas agregadas directamente desde el motor SQL."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) AS total FROM repositories;")
            total_records = cursor.fetchone()["total"]

            cursor.execute("""
                SELECT 
                    COALESCE(language, 'Unknown') AS language,
                    COUNT(*) AS count,
                    ROUND(AVG(stars), 2) AS avg_stars,
                    MAX(stars) AS max_stars
                FROM repositories
                GROUP BY language
                ORDER BY count DESC
                LIMIT 5;
            """)
            top_languages = [dict(row) for row in cursor.fetchall()]

            cursor.execute("""
                SELECT full_name, stars, forks
                FROM repositories
                ORDER BY stars DESC
                LIMIT 3;
            """)
            top_repos = [dict(row) for row in cursor.fetchall()]

            return {
                "total_records": total_records,
                "top_languages": top_languages,
                "top_repos": top_repos
            }