from rich.console import Console

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Static, Button, Footer, Input, Checkbox
from textual.containers import Container, Vertical, Horizontal
from textual.screen import Screen
from textual import events
from textual.pilot import Pilot
from rich.text import Text

import typer

from typing import List, Tuple


import sys
import subprocess
from typing import List


class Header(Static):
    pass


class HomePage(Screen):

    def __init__(self, output) -> None:
        self.output = output
        super().__init__()

    def process_title(self) -> str:
        title = ""
        for index, line in enumerate(self.output, start=1):
            if index == 4:
                title = line
                break
        if title == "":
            title = "User interface utility"

        return title.strip()

    def process_options(self):
        start_options = False
        data = {}
        for index, line in enumerate(self.output, start=1):

            if "Options" in line:
                start_options = True
                continue

            if "Commands" in line:
                start_options = False

            if start_options and any(word.isalpha() for word in line.split()):
                items = line.split(" ")
                words = []
                current_word = ""
                for option in items:
                    if option and option != '│' and option != '*':
                        current_word += " " + option
                    else:
                        words.append(current_word.strip())
                        current_word = ""

                words = list(filter(bool, words))
                if len(words) == 2:
                    words.insert(1, "BOOLEAN")
                if words:
                    words[0] = words[0].replace('--', '')
                    words[2] = words[2].replace('[', '(')
                    words[2] = words[2].replace(']', ')')
                    if words[0] == "help":
                        continue
                    data[words[0]] = [words[1], words[2]]

        return data

    def process_commands(self):
        start_commands = False
        commands = []
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
                commands.append(words)

        return commands

    def compose(self) -> ComposeResult:
        yield Header("Homepage", classes="header")
        yield Container(
            id="homepage"
        )
        yield Footer()

    def on_mount(self) -> None:

        options = self.process_options()
        title = self.process_title()
        commands = self.process_commands()

        self.query_one(Container).mount(Static(f"[green][bold]{title}", classes="title"))
        self.query_one(Container).mount(Container(id="interno"))
        self.query_one("#interno").mount(Static("Options", id="options"))
        for k, v in options.items():
            if v[0] == "BOOLEAN":
                self.query_one("#interno").mount(Horizontal(
                    Static(f"[bold]{v[1]}"),
                    Checkbox(),
                    classes="commands-horizontal"
                ))
            else:
                self.query_one("#interno").mount(Horizontal(
                    Input(placeholder=f"{k}...."),
                    Static(f"[bold]{v[1]}"),
                    classes="commands-horizontal"
                ))
        self.query_one("#interno").mount(Static("Commands", id="commands"))
        for command in commands:
            self.query_one("#interno").mount(Horizontal(
                Button(f"{command[0]}", id=f"{command[0]}"),
                Static(f"[bold][#E1C699]{command[1]}"),
                classes="commands-horizontal"
            ))


class Command(Screen):

    def __init__(self, output) -> None:
        self.output = output
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Header("Homepage", classes="header")
        yield Vertical(id="booklet-vertical")

    def process_input(self):
        start = False
        options = []
        for index, line in enumerate(self.output, start=1):
            if "Options" in line:
                start = True
                continue
            if start and any(word.isalpha() for word in line.split()):
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
                if len(words) == 2:
                    words.insert(1, "BOOLEAN")
                options.append(words)

        return options

    def on_mount(self) -> None:
        options = self.process_input()
        for option in options:

            arg_str = f"[b][red]{option[1]}[/] {' '.join(option[2:])}[/]"

            self.query_one(Vertical).mount(Horizontal(
                Static(f"[b][cyan]{option[0]}[/][/]", classes="name"),
                Checkbox(),
                Static(arg_str, classes="description"),
                Input(placeholder="prova....", classes="input"),
                classes="booklet-horizontal"
                )
            )


class Tui(App):

    def __init__(self) -> None:
        self.output, self.application = self.main_output()
        super().__init__()

    def main_output(self) -> Tuple[List[str], str]:

        if len(sys.argv) != 2:
            Console().print("pass exactly two argument!!!", style="bold yellow")
            exit()

        application = sys.argv[1]

        result = subprocess.run(
            [application, "--help"],
            capture_output=True,
        )
        return result.stdout.decode().split('\n'), application

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

    def call_button(self, command: str, debug: bool) -> List[str]:

        if debug:
            result = subprocess.run(
                [self.application, "--debug", command, "--help"],
                capture_output=True,
            )
        else:
            result = subprocess.run(
                [self.application, command, "--help"],
                capture_output=True,
            )

        return result.stdout.decode().split('\n')

    def process_data(self) -> List[str]:
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
        buttons = self.process_data()
        if event.button.id in buttons:
            debug = self.query("Checkbox").first().value
            result = self.call_button(event.button.id, debug)
            self.install_screen(Command(result), name=event.button.id)
            self.push_screen(event.button.id)


if __name__ == "__main__":
    Tui().run()
