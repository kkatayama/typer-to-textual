from textual.app import ComposeResult
from textual.binding import Binding
from textual.widgets import Static, Button, Footer, Input, Checkbox
from textual.containers import Container, Horizontal
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
                required = False
                items = line.split(" ")
                words = []
                current_word = ""
                for option in items:
                    if option and option != '│' and option != '*':
                        current_word += " " + option
                    else:
                        if option == '*':
                            required = True
                        words.append(current_word.strip())
                        current_word = ""

                words = list(filter(bool, words))
                if len(words) == 2:
                    words.insert(1, " ")
                if words:
                    words[0] = words[0].replace('--', '')
                    words[2] = words[2].replace('[', '(').replace(']', ')')
                    if required:
                        words[2] += '*'
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
                required = False
                items = line.split(" ")
                words = []
                current_word = ""
                for option in items:
                    if option and option != '│' and option != '*':
                        current_word += " " + option
                    else:
                        if option == '*':
                            required = True
                        words.append(current_word.strip())
                        current_word = ""

                words = list(filter(bool, words))

                if words:

                    if not words[0].startswith("--") or words[0].split(",")[0].replace('--', '') == "help":
                        continue

                    words[0] = words[0].split(",")[0].replace('--', '')

                    if len(words) > 1 and words[1].startswith("-"):
                        words.remove(words[1])

                    if len(words) == 1:
                        words.append("BOOLEAN")

                    if len(words) == 2:
                        types = ["INTEGER", "FLOAT", "TEXT", "TUPLE", "UUID", "PATH", "FILENAME", "BOOLEAN"]
                        if not any(words[1].replace('[', '(').replace('<', '(').startswith(t) for t in types):
                            words.insert(1, "BOOLEAN")
                        words.append("No description")

                    for i in range(2, len(words)):
                        words[i] = words[i].replace('[', '(').replace(']', ')')
                        if required:
                            words[i] += '*'

                    options[words[0]] = words[1:]

        return options

    def on_mount(self) -> None:

        arguments = self.arguments()
        options = self.options()

        if len(arguments) != 0 or len(options) != 0:
            self.mount(Container(id="command-vertical"))

        index = 1

        if len(arguments) != 0:

            self.query_one("#command-vertical").mount(Horizontal(
                Static("Arguments", classes="command-arguments"),
                classes="command-options-bar"
                )
            )

            for k, v in arguments.items():

                description = f"{' '.join(v[1:])}"
                id = f"--argument--{k}"
                if "*" in description:
                    description = description.replace("(required)", "").replace("*", "")
                    id = f"--argument--{k}-required"
                    description = Static(f"[b]{description} [red]required[/red][/]", classes="description")
                else:
                    description = Static(f"[b]{description}[/]", classes="description")

                self.query_one("#command-vertical").mount(Container(
                    Static(f"[b][cyan]{k}[/][/]", classes="name", id=f"{id}"),
                    Static(f"[b][yellow]{v[0]}[/]", name=f"{v[0]}", classes="type"),
                    description,
                    Input(placeholder=f"...", classes="input", name="input"),
                    Button("one more", classes="buttons", id=f"one_more&{self.identifier}&{index}"),
                    classes="command-horizontal",
                    id=f"container-{index}"
                    )
                )
                index += 1

        if len(options) != 0:

            self.query_one("#command-vertical").mount(Horizontal(
                Static("Options", classes="command-options"),
                classes="command-options-bar"
                )
            )

            for k, v in options.items():

                if v[0].startswith("<"):
                    clean_string = v[0].replace("<", "").replace(">", "").replace(".", "")
                    elements = len(clean_string.split())

                    self.query_one("#command-vertical").mount(Container(
                        Static(f"[b][cyan]{k}[/][/]", classes="name", id=f"--{k}"),
                        Static(f"[b][yellow]{v[0]}[/]", name=f"{clean_string}", classes="type"),
                        Static(f"[b]{' '.join(v[1:])}[/]", classes="description"),
                        id=f"{k}",
                        classes="command-horizontal"
                        )
                    )
                    for i in range(elements):
                        self.query_one(f"#{k}").mount(
                                Input(placeholder=f"{i+1}°", classes="input", id=f"--{k}_{i+1}", name="input"),
                        )

                elif v[0] != "BOOLEAN":
                    description = f"{' '.join(v[1:])}"
                    id = k
                    if "*" in description:
                        description = description.replace("(required)", "").replace("*", "")
                        id = k + "-required"
                        description = Static(f"[b]{description} [red]required[/red][/]", classes="description")
                    else:
                        description = Static(f"[b]{description}[/]", classes="description")

                    self.query_one("#command-vertical").mount(Container(
                        Static(f"[b][cyan]{k}[/][/]", classes="name", id=f"--{id}"),
                        Static(f"[b][yellow]{v[0]}[/]", name=f"{v[0]}", classes="type"),
                        description,
                        Input(placeholder=f"...", classes="input", name="input"),
                        Button("one more", classes="buttons", id=f"one_more&{self.identifier}&{index}"),
                        classes="command-horizontal",
                        id=f"container-{index}"
                        )
                    )
                    index += 1

                else:
                    self.query_one("#command-vertical").mount(Horizontal(
                        Static(f"[b][cyan]{k}[/][/]", classes="name", id=f"--{k}"),
                        Static(f"[b][yellow]{v[0]}[/]", classes="type", name="BOOLEAN"),
                        Static(f"[b]{' '.join(v[1:])}[/]", classes="description"),
                        Checkbox(name="checkbox"),
                        classes="command-horizontal"
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
            self.query_one("#command-vertical").mount(
                Horizontal(
                    Button("show", id=f"show-{self.identifier}", classes="run"),
                    classes="command-horizontal-run",
                    )
            )

    BINDINGS = [
        Binding(key="r", action="app.pop_screen_n('command')", description="return"),
    ]