from typing import List, Dict, Any, Optional


class DataTransformer:
    @staticmethod
    def _clean_string(value: Optional[str], default: str = "") -> str:
        """Sanitiza strings eliminando espacios en blanco innecesarios."""
        if value is None:
            return default
        return str(value).strip()

    @staticmethod
    def _clean_int(value: Any, default: int = 0) -> int:
        """Garantiza la conversión estricta a enteros."""
        try:
            return int(value) if value is not None else default
        except (ValueError, TypeError):
            return default

    def transform_repositories(self, raw_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Limpia, valida y normaliza el lote de registros crudos recibidos de la API.
        """
        cleaned_records: List[Dict[str, Any]] = []

        for item in raw_items:
            # Validación de campo obligatorio identificador
            repo_id = item.get("id")
            if not repo_id:
                continue

            owner = item.get("owner") or {}
            owner_login = self._clean_string(owner.get("login"), default="unknown")

            language = item.get("language")
            normalized_language = self._clean_string(language) if language else None

            record = {
                "repo_id": self._clean_int(repo_id),
                "name": self._clean_string(item.get("name")),
                "full_name": self._clean_string(item.get("full_name")),
                "owner_login": owner_login,
                "stars": self._clean_int(item.get("stargazers_count")),
                "forks": self._clean_int(item.get("forks_count")),
                "open_issues": self._clean_int(item.get("open_issues_count")),
                "language": normalized_language,
                "created_at": self._clean_string(item.get("created_at")),
                "updated_at": self._clean_string(item.get("updated_at")),
            }

            cleaned_records.append(record)

        return cleaned_records