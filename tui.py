import asyncio

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
        if options:
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

        if commands:
            self.query_one("#interno").mount(Static("Commands", id="commands"))
        for command in commands:
            self.query_one("#interno").mount(Horizontal(
                Button(f"{command[0]}", id=f"{command[0]}"),
                Static(f"[bold][#E1C699]{command[1]}"),
                classes="commands-horizontal"
            ))


class Options(Screen):

    def __init__(self, output, identifier) -> None:
        self.output = output
        self.identifier = identifier
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Header(f"{self.identifier}", classes="header")
        yield Footer()

    def process_arguments(self):
        start_arguments = False
        data = {}
        for index, line in enumerate(self.output, start=1):

            if "Arguments" in line:
                start_arguments = True
                continue

            if "Options" in line:
                start_arguments = False

            if start_arguments and any(word.isalpha() for word in line.split()):
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
                    words.insert(1, " ")
                if words:
                    words[0] = words[0].replace('--', '')
                    words[2] = words[2].replace('[', '(')
                    words[2] = words[2].replace(']', ')')
                    if words[0] == "help":
                        continue
                data[words[0]] = [words[1], words[2]]

        return data

    def process_options(self):
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
                if words:
                    words[0] = words[0].replace('--', '')
                    words[2] = words[2].replace('[', '(')
                    words[2] = words[2].replace(']', ')')
                    if words[0] == "help":
                        continue
                options.append(words)

        return options

    def on_mount(self) -> None:
        options = self.process_options()
        arguments = self.process_arguments()

        if len(arguments) != 0 or len(options) != 0:
            self.mount(Vertical(id="booklet-vertical"))

        if len(arguments) != 0:
            self.query_one(Vertical).mount(Static("Arguments", id="arguments"))
            for k, v in arguments.items():
                arg_str = f"[b][red]{v[0]}[/] {' '.join(v[1:])}[/]"
                self.query_one(Vertical).mount(Horizontal(
                    Static(f"[b][cyan]{k}[/][/]", classes="name"),
                    Static(arg_str, classes="description"),
                    Input(placeholder="prova....", classes="input"),
                    classes="booklet-horizontal"
                    )
                )


        if len(options) != 0:
            self.query_one(Vertical).mount(Static("Options", id="options2"))
            for option in options:
                option[0] = option[0].replace('--', '').replace("-", " ")
                arg_str = f"[b][red]{option[1]}[/] {' '.join(option[2:])}[/]"

                self.query_one(Vertical).mount(Horizontal(
                    Static(f"[b][cyan]{option[0]}[/][/]", classes="name"),
                    Checkbox(),
                    Static(arg_str, classes="description"),
                    Input(placeholder="prova....", classes="input"),
                    classes="booklet-horizontal"
                    )
                )

        if len(arguments) == 0 and len(options) == 0:
            self.mount(Container(
                            Static("[bold][yellow]No arguments needed !!!\n"),
                            Button("[bold]run command", id=f"show-{self.identifier}"),
                            classes="empty"
                    )
            )

        else:
            self.query_one(Vertical).mount(
                Horizontal(
                    Button("show", id=f"run-{self.identifier}"),
                    classes="booklet-horizontal",
                )
            )

    BINDINGS = [
        Binding(key="r", action="app.pop_screen", description="return"),
    ]


class Show(Screen):

    def __init__(self, application, command, debug, value=None) -> None:
        self.application = application
        self.command = command
        self.debug = debug
        self.value = value
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Header("Show", classes="header")
        yield Container(
                Static("[bold][yellow]Operation loading....", id="loading"),
                id="c")
        yield Footer()

    async def run_button(self):

        if self.value is not None:
            if self.debug:
                result = subprocess.run(
                    [self.application, "--debug", self.command, self.value],
                    capture_output=True,
                )
            else:
                result = subprocess.run(
                    [self.application, self.command, self.value],
                    capture_output=True,
                )
        else:
            if self.debug:
                result = subprocess.run(
                    [self.application, "--debug", self.command],
                    capture_output=True,
                )
            else:
                result = subprocess.run(
                    [self.application, self.command],
                    capture_output=True,
                )

        await self.query_one("#loading").remove()
        result = result.stdout.decode().split('\n')
        for index, line in enumerate(result, start=1):
            await self.query_one("#c").mount(Static(f"[bold]{line}", classes="prova"))

    async def on_mount(self) -> None:
        await asyncio.sleep(0.1)
        asyncio.create_task(self.run_button())

    BINDINGS = [
        Binding(key="r", action="app.pop_screen", description="return"),
    ]


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

    """def run_button(self, command: str, debug: bool) -> List[str]:

        if debug:
            result = subprocess.run(
                [self.application, "--debug", command],
                capture_output=True,
            )
        else:
            result = subprocess.run(
                [self.application, command],
                capture_output=True,
            )

        return result.stdout.decode().split('\n')"""

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
            if not self.is_screen_installed(event.button.id):
                self.install_screen(Options(result, event.button.id), name=event.button.id)
            self.push_screen(event.button.id)
        elif event.button.id.startswith("show-"):
            command = event.button.id.replace("show-", "")
            debug = self.query("Checkbox").first().value
            if not self.is_screen_installed(event.button.id):
                self.install_screen(Show(self.application, command, debug), name=event.button.id)
            self.push_screen(event.button.id)
        elif event.button.id.startswith("run-"):
            value = self.query_one(".input").value
            debug = self.query("Checkbox").first().value
            command = event.button.id.replace("run-", "")
            if not self.is_screen_installed(event.button.id):
                self.install_screen(Show(self.application, command, debug, value), name=event.button.id)
            self.push_screen(event.button.id)

    def action_pop_screen(self):
        self.uninstall_screen(self.pop_screen())


if __name__ == "__main__":
    Tui().run()
