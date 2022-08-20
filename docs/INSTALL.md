# Installation Guide

## Prerequisites

- Windows | macOS | Linux
- Python 3.8
- Futu ID and Trading Account
- FutuOpenD 6.1.2608

## Setting Up the Virtual Environment

**Step 1:** Download and install conda from the [official website](https://conda.io/projects/conda/en/latest/user-guide/install/index.html). (If you prefer the light-weight miniconda, you can also install it from the [miniconda website](https://docs.conda.io/en/latest/miniconda.html).)

**Step 2:** Run the following command on terminal to create a conda virtual environment and activate it:

```shell
conda create -n futubot python=3.8 -y
conda activate futubot
```

## Installing FutuBot

Install FutuBot from source in order to run it on your virtual environment:

```shell
git clone https://github.com/quincylin1/FutuBot.git
cd FutuBot
pip install -r requirements.txt
pip install -v -e .
# "-v" for verbose option.
# "-e" means installing the project in editable mode,
# so any local modifications on the project can be used without reinstalling it.
```
