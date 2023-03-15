import typer
from textual.app import ComposeResult
from textual.binding import Binding
from textual.widgets import Static, Button, Footer, Input, Checkbox
from textual.containers import Container, Vertical, Horizontal
from textual.screen import Screen


class Header(Static):
    pass


class CommandOptions(Screen):

    def __init__(self, output, identifier, description) -> None:
        self.output = output
        self.identifier = identifier
        self.description = description
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
        options = {}
        for index, line in enumerate(self.output, start=1):
            if "Options" in line:
                start = True
                continue
            if start:
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

                if words:

                    if ',' in words[0]:
                        words[0] = words[0].split(",")[0]
                    words[0] = words[0].replace('--', '')

                    if words[0] == "help":
                        continue

                    if len(words) > 1:
                        if words[1].startswith("-"):
                            words.remove(words[1])

                    if len(words) == 1:
                        words.append("BOOLEAN")

                    if len(words) == 2:
                        types = ["INTEGER", "FLOAT", "TEXT", "TUPLE", "UUID", "PATH", "FILENAME", "BOOLEAN"]
                        if not any(words[1].replace('[', '(').replace('<', '(').startswith(t) for t in types):
                            words.insert(1, "BOOLEAN")

                    if len(words) == 2:
                        words.append("No description")

                    for i in range(2, len(words)):
                        words[i] = words[i].replace('[', '(').replace(']', ')')

                    options[words[0]] = words[1:]

        return options

    def on_mount(self) -> None:

        options = self.options()
        arguments = self.arguments()

        if len(arguments) != 0 or len(options) != 0:
            self.mount(Container(id="booklet-vertical"))

        index = 1

        if len(arguments) != 0:

            self.query_one("#booklet-vertical").mount(Horizontal(
                Static("Arguments", classes="command-arguments"),
                classes="command-horizontal-options"
                )
            )

            for k, v in arguments.items():

                type = Static(f"[b][yellow]{v[0]}[/]", name=f"{v[0]}")
                type.styles.width = 10
                type.styles.border = ("blank", "red")

                self.query_one("#booklet-vertical").mount(Container(
                    Static(f"[b][cyan]{k}[/][/]", classes="name", id=f"--argument--{k}"),
                    type,
                    Static(f"[b]{' '.join(v[1:])}[/]", classes="description"),
                    Input(placeholder=f"{k}....", classes="input", name="input"),
                    Button("one more", classes="buttons", id=f"one_more-{index}"),
                    classes="booklet-horizontal",
                    id=f"container-{index}"
                    )
                )
                index += 1

        if len(options) != 0:

            self.query_one("#booklet-vertical").mount(Horizontal(
                Static("Options", classes="command-options"),
                classes="command-horizontal-options"
                )
            )

            for k, v in options.items():

                if v[0].startswith("<"):
                    stringa_pulita = v[0].replace("<", "").replace(">", "").replace(".", "")
                    elementi = len(stringa_pulita.split())

                    type = Static(f"[b][yellow]{v[0]}[/]", name=f"{stringa_pulita}")
                    type.styles.width = 10
                    type.styles.border = ("blank", "red")

                    self.query_one("#booklet-vertical").mount(Container(
                        Static(f"[b][cyan]{k}[/][/]", classes="name", id=f"--{k}"),
                        type,
                        Static(f"[b]{' '.join(v[1:])}[/]", classes="description"),
                        id=f"{k}",
                        classes="booklet-horizontal"
                        )
                    )
                    for i in range(elementi):
                        self.query_one(f"#{k}").mount(
                                Input(placeholder=f"{i+1}°...", classes="input", id=f"--{k}_{i+1}", name="input"),
                        )

                elif v[0] != "BOOLEAN":
                    type = Static(f"[b][yellow]{v[0]}[/]", name=f"{v[0]}")
                    type.styles.width = 10
                    type.styles.border = ("blank", "red")
                    self.query_one("#booklet-vertical").mount(Container(
                        Static(f"[b][cyan]{k}[/][/]", classes="name", id=f"--{k}"),
                        type,
                        Static(f"[b]{' '.join(v[1:])}[/]", classes="description"),
                        Input(placeholder=f"{k}....", classes="input", name="input"),
                        Button("one more", classes="buttons", id=f"one_more-{index}"),
                        classes="booklet-horizontal",
                        id=f"container-{index}"
                        )
                    )
                    index += 1

                else:
                    self.query_one("#booklet-vertical").mount(Horizontal(
                        Static(f"[b][cyan]{k}[/][/]", classes="name", id=f"--{k}"),
                        Static(f"[b][yellow]{v[0]}[/]", classes="types", name="BOOLEAN"),
                        Static(f"[b]{' '.join(v[1:])}[/]", classes="description"),
                        Checkbox(name="checkbox"),
                        classes="booklet-horizontal"
                        )
                    )
                    index += 1

        if len(arguments) == 0 and len(options) == 0:
            self.mount(Container(
                            Horizontal(Static("[bold][yellow]No arguments or options needed !!!\n")),
                            Horizontal(
                                Static(f"[bold] [#E1C699]{self.description}", id="description"),
                                Button("[bold]Show", id=f"show-{self.identifier}", classes="run"),
                            ),
                            classes="empty"
                    )
            )

        else:
            self.query_one("#booklet-vertical").mount(
                Horizontal(
                    Button("show", id=f"show-{self.identifier}", classes="run"),
                    classes="booklet-horizontal-button",
                    )
            )

    def on_input_submitted(self, event: Input.Submitted):
        event.input.action_cursor_left()



    BINDINGS = [
        Binding(key="r", action="app.pop_screen", description="return"),
    ]