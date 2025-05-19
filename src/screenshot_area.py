import FreeSimpleGUI as sg
from PIL import ImageGrab


class ScreenshotArea:
    """
    A class to create and manage a transparent resizable window with a red outline.
    """

    def __init__(self):
        """
        Initialize the screenshot area window.
        """
        self.window = None
        self.is_visible = False

    def show(self):
        """
        Show the screenshot area window.
        """
        if self.window:
            self.window.close()

        # Create a layout with a single frame that has a red border
        layout = [[
            sg.Frame(
                '',
                [[]],
                background_color='white',
                border_width=3,
                size=(400, 300),
                key='-FRAME-',
                pad=(0, 0)
            )
        ]]

        # Create a window with a transparent background
        self.window = sg.Window('Screenshot Area', layout,
                                no_titlebar=True,
                                grab_anywhere=True,
                                resizable=True,
                                background_color="red",
                                keep_on_top=True,
                                alpha_channel=0.1,  # Almost transparent
                                return_keyboard_events=True,
                                finalize=True)

        # Make the frame expand to fill the window
        self.window['-FRAME-'].expand(True, True)
        self.window.TKroot.resizable(True, True)
        self.window.TKroot.attributes('-topmost', True)

        self.is_visible = True

    def hide(self):
        """
        Hide the screenshot area window.
        """
        if self.window:
            self.window.close()
            self.window = None
            self.is_visible = False

    def toggle(self):
        """
        Toggle the visibility of the screenshot area window.
        """
        if self.is_visible:
            self.hide()
        else:
            self.show()

    def handle_events(self, event, values):
        """
        Handle events for the screenshot area window.
        
        Args:
            event (str): The event.
            values (dict): The values.
            
        Returns:
            bool: True if the event was handled, False otherwise.
        """
        if not self.window:
            return False

        # Handle escape key to close the window
        if event == 'Escape:27':
            self.hide()
            return True

        return False

    def grab_area_screenshot(self, filename):
        """
        Делает скриншот текущей области окна и сохраняет его в файл.
        """
        if not self.window:
            return
        # Получаем положение и размеры окна screenshot_area
        x = self.window.TKroot.winfo_rootx()
        y = self.window.TKroot.winfo_rooty()
        w = self.window.TKroot.winfo_width()
        h = self.window.TKroot.winfo_height()

        bbox = (x, y, x + w, y + h)
        screenshot = ImageGrab.grab(bbox)
        screenshot.save(filename)

