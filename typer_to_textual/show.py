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

    def __init__(self, application, command, homepage_data=None) -> None:
        self.application = application
        self.command = command
        self.homepage_data = homepage_data
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Header("Show", classes="header")
        yield Container(
                Static("[bold][yellow]Operation in progress....", id="loading"),
                id="c")
        yield Footer()

    async def run_button(self):

        if len(self.homepage_data) > 0:

            args = [self.application]
            for key, value in self.homepage_data.items():
                if value == "BOOL":
                    args.append(key)
                else:
                    args.append(key)
                    args.append(value)

            args.append(self.command)

            result = subprocess.run(args, capture_output=True)

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