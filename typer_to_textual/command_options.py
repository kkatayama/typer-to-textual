
from textual.app import ComposeResult
from textual.binding import Binding
from textual.widgets import Static, Button, Footer, Input, Checkbox
from textual.containers import Container, Vertical, Horizontal
from textual.screen import Screen


class Header(Static):
    pass


class CommandOptions(Screen):

    def __init__(self, output, identifier) -> None:
        self.output = output
        self.identifier = identifier
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Header(f"{self.identifier}", classes="header")
        yield Footer()

    def arguments(self):
        start_arguments = False
        arguments = {}
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
                    words[2] = words[2].replace('[', '(').replace(']', ')')
                    if words[0] == "help":
                        continue
                arguments[words[0]] = [words[1], words[2]]

        return arguments

    def options(self):
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

                types = ["INTEGER", "BOOLEAN", "TEXT"]
                if len(words) == 3 and words[1] not in types:
                    words[1] = "BOOLEAN"

                if len(words) == 4 and words[1] not in types:
                    words[1] = words[2]

                if words:
                    words[0] = words[0].replace('--', '')
                    words[2] = words[2].replace('[', '(')
                    words[2] = words[2].replace(']', ')')
                    if words[0] == "help":
                        continue
                options.append(words)

        return options

    def on_mount(self) -> None:

        options = self.options()
        arguments = self.arguments()

        if len(arguments) != 0 or len(options) != 0:
            self.mount(Vertical(id="booklet-vertical"))

        if len(arguments) != 0:
            self.query_one(Vertical).mount(Static("Arguments", id="arguments"))
            for k, v in arguments.items():
                arg_str = f"[b][red]{v[0]}[/] {' '.join(v[1:])}[/]"
                self.query_one(Vertical).mount(Horizontal(
                    Static(f"[b][cyan]{k}[/][/]", classes="name"),
                    Static(arg_str, classes="description"),
                    Input(placeholder=f"{k}....", classes="input"),
                    classes="booklet-horizontal"
                    )
                )

        if len(options) != 0:
            self.query_one(Vertical).mount(Static("Options", id="options2"))
            for option in options:

                if option[1] != "BOOLEAN":
                    self.query_one(Vertical).mount(Horizontal(
                        Static(f"[b][cyan]{option[0]}[/][/]", classes="name"),
                        Static(f"[b][red]{option[1]}[/]", classes="types"),
                        Static(f"[b]{' '.join(option[2:])}[/]", classes="description"),
                        Input(placeholder=f"{option[0]}....", classes="input", id=f"--{option[0]}"),
                        classes="booklet-horizontal"
                        )
                    )

                else:
                    self.query_one(Vertical).mount(Horizontal(
                        Static(f"[b][cyan]{option[0]}[/][/]", classes="name"),
                        Static(f"[b][red]{option[1]}[/]", classes="types"),
                        Static(f"[b]{' '.join(option[2:])}[/]", classes="description"),
                        Checkbox(id=f"--{option[0]}"),
                        classes="booklet-horizontal"
                        )
                    )

        if len(arguments) == 0 and len(options) == 0:
            self.mount(Container(
                            Horizontal(Static("[bold][yellow]No arguments or options needed !!!\n")),
                            Horizontal(Button("[bold]Run command", id=f"show-{self.identifier}")),
                            classes="empty"
                    )
            )

        else:
            self.query_one(Vertical).mount(
                Horizontal(
                    Button("show", id=f"show-{self.identifier}"),
                    classes="booklet-horizontal-button",
                    )
            )

    BINDINGS = [
        Binding(key="r", action="app.pop_screen", description="return"),
    ]