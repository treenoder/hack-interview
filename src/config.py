from utils.list_models import get_models
from utils.cache import get_default_model, set_default_model, get_default_position, ensure_cache_exists

APPLICATION_WIDTH = 85
THEME = "DarkGray12"

OUTPUT_FILE_NAME = "record.wav"
SAMPLE_RATE = 48000

# Ensure cache exists before using it
ensure_cache_exists()

# Get models from cache or API
MODELS = sorted(get_models())

# Get default model from cache or use first model in the list
cached_default_model = get_default_model()
if cached_default_model and cached_default_model in MODELS:
    DEFAULT_MODEL = cached_default_model
elif MODELS:
    # If no default model in cache or it's not in the models list, use the first model
    DEFAULT_MODEL = MODELS[0]
    # Save this as the default model
    set_default_model(DEFAULT_MODEL)
else:
    # Fallback if no models available
    DEFAULT_MODEL = "gpt-4o-mini"

# Get default position from cache
DEFAULT_POSITION = get_default_position()
