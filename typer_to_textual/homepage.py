from textual.app import ComposeResult
from textual.widgets import Static, Button, Footer, Input, Checkbox
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen


class Header(Static):
    pass


class HomePage(Screen):

    def __init__(self, output, identifier) -> None:
        self.output = output
        self.identifier = identifier
        super().__init__()

    def title(self) -> str:
        title = ""
        for index, line in enumerate(self.output, start=1):
            if index == 4:
                title = line
                break
        if title == "" or "Options" in title:
            title = "User interface utility"

        return title.strip()

    def parse_output(self):

        start_options = False
        start_commands = False
        options = {}
        commands = []
        for index, line in enumerate(self.output, start=1):

            if "Options" in line:
                start_options = True
                continue
            if "Commands" in line:
                start_options = False
                start_commands = True
                continue
            if start_options:
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
                    if not words[0].startswith("--") or words[0].split(",")[0].replace('--', '') == "help":
                        continue
                    words[0] = words[0].split(",")[0].replace('--', '')
                    if words[0] != "help":
                        if len(words) > 1 and words[1].startswith("-"):
                            words.pop(1)
                        if len(words) == 1:
                            words.append("BOOLEAN")
                        if len(words) == 2 and not any(
                                words[1].replace('[', '(').replace('<', '(').startswith(t) for t in
                                ["INTEGER", "FLOAT", "TEXT", "<", "UUID", "PATH", "FILENAME", "BOOLEAN"]):
                            words.insert(1, "BOOLEAN")
                        words[2:] = [w.replace('[', '(').replace(']', ')') for w in words[2:]]
                        options[words[0]] = words[1:] + (["No description"] if len(words) == 2 else [])

            elif start_commands and any(word.isalpha() for word in line.split()):
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

                if words:
                    if len(words) == 1:
                        words.append("No description")

                commands.append(words)

        return options, commands

    def compose(self) -> ComposeResult:
        yield Header("Homepage", classes="header")
        yield Footer()

    def on_mount(self) -> None:

        global container

        title = self.title()
        self.mount(Static(f"[green][bold]{title}", classes="title"))
        self.mount(Vertical(id="homepage-vertical"))

        options, commands = self.parse_output()

        if options:
            self.query_one(Vertical).mount(Horizontal(
                    Static("Options"),
                    classes="homepage-options-bar"
                )
            )
            for k, v in options.items():

                if v[0] == "BOOLEAN":
                    container = Container(
                        Static(f"[cyan][bold]{k}", classes="name", id=f"--{k}"),
                        Static(f"[b][yellow]{v[0]}[/]", name=f"{v[0]}", classes="type"),
                        Static(f"[bold]{v[1]}", classes="description-bool"),
                        Checkbox(name="checkbox"),
                        classes="homepage-horizontal"
                    )
                elif not v[0].startswith("["):
                    description = v[1].replace("(required)", "").strip()
                    id = k if "(required)" not in v[1] else f"{k}-required"
                    required_label = " [red](required)[/red]" if "(required)" in v[1] else ""
                    description = Static(f"[bold]{description}{required_label}", classes="description")
                    is_password = True if k == "password" else False

                    container = Container(
                        Static(f"[cyan]{k}", classes="name", id=f"--{id}"),
                        Static(f"[b][yellow]{v[0]}[/]", name=f"{v[0]}", classes="type"),
                        description,
                        Input(placeholder=f"{k}", password=is_password, name=f"{v[0]}&{k}", classes="input"),
                        classes="homepage-horizontal"
                    )

                self.query_one(Vertical).mount(container)

        if commands:
            self.query_one(Vertical).mount(Horizontal(
                Static("Commands"),
                classes="homepage-commands-bar"
                )
            )
            for command in commands:
                button = Button(command[0], id=command[0])
                description = Static(f"[bold][#E1C699]{command[1]}")
                command_horizontal = Horizontal(button, description, classes="homepage-command")

                self.query_one(Vertical).mount(command_horizontal)
