import asyncio
import subprocess

from textual.app import ComposeResult
from textual.binding import Binding
from textual.widgets import Static, Footer
from textual.containers import Container
from textual.screen import Screen


class Header(Static):
    pass


class Show(Screen):

    def __init__(self, application, command, homepage_data=None, command_data=None, lista=None) -> None:
        self.application = application
        self.command = command
        self.homepage_data = homepage_data
        self.command_data = command_data
        self.lista = lista
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Header("Show", classes="header")
        yield Container(
                Static("[bold][yellow]Operation in progress....", id="loading"),
                id="show-container")
        yield Footer()

    async def run_button(self):

        args = [self.application]

        for key, value in self.homepage_data.items():
            args.append(key)
            if value != "BOOL":
                args.append(value)

        args.append(self.command)

        for key, value in self.command_data.items():
            args.append(key)
            if value != "BOOL":
                if isinstance(value, list):
                    for val in value:
                        args.append(val)
                else:
                    values = value.split(",")  # Dividi il valore in una lista di stringhe
                    for val in values:
                        args.append(val.strip())

        for elemento in self.lista:
            args.append(elemento)

        result = subprocess.run(args, capture_output=True)

        output = result.stdout.decode().split('\n')
        stderr_lines = result.stderr.decode().split('\n')

        await self.query_one("#loading").remove()
        for row in output:
            await self.query_one("#show-container").mount(Static(f"[bold]{row}", classes="output"))
        for error in stderr_lines:
            await self.query_one("#show-container").mount(Static(f"[bold]{error}", classes="output"))

    async def on_mount(self) -> None:
        await asyncio.sleep(0.1)
        asyncio.create_task(self.run_button())

    BINDINGS = [
        Binding(key="r", action="app.pop_screen", description="return"),
    ]