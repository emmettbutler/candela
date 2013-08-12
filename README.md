![](http://www.gnu.org/graphics/gplv3-127x51.png)

**Candela** is a simple shell-building system that uses python and curses to
help developers create customized command line interfaces. It has a simple
interface, is well documented, and allows developers to take command-based
tools to the next level of complexity and usability.

This is free software, and you are welcome to redistribute it
under certain conditions. See the
[free software definition](http://www.gnu.org/philosophy/free-sw.html) for details

Features
--------

* Commands are 100% python and can run aribtrary code
* Commands can run code in secondary threads for asynchronous operation
* Customizable tab completion hooks for command arguments
* Customizable key event callbacks for reacting to each keypress event
* Responsive layout for smaller terminals
* Numerous built-in command templates
* Simple command syntax and help system
* "stickers" allow persistent information display
* Automatically generated command validation
* Up/Down arrows cycle through history
* Copy/Paste, insert text mode
* Easy transitions between menus
* Supports both named and positional command arguments

Example Shell
-------------

There is an example shell project in `shell_example.py`. To run it, use

    python shell_example.py

in a maximized terminal window.

Download
--------

Download the source from PyPI with

    pip install candela

You can also clone this repo to take a closer look at the code and demo app.

    git clone https://github.com/emmett9001/candela.git

Then, install the library with

    python setup.py install

Basic Use
---------

Importing
---------

Import Candela commands, menus, and the shell

    from candela.shell import Shell
    from candela.menu import Menu
    from candela.command import Command
    from candela import constants

Alternatively, you can simply `import candela` and reference the components
with `candela.shell.Shell`, etc.

Subclass Shell
--------------

Every Candela app is built as a subclass of `candela.shell.Shell`. A `Shell`
initialization follows this general outline:

* Set `self.name`
* Set `self.header`
* Define and instantiate `Command`s
* Define and instantiate `Menu`s
* Add `Command`s to `Menu`s
* Set `self.menus` to contain instantiated `Menu`s
* Set `self.menu` to be the name of the default menu

Commands
--------

In general, a command instantiation looks like this

    com = Command('first_command an_arg <-f reqd_arg>', 'Intro to commands')
    def _run(*args, **kwargs):
        # do anything
        return constants.CHOICE_VALID
    com.run = _run

Functions that execute on command invocation are modeled as python first-class
functions (callbacks).

Running the Shell
-----------------

Once you've set up some commands and menus, you can create a runnable python
script with your shell by using

    if __name__ == "__main__":
        MyShell().main_loop().end()

Advanced Use
------------

Please see the
[shell example](https://github.com/emmett9001/candela/blob/master/shell_example.py)
for a full walkthrough of how to use Candela. This example is both
well-commented and an instructional app demonstrating Candela's features.

Name
----

The name "Candela" was chosen after Spanish architect
[Felix Candela](http://en.wikipedia.org/wiki/F%C3%A9lix_Candela), who
pioneered the technique of building shell-shaped structures out of reinforced
concrete. He is sometimes known as the "shell builder".

Support
-------

If you need help using Candela, or have found a bug, please create an issue on
the [Github repo](https://github.com/emmett9001/candela/issues).

License
-------

    This file is part of Candela.

    Candela is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Candela is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Candela.  If not, see <http://www.gnu.org/licenses/>.
