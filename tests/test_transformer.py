import pytest
from src.transformer import DataTransformer


@pytest.fixture
def transformer():
    return DataTransformer()


def test_transform_repositories_sanitization(transformer):
    raw_payload = [
        {
            "id": 101,
            "name": "  test-repo  ",
            "full_name": "owner/test-repo",
            "owner": {"login": "owner"},
            "stargazers_count": "1500",  # String numérico desde la API
            "forks_count": 300,
            "open_issues_count": None,   # Valor nulo
            "language": " Python ",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-02-01T00:00:00Z",
        },
        {
            # Registro corrupto sin ID: debe ser descartado
            "name": "corrupt-repo",
            "stargazers_count": 10,
        },
    ]

    cleaned = transformer.transform_repositories(raw_payload)

    assert len(cleaned) == 1
    record = cleaned[0]

    assert record["repo_id"] == 101
    assert record["name"] == "test-repo"
    assert record["stars"] == 1500
    assert record["open_issues"] == 0  # Coerción segura de None a 0
    assert record["language"] == "Python"