from openai import OpenAI
from dotenv import load_dotenv
from utils.cache import get_cached_models, set_cached_models


def get_models(use_cache=True):
    """
    Get the list of available models.

    Args:
        use_cache (bool, optional): Whether to use cached models. Defaults to True.

    Returns:
        List[str]: The list of models.
    """
    # If using cache and there are cached models, return them
    if use_cache:
        cached_models = get_cached_models()
        if cached_models:
            return cached_models

    # Otherwise, fetch models from the API
    models = []
    load_dotenv()
    client = OpenAI()
    try:
        ms = client.models.list()
        for model in ms:
            models.append(model.id)

        # Cache the models for future use
        set_cached_models(models)
    except Exception as e:
        print(f"Error fetching models: {e}")

    return models


def update_models():
    """
    Force update the models list from the API.

    Returns:
        List[str]: The updated list of models.
    """
    return get_models(use_cache=False)


def main():
    models = get_models()
    for model in models:
        print(model)


if __name__ == "__main__":
    main()
