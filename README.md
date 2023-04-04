# typer-to-texual

**typer-to-textual** is a TUI developed through the Textual module, which aims to simplify 
the use of applications. This tool analyzes the help screens of different typer applications and creates 
a TUI that allows the user to select the desired commands and options easily and intuitively, without the 
need to know all available commands and options by heart. In summary, the use of the interactive TUI 
represents a major step forward in simplifying the use of typer applications and making them more accessible 
to all users, even the less experienced ones.

## Install

As a preliminary requirement, you need to install some utility:

**xdotool**. Installs the package via prompt with the command: 'sudo apt-get install xdotool'

After that, you can proceed either via PyPI, or by cloning the repository and install dependencies.
If you opt for PyPI, run the following command:
```bash
$ pip install typer-to-textual
```

After that, **typer-to-textual** can be run with:
```bash
$ python3 -m typer-to-textual [typer_application]
```

If you instead opt for the repository, you also need the [Poetry](https://python-poetry.org/) Python package manager.
On Debian-like OSes it can be installed with the following command:
```bash
$ sudo apt install python3-poetry
```
After that, run the following commands:
```bash
$ git clone https://github.com/palla98/typer-to-textual.git
```

after downloading:
```bash
$ cd typer-to-textual

$ poetry install
```

After that, **typer-to-textual** can be run with:
```bash
$ poetry run ./typer_to_textual.py [typer_application]
```
