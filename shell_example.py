import getpass

from shellbuilder.shell import Shell
from shellbuilder.menu import Menu
from shellbuilder.command import Command, QuitCommand
from shellbuilder import constants


class MyShell(Shell):
    def __init__(self):
        Shell.__init__(self)

        self.name = "My Shell"

        # set the header that appears in the top left of the shell
        self.header = "My Cool Shell"

        # place sticky text on the top right side of the shell
        # you can change this text by calling sticker() from a command
        self.sticker("Welcome, %s" % getpass.getuser())

        # define commands
        hello_world_com = self.build_hello_command()
        complex_com = self.build_complex_command()
        invalid_com = self.build_invalid_command()
        quit_com = self.build_quit_command()

        # define menus
        main_menu = Menu('main')
        #menu display title
        main_menu.title = "Main menu"
        # list of Command objects making up menu
        main_menu.commands = [hello_world_com, complex_com, invalid_com, quit_com]

        # list of menus
        self.menus = [main_menu]
        # default menu
        self.menu = 'main'

    def build_hello_command(self):
        com = Command('sayhello', 'Print a friendly greeting')
        def _run(tokens):
            for token in tokens:
                self.put(token)
            self.put("Hello, world!")
            return constants.CHOICE_VALID
        com.run = _run
        return com

    def build_invalid_command(self):
        com = Command('nope', 'I do not run')
        def _run(tokens):
            self.put("Who cares?")
            return constants.CHOICE_VALID
        com.run = _run

        def _val(tokens):
            return (False, "Command failed because I said so")
        com.validate = _val

        return com

    def build_complex_command(self):
        com = Command('meaning_of_life', 'Find the meaning of life')
        def _run(tokens):
            if len(tokens) > 1 and tokens[1] == "and_everything":
                self.put(self.do_something_complex())
            else:
                self.put("Wouldn't you like to know")
            return constants.CHOICE_VALID
        com.run = _run
        return com

    def build_quit_command(self):
        quit_com = QuitCommand(self.name)
        quit_com.alias('q')
        return quit_com

    def do_something_complex(self):
        # magic, mystery, arbitrary python code here
        self.put("Missingno")
        return 42


if __name__ == "__main__":
    MyShell().main_loop().end()
