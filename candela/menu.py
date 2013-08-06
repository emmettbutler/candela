"""
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
"""

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
