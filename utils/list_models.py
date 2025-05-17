from openai import OpenAI
from dotenv import load_dotenv


def get_models():
    models = []
    load_dotenv()
    client = OpenAI()
    try:
        ms = client.models.list()
        for model in ms:
            models.append(model.id)
    except Exception as e:
        print(f"Error fetching models: {e}")
    return models


def main():
    models = get_models()
    for model in models.data:
        print(model.id)


if __name__ == "__main__":
    main()
