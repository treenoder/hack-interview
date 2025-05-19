from typing import Any, Dict

import FreeSimpleGUI as sg
from loguru import logger

from src.button import OFF_IMAGE
from src.config import MODELS
from src.gui import initialize_window
from src.handlers import handle_events, screenshot_area
from utils.cache import set_default_position, set_default_model


def main() -> None:
    """
    Main function. Initialize the window and handle the events.
    """
    window: sg.Window = initialize_window()
    window.TKroot.resizable(True, True)
    logger.debug("Application started.")

    while True:
        event: str
        values: Dict[str, Any]

        # Create a list of windows to read from
        windows = [window]
        if screenshot_area.window:
            windows.append(screenshot_area.window)

        # Read events from all windows
        window_with_event, event, values = sg.read_all_windows()

        # If the main window was closed
        if window_with_event == window and event in ["-CLOSE_BUTTON-", sg.WIN_CLOSED]:
            logger.debug("Closing...")
            # Save default model
            model = values.get("-MODEL_COMBO-")
            if model and model in MODELS:
                set_default_model(model)

            # Save the current position before closing
            position = values.get("-POSITION_INPUT-")
            if position:
                logger.debug(f"Saving position: {position}")
                set_default_position(position)

            # Close the screenshot area window if it's open
            if screenshot_area.window:
                screenshot_area.hide()

            break

        # If the screenshot area window was closed
        elif window_with_event == screenshot_area.window and event == sg.WIN_CLOSED:
            screenshot_area.hide()
            # Update the button state
            window["-SCREENSHOT_AREA_BUTTON-"].metadata.state = False
            window["-SCREENSHOT_AREA_BUTTON-"].update(image_data=OFF_IMAGE)
            continue

        # Handle events for the main window
        if window_with_event == window:
            handle_events(window, event, values)

    window.close()


if __name__ == "__main__":
    main()
