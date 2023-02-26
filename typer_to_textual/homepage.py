
from textual.app import ComposeResult
from textual.widgets import Static, Button, Footer, Input, Checkbox
from textual.containers import Container, Horizontal
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
        if title == "":
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
                    words[2] = words[2].replace('[', '(').replace(']', ')')
                    if words[0] == "help":
                        continue
                    options[words[0]] = [words[1], words[2]]
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
        yield Container(
            id="homepage"
        )
        yield Footer()

    def on_mount(self) -> None:

        title = self.title()
        self.query_one(Container).mount(Static(f"[green][bold]{title}", classes="title"))

        options, commands = self.parse_output()
        self.query_one(Container).mount(Container(id="interno"))

        if options:
            self.query_one("#interno").mount(Static("Options", id="options"))
            for k, v in options.items():
                if v[0] == "BOOLEAN":
                    self.query_one("#interno").mount(Horizontal(
                        Static(f"[bold]{v[1]}"),
                        Checkbox(id=f"--{k}"),
                        classes="commands-horizontal"
                    ))
                else:
                    if k == "password":
                        self.query_one("#interno").mount(Horizontal(
                            Input(placeholder=f"{k}....", password=True, id=f"--{k}"),
                            Static(f"[bold]{v[1]}"),
                            classes="commands-horizontal"
                        ))
                    else:
                        self.query_one("#interno").mount(Horizontal(
                            Input(placeholder=f"{k}....", id=f"--{k}"),
                            Static(f"[bold]{v[1]}"),
                            classes="commands-horizontal"
                        ))

        if commands:
            self.query_one("#interno").mount(Static("Commands", id="commands"))
            if options:
                self.query_one("#commands").styles.margin = (5, 0, 0, 1)
            for command in commands:
                self.query_one("#interno").mount(Horizontal(
                    Button(f"{command[0]}", id=f"{command[0]}"),
                    Static(f"[bold][#E1C699]{command[1]}"),
                    classes="commands-horizontal"
                ))
