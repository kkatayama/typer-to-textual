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

se però [typer_application] è '**python3 -m [nome_modulo]**' bisogna stare attenti perchè si utlizza
l'interprete Python dell'ambiente virtuale creato da Poetry. Quindi bisogna andare ad installare 
[nome_modulo] nell'ambiente virtuale altrimenti non viene riconosciuto.

oppure semplicemente si può lanciare il comando:
```bash
python3 typer_to_textual.py 'python3 -m [nome_modulo]'
```

la cosa migliore è andare a creare uno script .sh in modo tale da passare direttamente un eseguibile
Lo si va a creare e salvare nella tua directory bin personale:
(~/.local/bin/[nome_script].sh):
```bash
sudo nano ~/.local/bin/[nome_script].sh
```

```bash
#!/bin/bash

OLD_PWD=$PWD

cd path/to/executable
poetry run ./executable "$@"
cd $PWD
```
In seguito renderlo eseguibile con questo comando:
```bash
sudo chmod +x ~/.local/bin/[nome_script].sh
```

e poi andare a creare un link simbolico:
```bash
sudo ln -s  ~/.local/bin/[nome_script].sh ~/.local/bin/[nome_script]
```
Dopodichè semplicemente basterà chiamare lo script digitando semplicemente il comando [nome_script]
da qualsiasi posizione nel terminale.

quindi si potrà usare typer-to-textual anche in questo modo senza avere problemi di ambiente virtuale:
```bash
poetry run ./typer_to_textual.py [nome_script]
```