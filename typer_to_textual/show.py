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

    def __init__(self, application, command, homepage_data=None, command_data=None) -> None:
        self.application = application
        self.command = command
        self.homepage_data = homepage_data
        self.command_data = command_data
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
                args.append(value)

        result = subprocess.run(args, capture_output=True)

        await self.query_one("#loading").remove()
        result = result.stdout.decode().split('\n')
        for row in result:
            await self.query_one("#show-container").mount(Static(f"[bold]{row}", classes="output"))

    async def on_mount(self) -> None:
        await asyncio.sleep(0.1)
        asyncio.create_task(self.run_button())

    BINDINGS = [
        Binding(key="r", action="app.pop_screen", description="return"),
    ]