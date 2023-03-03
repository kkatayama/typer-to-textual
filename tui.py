import sys
import subprocess

from textual.app import App
from textual.binding import Binding
from textual.containers import Horizontal
from textual.widgets import Button, Static, Input
from textual import events
from textual.pilot import Pilot

from typing import Tuple, List

from typer_to_textual.command_options import CommandOptions
from typer_to_textual.homepage import HomePage
from typer_to_textual.show import Show


def homepage_output() -> Tuple[List[str], str]:

    try:
        if len(sys.argv) != 2:
            raise RuntimeError("pass exactly two arguments")
    except RuntimeError as e:
        print(f"Error: {str(e)}")
        exit()

    application = sys.argv[1]

    result = subprocess.run(["xdotool", "getactivewindow"], capture_output=True)
    window_id = result.stdout.decode().strip()

    # ingrandisci la finestra corrente
    subprocess.run(["xdotool", "windowsize", window_id, "70%", "70%"])

    result = subprocess.run([application, "--help"], capture_output=True)

    return result.stdout.decode().split('\n'), application


class Tui(App):

    def __init__(self) -> None:
        self.output, self.application = homepage_output()
        super().__init__()

    CSS_PATH = "style.css"

    BINDINGS = [
        Binding(key="escape", action="key_escape", description="exit"),
    ]

    def on_mount(self) -> None:
        self.install_screen(HomePage(self.output), name="homepage")
        self.push_screen("homepage")

    async def on_key(self, event: events.Key):
        if event.key == "up":
            pilot = Pilot(self)
            #await pilot.press("enter")
            await pilot.press("shift+tab")
        if event.key == "down":
            pilot = Pilot(self)
            #await pilot.press("enter")
            await pilot.press("tab")

    def action_key_escape(self) -> None:
        self.exit()

    def call_button(self, command: str) -> List[str]:

        result = subprocess.run(["xdotool", "getactivewindow"], capture_output=True)
        window_id = result.stdout.decode().strip()

        # ingrandisci la finestra corrente
        subprocess.run(["xdotool", "windowsize", window_id, "70%", "70%"])

        result = subprocess.run([self.application, command, "--help"], capture_output=True)

        return result.stdout.decode().split('\n')

    def buttons(self):
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

    def on_button_pressed(self, event: Button.Pressed):

        values = self.buttons()
        buttons = values.keys()

        if event.button.id in buttons:

            description = values[event.button.id]
            if not self.is_screen_installed(event.button.id):
                result = self.call_button(event.button.id)
                self.install_screen(CommandOptions(result, event.button.id, description), name=event.button.id)
            self.push_screen(event.button.id)

        elif event.button.id.startswith("show-"):

            homepage_data = {}

            for element in self.query_one(HomePage).query():
                if element.name == "checkbox":
                    if str(element.value) == "True":
                        homepage_data[element.id] = "BOOL"
                elif element.name == "input":
                    if element.value != '':
                        homepage_data[element.id] = element.value

            command_data = {}
            lista = []
            almeno_uno = False

            for element in self.query(CommandOptions).last().query(".booklet-horizontal"):
                key = element.query_one(".name").id
                type = ''
                tupla = []
                for index, i in enumerate(element.query("Static"), start=1):
                    if index == 2 and i.name != "BOOLEAN":
                        tupla = i.name.split(" ")
                        if len(tupla) == 1:
                            if tupla[0] == "TEXT":
                                type = "TEXT"
                            elif tupla[0] == "INTEGER":
                                type = "INTEGER"
                            else:
                                type = "FLOAT"
                        else:
                            type = "TUPLE"

                if type == "INTEGER":
                    for i in element.query(".input"):
                        if i.value != '':
                            try:
                                converted_value = int(i.value)
                                if isinstance(converted_value, int):
                                    i.styles.border = ("blank", "red")
                            except ValueError:
                                almeno_uno = True
                                i.styles.border = ("tall", "red")

                elif type == "FLOAT":
                    for i in element.query(".input"):
                        if i.value != '':
                            try:
                                converted_value = float(i.value)
                                if isinstance(converted_value, float):
                                    i.styles.border = ("blank", "red")
                            except ValueError:
                                almeno_uno = True
                                i.styles.border = ("tall", "red")

                elif type == "TUPLE":
                    for index, i in enumerate(element.query(".input"), start=0):
                        if i.value != '':
                            tipo = tupla[index]
                            if tipo == "INTEGER":
                                tipo = 'int'
                            if tipo == "TEXT":
                                tipo = 'str'
                            if tipo == "FLOAT":
                                tipo = 'float'
                            try:
                                converted_value = eval(tipo)(i.value)
                                if isinstance(converted_value, eval(tipo)):
                                    i.styles.border = ("blank", "red")
                            except ValueError:
                                almeno_uno = True
                                i.styles.border = ("tall", "red")

                if len(element.query(".input")) > 0:
                    tmp = ''
                    diversi = False
                    for index, i in enumerate(element.query(".input"), start=1):
                        if index == 1:
                            tmp = i.placeholder
                        if index == 2:
                            if i.placeholder != tmp:
                                diversi = True
                    if diversi:
                        if len(element.query(".input")) > 0:
                            for index, i in enumerate(element.query(".input"), start=1):
                                if i.value != '':
                                    if index == 1:
                                        command_data[key] = [i.value]
                                    else:
                                        command_data[key].append(i.value)
                    elif not diversi:
                        for index, i in enumerate(element.query(".input"), start=1):
                            if i.value != '':
                                lista.append(key)
                                lista.append(i.value)
                else:
                    if str(element.query_one("Checkbox").value) == "True":
                        command_data[key] = "BOOL"

            command = event.button.id.replace("show-", "")

            if almeno_uno:
                return

            if not self.is_screen_installed(event.button.id):
                self.install_screen(Show(self.application, command, homepage_data, command_data, lista), name=event.button.id)
            self.push_screen(event.button.id)

        if event.button.id.startswith("one_more-"):
            index = event.button.id.split("-")[1]
            placeholder = self.query(CommandOptions).last().query_one(f"#container-{index}").query_one(".name").id.replace("--", "")
            self.query(CommandOptions).last().query_one(f"#container-{index}").mount(Input(placeholder=f"{placeholder}....", classes="input"), before=3)

    def action_pop_screen(self):
        self.uninstall_screen(self.pop_screen())


if __name__ == "__main__":
    Tui().run()
