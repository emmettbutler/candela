import constants


class Command(object):
    def __init__(self, definition, description):
        self.definition = definition
        self.description = description

        def runner(tokens):
            return constants.CHOICE_VALID
        self.run = runner

        def validator(tokens):
            required_params = [token for token in self.definition.split() if token.startswith("<") and token.endswith(">")]
            if len(tokens) - 1 < len(required_params):
                return (False, "Missing arguments")
            return (True, "")
        self.validate = validator

        self.name = definition.split()[0]

        self.new_menu = ''
        self.aliases = []

    def __str__(self):
        return "%s\n    %s" % (self.definition, self.description)

    def alias(self, alias):
        if alias not in self.aliases:
            self.aliases.append(alias)

    def num_required_args(self):
        counter = 0
        for token in self.definition.split():
            if token.startswith("<") and token.endswith(">"):
                counter += 1
        return counter


class BackCommand(Command):
    def __init__(self, tomenu):
        super(BackCommand, self).__init__('back', 'Back to the %s menu' % tomenu)
        self.new_menu = tomenu

        def _run(tokens):
            return constants.CHOICE_BACK
        self.run = _run

        self.default_run = _run


class QuitCommand(Command):
    def __init__(self, name):
        super(QuitCommand, self).__init__('quit', 'Quit %s' % name)

        def _run(tokens):
            return constants.CHOICE_QUIT
        self.run = _run

        self.default_run = _run


class RunScriptCommand(Command):
    def __init__(self, shell):
        super(RunScriptCommand, self).__init__('run <scriptfile>', 'Run a script')

        self.shell = shell

        def _run(tokens):
            self.shell.runscript(tokens[1])
        self.run = _run

        self.default_run = _run
