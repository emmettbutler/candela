class Menu():
    def __init__(self, name):
        self.name = name
        self.title = ''
        self.commands = []

    def options(self):
        ret = ""
        for command in self.commands:
            ret += "%s\n" % str(command)
        return ret
