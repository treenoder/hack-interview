import httpx

def transcribe_audio_from_file(file_path: str = "record.wav"):
    with open(file_path, "rb") as f:
        audio = f.read()
        response = httpx.post(
            "http://192.168.31.76:9000/asr",
            params={
                "language": "uk",
                "initial_prompt": "Захист лабораторної роботи з математики",
            },
            files={
                "audio_file": audio,
            }
        )
        return response.content.decode("utf-8")