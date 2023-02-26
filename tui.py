import sys
import subprocess

from textual.app import App
from textual.binding import Binding
from textual.widgets import Button
from textual import events
from textual.pilot import Pilot

from typing import Tuple, List

from typer_to_textual.command_options import CommandOptions
from typer_to_textual.homepage import HomePage
from typer_to_textual.show import Show


def homepage_output() -> Tuple[List[str], str]:

    try:
        if len(sys.argv) != 2:
            raise RuntimeError("pass exactly two arguments")
    except RuntimeError as e:
        print(f"Error: {str(e)}")
        exit()

    application = sys.argv[1]

    result = subprocess.run(
        [application, "--help"],
        capture_output=True,
    )

    return result.stdout.decode().split('\n'), application


class Tui(App):

    def __init__(self) -> None:
        self.output, self.application = homepage_output()
        super().__init__()

    CSS_PATH = "style.css"

    BINDINGS = [
        Binding(key="escape", action="key_escape", description="exit"),
    ]

    def on_mount(self) -> None:
        self.install_screen(HomePage(self.output), name="homepage")
        self.push_screen("homepage")

    async def on_key(self, event: events.Key):
        if event.key == "up":
            pilot = Pilot(self)
            await pilot.press("shift+tab")
        if event.key == "down":
            pilot = Pilot(self)
            await pilot.press("tab")

    def action_key_escape(self) -> None:
        self.exit()

    def call_button(self, command: str) -> List[str]:

        result = subprocess.run(
            [self.application, command, "--help"],
            capture_output=True,
        )

        return result.stdout.decode().split('\n')

    def buttons(self) -> List[str]:
        start_commands = False
        buttons = []
        for index, line in enumerate(self.output, start=1):

            if "Commands" in line:
                start_commands = True
                continue

            if start_commands and any(word.isalpha() for word in line.split()):
                command = line.split(" ")
                words = []
                current_word = ""
                for item in command:
                    if item and item != '│':
                        current_word += " " + item
                    else:
                        words.append(current_word.strip())
                        current_word = ""

                words = list(filter(bool, words))
                buttons.append(words[0])

        return buttons

    def on_button_pressed(self, event: Button.Pressed):

        buttons = self.buttons()

        if event.button.id in buttons:

            result = self.call_button(event.button.id)
            if not self.is_screen_installed(event.button.id):
                self.install_screen(CommandOptions(result, event.button.id), name=event.button.id)
            self.push_screen(event.button.id)

        elif event.button.id.startswith("show-"):

            homepage_checkbox_elements = self.query_one(HomePage).query("Checkbox")
            homepage_checkbox_data = {}
            for element in homepage_checkbox_elements:
                if str(element.value) == "False":
                    continue
                homepage_checkbox_data[element.id] = "BOOL"

            homepage_input_elements = self.query_one(HomePage).query("Input")
            homepage_input_data = {}
            for element in homepage_input_elements:
                if element.value == '':
                    continue
                homepage_input_data[element.id] = element.value

            homepage_data = {}
            homepage_data.update(homepage_checkbox_data)
            homepage_data.update(homepage_input_data)

            """command_checkbox_elements = self.query_one(CommandOptions).query("Checkbox")
            command_checkbox_data = {}
            for element in command_checkbox_elements:
                command_checkbox_data[element.id] = element.value

            command_input_elements = self.query_one(CommandOptions).query("Input")
            command_input_data = {}
            for element in command_input_elements:
                command_input_data[element.id] = element.value"""

            command = event.button.id.replace("show-", "")

            if not self.is_screen_installed(event.button.id):
                self.install_screen(Show(self.application, command, homepage_data), name=event.button.id)
            self.push_screen(event.button.id)




        """elif event.button.id.startswith("run-"):
            #values = self.query_one(".input").value



            debug = self.query("Checkbox").first().value
            command = event.button.id.replace("run-", "")

            inputs = self.query_one(HomePage).query("Input")
            data = {}
            for i in inputs:
                data[i.id] = i.value

            if not self.is_screen_installed(event.button.id):
                self.install_screen(Show(self.application, command, debug, data), name=event.button.id)
            self.push_screen(event.button.id)"""

    def action_pop_screen(self):
        self.uninstall_screen(self.pop_screen())


if __name__ == "__main__":
    Tui().run()
