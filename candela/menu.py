class Menu():
    """
    Simple representation of a menu: one state of the state machine
    created by Candela.
    Consists of a series of Commands
    One Shell instance may have one or more menus.
    """
    def __init__(self, name):
        self.name = name
        self.title = ''
        self.commands = []

    def options(self):
        """
        Return the string representations of the options for this menu
        """
        ret = ""
        for command in self.commands:
            ret += "%s\n" % str(command)
        return ret
