import constants


class Command(object):
    """
    The representation of a single command available to the user
    A command exists within one menu at a time.
    A single command object can be used in multiple menus.
    """
    def __init__(self, definition, description):
        """
        Creates a new generic command, setting the default functions for run()
        and validate().
        These two commands are called on each matched command during the main loop.
        First, validate() is called. If validate() returns True, then run() is
        called. These are the default implementations, and can be overridden.

        The default validation function simply parses the command definition and
        ensures that those arguments specified as required by that definition are
        present in a command input string.

        The default run function does nothing. It only returns the marker for
        command success and exits.

        The parser implements a specific syntax for required and optional arguments.
        See parse_definition() for details.

        Args:
        definition      - The definition string, following the specific syntax
                          detailed in the parse_definition() docstring
        description     - The human-readable description of what the command does
                          and how to use it
        """
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
        self.default_validate = validator

        # the menu to transfer to when the command returns CHOICE_VALID
        self.new_menu = ''

    def parse_command(self, tokens):
        """
        Parse a command input string into a series of tokens, and subsequently
        argument data.

        The syntax for a command input string is simple. It consists of the command
        name or alias followed by a sequence of space-separated tokens. A token
        can be either a single-letter flag prefixed with '-' or a word of
        abritrary length.

        Semantics of command input strings:
        command     ::= command_name ([flag] argument)*
        flag        ::= -(letter)
        argument    ::= (letter | digit | _)*
        command_name::= (letter | digit | _)*
        letter      ::= (lowercase | uppercase)*
        lowercase   ::= "a"..."z"
        uppercase   ::= "A"..."Z"
        digit       ::= "0"..."9"

        Args:
        tokens  - The list of tokens, the result of input_string.split()

        Returns the tuple of positional arguments and the dictionary of
        flag: arg_value pairs of keyword arguments
        """
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
        """
        Parse the command definition into a listing of required commands, to
        be used for validation

        The syntax of command definitions allows the specification of positional
        and named arguments. The named arguments can be required or optional. All
        positional arguments are required.

        Command definition semantics:
        definition      ::= command_name (positional)* (named)*
        command_name    ::= (letter | digit | _)*
        positional      ::= (letter | digit | _)*
        argument        ::= (letter | digit | _)*
        named           ::= (required | optional)
        required        ::= "<"flag argument">"
        optional        ::= "["flag argument"]"
        flag            ::= -(letter)
        letter          ::= (lowercase | uppercase)*
        lowercase       ::= "a"..."z"
        uppercase       ::= "A"..."Z"
        digit           ::= "0"..."9"

        More directly, this is an example command definition:
        my_command arg1 arg2 <-f im_required> [-o im_optional]
        You can also examine shell_example.py for more examples of command definitions

        Args:
        tokens  - The list of tokens, the result of definition.split()
        """
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
            raise ParseException("Unexpected end of command definition: %s" % (token))
        return (args, kwargs)


    def __str__(self):
        ret = "%s\n    %s" % (self.definition, self.description)
        if self.aliases:
            ret += "\n    Aliases: %s" % ",".join(self.aliases)
        return ret

    def alias(self, alias):
        """
        Create an alias for this command.
        An alias is simply an alternate name for the command.
        A command can be invoked by using any of its aliases or its name.

        Args:
        alias       - The string by which to alias this command
        """
        if alias not in self.aliases:
            self.aliases.append(alias)

class BackCommand(Command):
    """
    A command that, on success, reverts the latest new_menu action by resetting
    the shell to the previous menu.
    """
    def __init__(self, tomenu):
        super(BackCommand, self).__init__('back', 'Back to the %s menu' % tomenu)
        self.new_menu = tomenu

        def _run(*args, **kwargs):
            return constants.CHOICE_BACK
        self.run = _run

        self.default_run = _run


class QuitCommand(Command):
    """
    A command that, on success, quits the shell and cleans up the window.
    It does this by returning CHOICE_QUIT, which is the escape sequence
    for which the shell's main loop is listening.
    """
    def __init__(self, name):
        super(QuitCommand, self).__init__('quit', 'Quit %s' % name)

        def _run(*args, **kwargs):
            return constants.CHOICE_QUIT
        self.run = _run

        self.default_run = _run


class RunScriptCommand(Command):
    """
    A command that, on success, loads and runs a candela shell script.
    """
    def __init__(self, shell):
        super(RunScriptCommand, self).__init__('run scriptfile', 'Run a script')

        self.shell = shell

        def _run(*args, **kwargs):
            self.shell.runscript(args[0])
        self.run = _run

        self.default_run = _run


class ParseException(Exception):
    pass
