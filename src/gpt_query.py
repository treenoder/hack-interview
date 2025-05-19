import dataclasses

from dotenv import load_dotenv
from loguru import logger
from openai import ChatCompletion, OpenAI
from openai.types.audio import Transcription

from src.config import DEFAULT_MODEL, DEFAULT_POSITION, OUTPUT_FILE_NAME
from src.models import AnalyzeType
from utils.image import encode_image
from utils.transcribe import transcribe_audio_from_file

SYS_PREFIX: str = "Ти відповідаєш на запитання викладача з "
SYS_SUFFIX: str = """ .
Ти отримаєш аудіотранскрипцію запитання. 
Він може бути неповним, деякі слова можуть бути неправильно транскибовані. 
Потрібно зрозуміти питання і написати на нього відповідь.
Latex формули видавати між символами $.\n
"""

SHORT_INSTRUCTION: str = "Відповідайте коротко, обмежуючи свою відповідь 50 словами."
LONG_INSTRUCTION: str = """
Перш ніж відповісти, глибоко вдихни і подумай крок за кроком. 
Якщо у відповіді є формули, то треба записати короткі визначення всіх параметрів, змінних та самої формули.
Перевір що відповідь містить не більше ніж 150-200 слів. 
"""

load_dotenv()

client: OpenAI = OpenAI()

@dataclasses.dataclass
class Transcription:
    path: str
    text: str | None = None
    _sha1_hash: str = dataclasses.field(init=False)

    def __post_init__(self):
        import hashlib
        with open(self.path, "rb") as f:
            self._sha1_hash = hashlib.sha1(f.read()).hexdigest()

    @property
    def sha1_hash(self):
        return self._sha1_hash

    def __eq__(self, other):
        return self.sha1_hash == other.sha1_hash

    def __hash__(self):
        return hash(self.sha1_hash)


last_transcription: Transcription | None = None


def transcribe_audio(path_to_file: str = OUTPUT_FILE_NAME) -> str:
    """
    Transcribe audio from a file using the OpenAI Whisper API.

    Args:
        path_to_file (str, optional): Path to the audio file. Defaults to OUTPUT_FILE_NAME.

    Returns:
        str: The audio transcription.
    """
    global last_transcription
    logger.debug(f"Transcribing audio from: {path_to_file}...")
    if last_transcription and last_transcription.text and last_transcription == Transcription(path_to_file):
        logger.debug("Using cached transcription.")
        return last_transcription.text
    else:
        last_transcription = Transcription(path_to_file)

    # with open(path_to_file, "rb") as audio_file:
    #     try:
    #         transcript = str(client.audio.transcriptions.create(
    #             model="whisper-1", file=audio_file, response_format="text"
    #         ))
    #     except Exception as error:
    #         logger.error(f"Can't transcribe audio: {error}")
    #         raise error
    transcript = transcribe_audio_from_file(path_to_file)
    last_transcription.text = transcript
    logger.debug("Audio transcribed.")
    print("Transcription:", transcript)

    return transcript


def generate_answer(
    transcript: str,
    short_answer: bool = True,
    temperature: float = 0.7,
    model: str = DEFAULT_MODEL,
    position: str = DEFAULT_POSITION,
    analyze_type: AnalyzeType = AnalyzeType.ANALYZE,
) -> str:
    """
    Generate an answer to the question using the OpenAI API.

    Args:
        transcript (str): The audio transcription.
        short_answer (bool, optional): Whether to generate a short answer. Defaults to True.
        temperature (float, optional): The temperature to use. Defaults to 0.7.
        model (str, optional): The model to use. Defaults to DEFAULT_MODEL.
        position (str, optional): The position to use. Defaults to DEFAULT_POSITION.
        analyze_type (AnalyzeType, optional): The type of analysis to perform. Defaults to AnalyzeType.ANALYZE.

    Returns:
        str: The generated answer.
    """
    # Generate system prompt
    system_prompt: str = SYS_PREFIX + position + SYS_SUFFIX
    if short_answer:
        system_prompt += SHORT_INSTRUCTION
    else:
        system_prompt += LONG_INSTRUCTION

    # Generate answer
    try:
        content = [{
            "type": "text",
            "text": transcript,
        }]
        if analyze_type is AnalyzeType.ANALYZE_SS:
            img = encode_image("screenshot.png")
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{img}"
                }
            })
        response: ChatCompletion = client.chat.completions.create(
            model=model,
            temperature=temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": content},
            ],
        )
    except Exception as error:
        logger.error(f"Can't generate answer: {error}")
        raise error

    return response.choices[0].message.content
