import json
import os
from typing import Dict, List, Any, Optional

CACHE_FILE = "cache.json"
DEFAULT_CACHE = {
    "models": [],
    "default_model": None,
    "default_position": "Python Developer"
}

def ensure_cache_exists() -> None:
    """
    Ensure that the cache file exists. If it doesn't, create it with default values.
    """
    if not os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "w") as f:
            json.dump(DEFAULT_CACHE, f, indent=2)

def read_cache() -> Dict[str, Any]:
    """
    Read the cache file and return its contents.

    Returns:
        Dict[str, Any]: The contents of the cache file.
    """
    ensure_cache_exists()
    try:
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        # If the file is corrupted, return default cache
        return DEFAULT_CACHE.copy()

def write_cache(cache_data: Dict[str, Any]) -> None:
    """
    Write the given data to the cache file.

    Args:
        cache_data (Dict[str, Any]): The data to write to the cache file.
    """
    with open(CACHE_FILE, "w") as f:
        json.dump(cache_data, f, indent=2)

def get_cached_models() -> List[str]:
    """
    Get the list of models from the cache.

    Returns:
        List[str]: The list of models.
    """
    cache = read_cache()
    return cache.get("models", [])

def set_cached_models(models: List[str]) -> None:
    """
    Set the list of models in the cache.

    Args:
        models (List[str]): The list of models to cache.
    """
    cache = read_cache()
    cache["models"] = models
    write_cache(cache)

def get_default_model() -> Optional[str]:
    """
    Get the default model from the cache.

    Returns:
        Optional[str]: The default model, or None if not set.
    """
    cache = read_cache()
    return cache.get("default_model")

def set_default_model(model: str) -> None:
    """
    Set the default model in the cache.

    Args:
        model (str): The model to set as default.
    """
    cache = read_cache()
    cache["default_model"] = model
    write_cache(cache)

def get_default_position() -> str:
    """
    Get the default position from the cache.

    Returns:
        str: The default position.
    """
    cache = read_cache()
    return cache.get("default_position", "Python Developer")

def set_default_position(position: str) -> None:
    """
    Set the default position in the cache.

    Args:
        position (str): The position to set as default.
    """
    cache = read_cache()
    cache["default_position"] = position
    write_cache(cache)
