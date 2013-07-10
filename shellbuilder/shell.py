import curses
import sys
import threading

import constants


class Shell():
    def __init__(self, scriptfile=None):
        self.script_lines = self.parse_script_file(scriptfile)
        self.script_counter = 0
        self.scriptfile = ""

        self.stdscr = curses.initscr()
        self.stdscr.keypad(1)

        self.backbuffer = []
        self.height,self.width = self.stdscr.getmaxyx()

        self.menus = []
        self.stickers = []

        self.should_show_help = True

        self.header = ""
        self._header_bottom = 0
        self._header_right = 0

    def parse_script_file(self, filename):
        self.scriptfile = filename
        try:
            f = open(filename, 'r')
            script_lines = f.readlines()
            script_lines = [a.strip('\n') for a in script_lines]
            f.close()
        except Exception as e:
            return
        return script_lines

    def runscript(self, scriptfile):
        self.script_lines = self.parse_script_file(scriptfile)
        self.script_counter = 0

    def print_backbuffer(self):
        rev = list(self.backbuffer)
        rev.reverse()
        i = 0

        for string, iscommand in rev:
            ypos = self.height-2-i
            if ypos > 0:
                printstring = string
                if iscommand:
                    printstring = "> %s" % string
                self.stdscr.addstr(ypos,0,printstring)
            i += 1

    def sticker(self, output, new_output="", pos=None):
        if len(self.stickers) > 0:
            sort = sorted(self.stickers, key=lambda x: x[1][0])
            ht = sort[0][1][0]+1
        else:
            ht = 3

        if not pos:
            pos = (ht, self.width - 20)

        match = None
        for text,_pos in self.stickers:
            if output == text:
                match = (text,_pos)
                break
        if match:
            self.remove_sticker(match[0])

        sticker = (new_output or output, match[1] if match else pos)
        self.stickers.append(sticker)

        self.update_screen()

    def print_stickers(self):
        for text,pos in self.stickers:
            _y,_x = pos
            if _x + len(text) > self.width:
                _x = self.width - len(text) - 1
            self.stdscr.addstr(_y, _x, text)

    def remove_sticker(self, text):
        self.stickers = [a for a in self.stickers if a[0] != text]

    def print_header(self):
        ht = 0
        for line in self.header.split("\n"):
            self.stdscr.addstr(ht, 0, line)
            if len(line) > self._header_right:
                self._header_right = len(line)
            ht += 1
        self._header_bottom = ht

    def get_helpstring(self):
        _menu = self.get_menu()
        if not _menu:
            return

        helpstring = "\n\n" + _menu.title + "\n" + "-"*20 + "\n" + _menu.options()
        return helpstring

    def print_help(self):
        _helpstring = self.get_helpstring()
        if not _helpstring:
            return
        helpstrings = [" %s" % a for a in _helpstring.split("\n")]
        ht = 0
        longest = len(max(helpstrings, key=len))
        _x = self._header_right + 50
        if _x + longest > self.width:
            _x = self.width - longest - 1
        for line in helpstrings:
            self.stdscr.addstr(ht, _x, line + " "*15)
            ht += 1

    def put(self, output, command=False, pos=None):
        self.update_screen()

        if not output:
            return

        output = str(output)

        _x,_y = (self.height-1, 0)
        if pos:
            _x,_y = pos

        for line in output.split('\n'):
            # put the line
            self.stdscr.addstr(_x, _y, line)

            # add it to backbuffer
            backbuf_string = line
            to_append = (backbuf_string, command)
            if line != "> ":
                self.backbuffer.append(to_append)
                # TODO - stop backbuffer from growing huge

    def _input(self, prompt):
        self.put(prompt)
        keyin = ''
        buff = ''
        hist_counter = 1
        while keyin != 10:
            keyin = self.stdscr.getch()
            #self.stdscr.addstr(20, 70, str(keyin))
            if keyin in [127, 263]:  # backspaces
                buff = buff[:-1]
                self.stdscr.addstr(self.height-1, 0, " "*(self.width-3))
                self.stdscr.addstr(self.height-1, 0, "> %s" % buff)
            elif keyin in [curses.KEY_DOWN, curses.KEY_UP]:
                hist_counter,buff = self.process_history_command(keyin, hist_counter)
            elif keyin == curses.KEY_F1:
                curses.endwin()
                sys.exit()
            elif keyin >= 32 and keyin <= 126:
                buff += chr(keyin)
        self.put(buff, command=True)
        self.stdscr.refresh()
        return buff

    def process_history_command(self, keyin, hist_counter):
        hist_commands = [(s,c) for s,c in self.backbuffer if c]
        if not hist_commands:
            return

        #hist_commands.reverse()

        buff = hist_commands[-hist_counter][0]

        self.stdscr.addstr(self.height-1, 0, " "*(self.width-3))
        self.stdscr.addstr(self.height-1, 0, "> %s" % buff)

        if keyin == curses.KEY_UP and hist_counter < len(hist_commands):
            hist_counter += 1
        elif keyin == curses.KEY_DOWN and hist_counter > 0:
            hist_counter -= 1
        return hist_counter, buff

    def print_menu_header(self):
        self.put(self.get_helpstring())

    def script_in(self):
        if not self.script_lines:
            return None

        if self.script_counter < len(self.script_lines):
            command = self.script_lines[self.script_counter]
            self.script_counter += 1
        else:
            command = None
        return command

    def main_loop(self):
        """main shell IO loop:
        get an input command
        split into tokens
        find matching command
        validate tokens for command
        run command
        """
        ret_choice = None
        while ret_choice != constants.CHOICE_QUIT:
            ret_choice = constants.CHOICE_INVALID
            choice = self.script_in()
            if choice:
                self.put("> %s" % choice)
            else:
                choice = self._input("> ")
            tokens = choice.split()
            if len(tokens) == 0:
                self.put("\n")
                continue
            for command in self.get_menu().commands:
                if tokens[0] == command.name or tokens[0] in command.aliases:
                    success, message = command.validate(tokens)
                    if not success:
                        self.put(message)
                        break
                    else:
                        ret_choice = command.run(tokens)
                        if command.new_menu and ret_choice != constants.FAILURE:
                            self.menu = command.new_menu
            if success:
                if ret_choice == constants.CHOICE_INVALID:
                    self.put("Invalid command")

        return self

    def get_menu(self):
        if not self.menus: return
        return [a for a in self.menus if a.name == self.menu][0]

    def timeout(self, func, args=(), kwargs={}, timeout_duration=10, default=None):
        """create a new thread, run func in the thread for a max of
        timeout_duraction seconds"""
        class InterruptableThread(threading.Thread):
            def __init__(self):
                threading.Thread.__init__(self)
                self.result = default
            def run(self):
                self.result = func(*args, **kwargs)
        it = InterruptableThread()
        it.start()
        it.join(timeout_duration)
        if it.isAlive():
            return it.result
        else:
            return it.result

    def end(self):
        curses.endwin()

    def update_screen(self):
        self.stdscr.clear()

        self.print_backbuffer()
        self.print_header()
        if self.should_show_help:
            self.print_help()
        self.print_stickers()

        self.stdscr.refresh()

