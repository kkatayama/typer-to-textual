from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Static, Button, Footer, Input, Checkbox
from textual.containers import Container, Vertical, Horizontal
from textual.screen import Screen
from textual import events
from textual.pilot import Pilot

import sys
import subprocess
from typing import List


class Header(Static):
    pass


class HomePage(Screen):

    def __init__(self, output) -> None:
        self.output = output
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Header("Homepage", classes="header")
        yield Container(
            Static(f"Esse3 command line utility", classes="title"),
            Vertical(
                Static("Option preferences", id="login"),
                Input(placeholder="username...     [default: None or env var]", classes="credentials"),
                Input(placeholder="password...     [default: None or env var]", password=True, classes="credentials"),
                Horizontal(
                    Static("enable debug mode:"),
                    Checkbox(),
                    id="debug"
                ),
                Static("commands", id="commands"),
                Button("Taxes", id="taxes"),
                Button("Booklet", id="booklet"),
                #Button("Reservations", id="reservations"),
            ),
            id="homepage"
        )
        yield Footer()


class Booklet(Screen):

    def __init__(self, output) -> None:
        self.output = output
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Header("Homepage", classes="header")
        yield Static(f"{self.output[6]}")


class Tui(App):

    def __init__(self, output) -> None:
        self.output = output
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
        application = "esse3-student"

        result = subprocess.run(
            [application, command, "--help"],
            capture_output=True,
        )
        return result.stdout.decode().split('\n')

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "booklet":
            result = self.call_button("booklet")
            self.install_screen(Booklet(result), name="booklet")
            self.push_screen("booklet")


def output() -> List[str]:
    comando = "esse3-student"

    if len(sys.argv) < 2:
        raise Exception("Non sono stati passati argomenti.")

    argomento = sys.argv[1]

    if len(sys.argv) == 2 and argomento != "--help":
        raise Exception("L'unico argomento passato non è '--help'.")

    risultato = subprocess.run(
        [comando, argomento, "--help"],
        capture_output=True,
    )
    return risultato.stdout.decode().split('\n')


if __name__ == "__main__":
    result = output()
    Tui(result).run()
