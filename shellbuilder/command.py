import constants


class Command(object):
    def __init__(self, definition, description):
        self.name = definition.split()[0]
        self.aliases = []

        self.definition = definition
        self.description = description

        self.args,self.kwargs = self.parse_definition(definition.split())

        def runner(*args, **kwargs):
            return constants.CHOICE_VALID
        self.run = runner

        def validator(*args, **kwargs):
            required_params = list(self.args)
            for kw in self.kwargs.keys():
                name,reqd = self.kwargs[kw]
                if reqd:
                    required_params.append(kw)
            if len(args) + len(kwargs) < len(required_params):
                return (False, "Missing arguments")
            for kw in self.kwargs.keys():
                name,reqd = self.kwargs[kw]
                if reqd and kw not in kwargs.keys():
                    return (False, "Missing argument %s (-%s) - %s" % (name, kw, kwargs))
            return (True, "")
        self.validate = validator

        self.new_menu = ''

    def parse_command(self, tokens):
        args = []
        kwargs = {}
        current_key = None
        parsing_named = False
        for token in tokens:
            if token == self.name:
                continue
            if "-" not in token:
                if not parsing_named:
                    args.append(token)
                else:
                    kwargs[current_key] = token
                    parsing_named = False
            else:
                if not parsing_named:
                    parsing_named = True
                    current_key = token.strip("-")
                else:
                    raise ParseException("Unexpected '-' in command input")
        if parsing_named:
            raise ParseException("Unexpected end of command input")
        return (args, kwargs)

    def parse_definition(self, tokens):
        args = []
        kwargs = {}  # key: (value, optional)
        parsing_optional = False
        parsing_reqd = False
        current_key = None
        for token in tokens:
            if token == self.name:
                continue
            if not any((spec_char in token) for spec_char in ["<", "]", "[", ">"]):
                args.append(token)
            else:
                if token.startswith("<"):
                    if not parsing_reqd:
                        current_key = token.strip("<-")
                        parsing_reqd = True
                    else:
                        raise ParseException("Encountered unexpected '<'")
                elif token.startswith("["):
                    if not parsing_optional:
                        current_key = token.strip("[-")
                        parsing_optional = True
                    else:
                        raise ParseException("Encountered unexpected '['")
                elif token.endswith(">"):
                    if parsing_reqd:
                        kwargs[current_key] = (token.strip(">"), True)
                        parsing_reqd = False
                    else:
                        raise ParseException("Encountered unexpected '>'")
                elif token.endswith("]"):
                    if parsing_optional:
                        kwargs[current_key] = (token.strip("]"), False)
                        parsing_optional = False
                    else:
                        raise ParseException("Encountered unexpected ']'")
        if parsing_optional or parsing_reqd:
            raise ParseException("Unexpected end of command definition")
        return (args, kwargs)


    def __str__(self):
        return "%s\n    %s" % (self.definition, self.description)

    def isoptional(self, token):
        if len(token.split()) != 2:
            return True
        return (self.isnamed(token) and token.startswith("[") and token.endswith("]"))

    def isnamed(self, token):
        return (len(token.split()) == 2 and token.split()[0].startswith("-"))

    def isrequired(self, token):
        return (token.startswith("<") and token.endswith(">"))

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

        def _run(*args, **kwargs):
            return constants.CHOICE_BACK
        self.run = _run

        self.default_run = _run


class QuitCommand(Command):
    def __init__(self, name):
        super(QuitCommand, self).__init__('quit', 'Quit %s' % name)

        def _run(*args, **kwargs):
            return constants.CHOICE_QUIT
        self.run = _run

        self.default_run = _run


class RunScriptCommand(Command):
    def __init__(self, shell):
        super(RunScriptCommand, self).__init__('run <scriptfile>', 'Run a script')

        self.shell = shell

        def _run(*args, **kwargs):
            self.shell.runscript(args[0])
        self.run = _run

        self.default_run = _run


class ParseException(Exception):
    pass
