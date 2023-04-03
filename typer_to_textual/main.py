import sys
import subprocess

from textual.app import App
from textual.binding import Binding
from textual.widgets import Button, Input
from textual import events
from textual.pilot import Pilot

from rich.console import Console
from typing import Tuple, List

from typer_to_textual.command_options import CommandOptions
from typer_to_textual.homepage import HomePage
from typer_to_textual.show import Show


def maximize() -> None:
    result = subprocess.run(["xdotool", "getactivewindow"], capture_output=True)
    window_id = result.stdout.decode().strip()

    # Get the screen resolution
    res = subprocess.check_output("xrandr | grep '\*' | awk '{print $1}'", shell=True).decode().strip().split('x')
    screen_width = int(res[0])
    screen_height = int(res[1])

    # Determine the window size based on screen resolution
    if screen_width <= 1366 and screen_height <= 768:
        window_size = "80%"
    else:
        window_size = "70%"

    subprocess.run(["xdotool", "windowsize", window_id, window_size, window_size])

    # Calculate the window position to center it on the screen
    window_width = int(window_size[:-1]) / 100 * screen_width
    window_height = int(window_size[:-1]) / 100 * screen_height
    x_pos = int((screen_width - window_width) / 2)
    y_pos = int((screen_height - window_height) / 2)

    # Move the window to the calculated position
    subprocess.run(["xdotool", "windowmove", window_id, str(x_pos), str(y_pos)])


def homepage_output() -> Tuple[List[str], str]:

    if len(sys.argv) != 2:
        Console().print("[bold][red]Error[/red]: Pass only the name of application")
        sys.exit(1)

    application = sys.argv[1]
    command = application.split()
    command.append("--help")
    maximize()

    try:
        result = subprocess.run(command, capture_output=True)
        if len(result.stdout.decode().split('\n')) == 1:
            Console().print(f"[bold][red]Error[/red]: The application: '{application}' is not found")
            sys.exit(1)
        return result.stdout.decode().split('\n'), application
    except FileNotFoundError:
        Console().print(f"[bold][red]Error[/red]: The application: '{application}' is not found")
        sys.exit(1)


class Tui(App):

    def __init__(self) -> None:
        self.output, self.application = homepage_output()
        super().__init__()

    CSS_PATH = "style.css"

    BINDINGS = [
        Binding(key="escape", action="key_escape", description="exit"),
    ]

    def on_mount(self) -> None:
        self.install_screen(HomePage(self.output, "homepage"), name="homepage")
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

    def call_command(self, command: str, homepage_data) -> List[str]:

        maximize()

        args = [self.application]

        for option in homepage_data:
            args.append(option)

        args.append(command)
        args.append("--help")

        result = subprocess.run(args, capture_output=True)

        return result.stdout.decode().split('\n')

    def command_buttons(self):
        start_commands = False
        buttons = {}
        for index, line in enumerate(self.output, start=1):

            if "Commands" in line:
                start_commands = True
                continue

            if start_commands and any(word.isalpha() for word in line.split()):
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
                buttons[words[0]] = words[1]

        return buttons

    def check(self, elements: str, id: str):

        validation_errors = False

        screen_class = "HomePage" if id == "homepage" else "CommandOptions"

        for screens in self.query(f"{screen_class}"):
            if screens.identifier == id:
                for element in screens.query(f".{elements}"):
                    input_type = ''
                    tuple_types = []

                    for index, static_element in enumerate(element.query("Static"), start=1):
                        if index == 2 and static_element.name != "BOOLEAN":
                            tuple_types = static_element.name.split(" ")
                            if len(tuple_types) == 1:
                                if tuple_types[0] == "INTEGER":
                                    input_type = "INTEGER"
                                elif tuple_types[0] == "FLOAT":
                                    input_type = "FLOAT"
                                else:
                                    input_type = "TEXT"
                            elif static_element.name.startswith("<"):
                                input_type = "TUPLE"
                            else:
                                input_type = "ARGUMENT"

                    if input_type == "ARGUMENT":
                        break

                    if input_type == "INTEGER" or input_type == "FLOAT":
                        for input_element in element.query(".input"):
                            try:
                                if input_element.value != "":
                                    if input_type == "INTEGER":
                                        int(input_element.value)
                                    else:
                                        float(input_element.value)
                                input_element.styles.border = None
                            except ValueError:
                                validation_errors = True
                                input_element.styles.border = ("tall", "red")

                    elif input_type == "TUPLE":
                        for index, input_element in enumerate(element.query(".input")):
                            expected_type = {
                                "INTEGER": int,
                                "TEXT": str,
                                "FLOAT": float
                            }.get(tuple_types[index], None)

                            try:
                                if input_element.value != "":
                                    expected_type(input_element.value)
                                input_element.styles.border = None
                            except ValueError:
                                validation_errors = True
                                input_element.styles.border = ("tall", "red")

                for element in screens.query(f".{elements}"):
                    for index, e in enumerate(element.query("Static"), start=1):
                        if index == 1:
                            key = e.id
                            if "-required" in key:
                                for input_element in element.query(".input"):
                                    if input_element.value == "":
                                        validation_errors = True
                                        input_element.styles.border = ("tall", "red")
                                    else:
                                        input_element.styles.border = None

        return validation_errors

    def homePage_field(self) -> list:

        homepage_data = []
        for element in self.query_one(HomePage).query(".homepage-horizontal"):
            key = element.query_one(".name").id.replace("-required", "")
            if len(element.query("Input")) > 0:
                for index, i in enumerate(element.query("Input"), start=1):
                    if i.value != '':
                        homepage_data.append(key)
                        homepage_data.append(i.value)
            else:
                for index, i in enumerate(element.query("Checkbox"), start=1):
                    if str(i.value) == "True":
                        homepage_data.append(key)

        return homepage_data

    def commandPage_field(self, command):

        tuple_data = {}
        other_data = []
        command = command.replace("show-", "")
        for screens in self.query(CommandOptions):
            if screens.identifier == command:
                for element in screens.query(".command-horizontal"):
                    key = element.query_one(".name").id
                    if len(element.query(".input")) > 0:
                        if "-required" in key:
                            key = key.replace("-required", "")
                        diversi = len(set(i.placeholder for i in element.query(".input"))) > 1
                        if diversi:
                            for index, i in enumerate(element.query(".input"), start=1):
                                if i.value != '':
                                    if key not in tuple_data:
                                        tuple_data[key] = [i.value]
                                    else:
                                        tuple_data[key].append(i.value)
                        else:
                            for index, i in enumerate(element.query(".input"), start=1):
                                if "--argument--" in key and i.value != '':
                                    other_data.append(i.value)
                                elif i.value != '':
                                    other_data.append(key)
                                    other_data.append(i.value)
                    else:
                        if "-required" in key:
                            key = key.replace("-required", "")
                        if str(element.query_one("Checkbox").value) == "True":
                            tuple_data[key] = "BOOL"

        return tuple_data, other_data

    def on_button_pressed(self, event: Button.Pressed):

        values = self.command_buttons()
        buttons = values.keys()

        if event.button.id in buttons:

            validation_errors = self.check("homepage-horizontal", "homepage")
            if validation_errors:
                return

            description = values[event.button.id]
            homepage_data = self.homePage_field()

            if not self.is_screen_installed(event.button.id):
                result = self.call_command(event.button.id, homepage_data)
                self.install_screen(CommandOptions(result, event.button.id, description), name=event.button.id)
            self.push_screen(event.button.id)

        elif event.button.id.startswith("show-"):

            command = event.button.id.replace("show-", "")
            validation_errors = self.check("command-horizontal", command)
            if validation_errors:
                return

            homepage_data = self.homePage_field()
            tuple_data, other_data = self.commandPage_field(command)

            if not self.is_screen_installed(event.button.id):
                self.install_screen(Show(self.application, command, homepage_data, tuple_data, other_data), name=event.button.id)
            self.push_screen(event.button.id)

        elif event.button.id.startswith("one_"):

            id, index = event.button.id.split("&")[1:]
            for screens in self.query(CommandOptions):
                if screens.identifier == id:
                    container = screens.query_one(f"#container-{index}")
                    input_elements = container.query("Input")
                    if event.button.id.startswith("one_more"):
                        if len(input_elements) == 1:
                            container.mount(Button("one less", classes="buttons", id=f"one_less&{id}&{index}"), after=4)
                        input_element = Input(placeholder=f"...", classes="input")
                        container.mount(input_element, before=3)
                    elif event.button.id.startswith("one_less") and len(input_elements) > 1:
                        input_elements.first().remove()
                        if len(container.query("Input")) == 1:
                            container.query("Button").last().remove()

    async def action_pop_screen_n(self, screen):

        input_has_focus = any(i.has_focus for i in self.query("Input"))

        if input_has_focus:
            for i in self.query("Input"):
                if i.has_focus:
                    i.value = i.value + 'r'
                    pilot = Pilot(self)
                    await pilot.press("right")
                    break
        else:
            if screen == "show":
                self.uninstall_screen(self.pop_screen())
            else:
                self.pop_screen()



