
from textual.app import ComposeResult
from textual.widgets import Static, Button, Footer, Input, Checkbox
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen


class Header(Static):
    pass


class HomePage(Screen):

    def __init__(self, output) -> None:
        self.output = output
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
                        types = ["INTEGER", "FLOAT", "TEXT", "[", "<", "UUID", "PATH", "FILENAME", "BOOLEAN"]
                        if not any(words[1].replace('[', '(').replace('<', '(').startswith(t) for t in types):
                            words.insert(1, "BOOLEAN")

                    if len(words) == 2:
                        words.append("No description")

                    for i in range(2, len(words)):
                        words[i] = words[i].replace('[', '(').replace(']', ')')

                    options[words[0]] = words[1:]

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
                commands.append(words)

        return options, commands

    def compose(self) -> ComposeResult:
        yield Header("Homepage", classes="header")
        yield Footer()

    def on_mount(self) -> None:

        title = self.title()
        self.mount(Static(f"[green][bold]{title}", classes="title"))
        self.mount(Vertical(id="homepage-vertical"))

        options, commands = self.parse_output()

        if options:
            self.query_one(Vertical).mount(Horizontal(
                    Static("Options", classes="options"),
                    classes="homepage-horizontal-options"
                )
            )
            for k, v in options.items():
                if v[0] == "BOOLEAN":
                    self.query_one(Vertical).mount(Horizontal(
                        Static(f"[bold]{k}:", classes="checkbox-name"),
                        Checkbox(id=f"--{k}"),
                        Static(f"[bold]{v[1]}"),
                        classes="homepage-horizontal-bool"
                    ))
                else:
                    if k == "password":
                        self.query_one(Vertical).mount(Horizontal(
                            Input(placeholder=f"{k}....", password=True, id=f"--{k}"),
                            Static(f"[bold]{v[1]}"),
                            classes="homepage-horizontal"
                        ))
                    else:
                        self.query_one(Vertical).mount(Horizontal(
                            Input(placeholder=f"{k}....", id=f"--{k}"),
                            Static(f"[bold]{v[1]}"),
                            classes="homepage-horizontal"
                        ))

        if commands:
            self.query_one(Vertical).mount(Horizontal(
                Static("Commands", id="commands"),
                classes="homepage-horizontal-commands"
                )
            )
            for command in commands:
                self.query_one(Vertical).mount(Horizontal(
                    Button(f"{command[0]}", id=f"{command[0]}"),
                    Static(f"[bold][#E1C699]{command[1]}", classes="homepage-static-buttons"),
                    classes="homepage-horizontal"
                ))
