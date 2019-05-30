# orbital-debris-cleaning
# Game orbital debris cleaning

A small game written on an asynchronous Python. The project is a training, to hone the skills of asynchronous programming.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

Use pyenv and virtualenv plugin insulation project. Pyenv example:
```
$ python virtualevn myenv
$ source myenv/bin/activate
```

Install requirements:

```
pip install -r requirements.txt
```


### Prerequisites

Install [pyenv](https://github.com/pyenv/pyenv) and [pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv) plugin.

### Installing

Сreate a working directory and go into it.

```
$ mkdir project && cd project
```

To create a virtualenv for the Python version used with `pyenv`, run `pyenv virtualenv`, specifying the Python version you want and the name of the virtualenv directory. For example,
Run in terminal for Ubuntu.
```bash
$ pyenv versions
$ 3.7.2
$ pyenv virtualenv 3.7.2 async_project
$ source /home/user/.pyenv/versions/async_project/bin/activate
```
```bash
$ git clone https://github.com/DjaPy/orbital-debris-cleaning.git
```

Install dependencies.

```bash
$ pip install -r requariments.txt

```

### Running

Run game.

```bash
$ python save_the_planet.py
```

Move the ship with the cursor. Fly around garbage. 

### Conclusion

Have a good trip to space ;) !

