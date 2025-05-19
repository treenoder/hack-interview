from typing import Any, Dict

import FreeSimpleGUI as sg
from loguru import logger

from src import audio, gpt_query
from src.button import OFF_IMAGE, ON_IMAGE
from src.models import AnalyzeType
from src.screenshot_area import ScreenshotArea
from utils.list_models import update_models
from utils.cache import set_default_model, set_default_position

# Create a global instance of the ScreenshotArea class
screenshot_area = ScreenshotArea()

_analyze_type = AnalyzeType.ANALYZE


def handle_events(window: sg.Window, event: str, values: Dict[str, Any]) -> None:
    """
    Handle the events. Record audio, transcribe audio, generate quick and full answers.

    Args:
        window (sg.Window): The window element.
        event (str): The event.
        values (Dict[str, Any]): The values of the window.
    """
    global _analyze_type
    # Check if the screenshot area window handled the event
    if screenshot_area.handle_events(event, values):
        return

    # If the user is not focused on the position input, process the events
    focused_element: sg.Element = window.find_element_with_focus()
    if not focused_element or focused_element.Key != "-POSITION_INPUT-":
        if event in ("r", "R", "-RECORD_BUTTON-"):
            recording_event(window)
        elif event in ("a", "A", "-ANALYZE_BUTTON-"):
            _analyze_type = AnalyzeType.ANALYZE
            transcribe_event(window)
        elif event == "-ANALYZE_SS_BUTTON-":
            _analyze_type = AnalyzeType.ANALYZE_SS
            analyze_ss_event(window)
        elif event == "-SCREENSHOT_AREA_BUTTON-":
            screenshot_area_event(window)

    # If the user is focused on the position input
    if event[:6] in ("Return", "Escape"):
        window["-ANALYZE_BUTTON-"].set_focus()

    # When the model is changed, update the default model in cache
    elif event == "-MODEL_COMBO-":
        model = values["-MODEL_COMBO-"]
        if model:
            logger.debug(f"Setting default model to {model}")
            set_default_model(model)

    # When the user presses Enter or Tab in the position input, update the default position
    elif event in ("Return:36", "Tab:48") and focused_element and focused_element.Key == "-POSITION_INPUT-":
        position = values["-POSITION_INPUT-"]
        if position:
            logger.debug(f"Setting default position to {position}")
            set_default_position(position)
            window["-ANALYZE_BUTTON-"].set_focus()

    # When the update models button is clicked
    elif event == "-UPDATE_MODELS-":
        logger.debug("Updating models list...")
        window["-UPDATE_MODELS-"].update(disabled=True)
        window["-UPDATE_MODELS-"].update(text="...")

        # Update models in a separate thread to avoid blocking the UI
        def update_models_thread():
            models = update_models()
            return models

        window.perform_long_operation(update_models_thread, "-MODELS_UPDATED-")

    # When models are updated
    elif event == "-MODELS_UPDATED-":
        models = values["-MODELS_UPDATED-"]
        logger.debug(f"Models updated: {len(models)} models found")

        # Get current model
        current_model = values["-MODEL_COMBO-"]

        # Update the dropdown with new models
        window["-MODEL_COMBO-"].update(values=models)

        # If current model is in the new list, keep it selected
        if current_model in models:
            window["-MODEL_COMBO-"].update(value=current_model)
        # Otherwise select the first model
        elif models:
            window["-MODEL_COMBO-"].update(value=models[0])
            set_default_model(models[0])

        # Re-enable the update button
        window["-UPDATE_MODELS-"].update(disabled=False)
        window["-UPDATE_MODELS-"].update(text="↻")

    # When the transcription is ready
    elif event == "-WHISPER-":
        answer_events(window, values, _analyze_type)

    # When the quick answer is ready
    elif event == "-QUICK_ANSWER-":
        logger.debug("Quick answer generated.")
        print("Quick answer:", values["-QUICK_ANSWER-"])
        window["-QUICK_ANSWER-"].update(values["-QUICK_ANSWER-"])

    # When the full answer is ready
    elif event == "-FULL_ANSWER-":
        logger.debug("Full answer generated.")
        print("Full answer:", values["-FULL_ANSWER-"])
        window["-FULL_ANSWER-"].update(values["-FULL_ANSWER-"])


def recording_event(window: sg.Window) -> None:
    """
    Handle the recording event. Record audio and update the record button.

    Args:
        window (sg.Window): The window element.
    """
    button: sg.Element = window["-RECORD_BUTTON-"]
    button.metadata.state = not button.metadata.state
    button.update(image_data=ON_IMAGE if button.metadata.state else OFF_IMAGE)

    # Record audio
    if button.metadata.state:
        window.perform_long_operation(lambda: audio.record(button), "-RECORDED-")


def transcribe_event(window: sg.Window) -> None:
    """
    Handle the transcribe event. Transcribe audio and update the text area.

    Args:
        window (sg.Window): The window element.
    """
    transcribed_text: sg.Element = window["-TRANSCRIBED_TEXT-"]
    transcribed_text.update("Transcribing audio...")

    # Transcribe audio
    window.perform_long_operation(gpt_query.transcribe_audio, "-WHISPER-")


def screenshot_area_event(window: sg.Window) -> None:
    """
    Handle the screenshot area event. Toggle the screenshot area window and update the button.

    Args:
        window (sg.Window): The window element.
    """
    button: sg.Element = window["-SCREENSHOT_AREA_BUTTON-"]
    button.metadata.state = not button.metadata.state
    button.update(image_data=ON_IMAGE if button.metadata.state else OFF_IMAGE)

    # Toggle the screenshot area window
    screenshot_area.toggle()


def analyze_ss_event(window: sg.Window) -> None:
    """
    Handle the analyze SS event. Take a screenshot of the screenshot area if enabled,
    save it as screenshot.png, then transcribe audio and update the text area.

    Args:
        window (sg.Window): The window element.
    """
    # Check if screenshot area is enabled
    button: sg.Element = window["-SCREENSHOT_AREA_BUTTON-"]
    if button.metadata.state and screenshot_area.window:
        # Take a screenshot of the screenshot area and save it as screenshot.png
        logger.debug("Taking screenshot of the screenshot area...")
        screenshot_area.grab_area_screenshot("screenshot.png")
        logger.debug("Screenshot saved as screenshot.png")

    # Continue with regular analyze functionality
    transcribe_event(window)


def answer_events(window: sg.Window, values: Dict[str, Any], analyze_type: AnalyzeType) -> None:
    """
    Handle the answer events. Generate quick and full answers and update the text areas.

    Args:
        window (sg.Window): The window element.
        values (Dict[str, Any]): The values of the window.
    """
    transcribed_text: sg.Element = window["-TRANSCRIBED_TEXT-"]
    quick_answer: sg.Element = window["-QUICK_ANSWER-"]
    full_answer: sg.Element = window["-FULL_ANSWER-"]

    # Get audio transcript and update text area
    audio_transcript: str = values["-WHISPER-"]
    transcribed_text.update(audio_transcript)

    # Get model and position
    model: str = values["-MODEL_COMBO-"]
    position: str = values["-POSITION_INPUT-"]

    # Generate quick answer
    logger.debug("Generating quick answer...")
    quick_answer.update("Generating quick answer...")
    window.perform_long_operation(
        lambda: gpt_query.generate_answer(
            audio_transcript,
            short_answer=True,
            temperature=0,
            model=model,
            position=position,
            analyze_type=analyze_type,
        ),
        "-QUICK_ANSWER-",
    )

    # Generate full answer
    logger.debug("Generating full answer...")
    full_answer.update("Generating full answer...")
    window.perform_long_operation(
        lambda: gpt_query.generate_answer(
            audio_transcript,
            short_answer=False,
            temperature=0.7,
            model=model,
            position=position,
            analyze_type=analyze_type,
        ),
        "-FULL_ANSWER-",
    )
