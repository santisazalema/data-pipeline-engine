import time
import requests
from typing import List, Dict, Any, Optional


class GitHubExtractor:
    BASE_URL = "https://api.github.com/search/repositories"

    def __init__(self, token: Optional[str] = None):
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "DataPipelineEngine/1.0",
        }
        if token:
            self.headers["Authorization"] = f"Bearer {token}"

    def fetch_repositories(
        self, query: str = "stars:>1000", max_pages: int = 3, per_page: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Extrae repositorios por lotes paginados manejando códigos de estado y timeouts.
        """
        all_items: List[Dict[str, Any]] = []

        for page in range(1, max_pages + 1):
            params = {
                "q": query,
                "sort": "stars",
                "order": "desc",
                "page": page,
                "per_page": per_page,
            }

            try:
                response = requests.get(
                    self.BASE_URL,
                    headers=self.headers,
                    params=params,
                    timeout=10
                )

                if response.status_code == 403:
                    # Control de rate limit de la API pública
                    print(f"[WARN] Rate limit alcanzado en página {page}. Abortando extracción.")
                    break

                response.raise_for_status()
                data = response.json()
                items = data.get("items", [])

                if not items:
                    break

                all_items.extend(items)
                time.sleep(1)  # Intervalo de cortesía para respetar la API

            except requests.exceptions.RequestException as e:
                print(f"[ERROR] Error de red en la página {page}: {e}")
                break

        return all_items