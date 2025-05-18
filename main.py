from typing import Any, Dict

import FreeSimpleGUI as sg
from loguru import logger

from src.config import MODELS
from src.gui import initialize_window
from src.handlers import handle_events
from utils.cache import set_default_position, set_default_model


def main() -> None:
    """
    Main function. Initialize the window and handle the events.
    """
    window: sg.Window = initialize_window()
    logger.debug("Application started.")

    while True:
        event: str
        values: Dict[str, Any]
        event, values = window.read()

        if event in ["-CLOSE_BUTTON-", sg.WIN_CLOSED]:
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
            break

        handle_events(window, event, values)

    window.close()


if __name__ == "__main__":
    main()
