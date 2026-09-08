import json
from pathlib import Path

from app.core.config import settings


CACHE_FILE= Path(settings.storage_dir) / "evaluation_cache.json"

def load_cache():
    """
    load the cache
    """

    if not CACHE_FILE.exists():
        return {}

    with open("CACHE_FILE", "r", encoding="utf-8") as file:
        return json.load(file)


def save_cache(cache):
    """
    Save the cache for the evaluations.
    """

    CACHE_FILE.mkdir(parents=True, exist_ok=True)


    with open("CACHE_FILE", "w", encoding="utf-8") as file:
        json.dump(
            cache,
            file, 
            indent=4
        )

def get_cache_key(question, expected_answer):
    """
    create a unique key for a evaluation item.
    """

    return f"{question.strip()}|||{expected_answer.strip()}"
    
