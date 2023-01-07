#  Copyright (c) 2021. Davi Pereira dos Santos
#  This file is part of the idict project.
#  Please respect the license - more about this in the section (*) below.
#
#  idict is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  idict is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with idict.  If not, see <http://www.gnu.org/licenses/>.
#
#  (*) Removing authorship by any means, e.g. by distribution of derived
#  works or verbatim, obfuscated, compiled or rewritten versions of any
#  part of this work is illegal and unethical regarding the effort and
#  time spent here.

import re


def decolorize(txt):
    """
    >>> decolorize("\x1b[38;5;116m\x1b[1m\x1b[48;5;0mB\x1b[0m\x1b[38;5;85m\x1b[1m\x1b[48;5;0ma\x1b[0m\x1b[38;5;157m\x1b[1m\x1b[48;5;0m_\x1b[0m\x1b[38;5;122m\x1b[1m\x1b[48;5;0m3\x1b[0m\x1b[38;5;86m\x1b[1m\x1b[48;5;0m1\x1b[0m\x1b[38;5;156m\x1b[1m\x1b[48;5;0md\x1b[0m\x1b[38;5;114m\x1b[1m\x1b[48;5;0m0\x1b[0m\x1b[38;5;80m\x1b[1m\x1b[48;5;0m0\x1b[0m\x1b[38;5;86m\x1b[1m\x1b[48;5;0m1\x1b[0m\x1b[38;5;156m\x1b[1m\x1b[48;5;0mc\x1b[0m\x1b[38;5;116m\x1b[1m\x1b[48;5;0m1\x1b[0m\x1b[38;5;84m\x1b[1m\x1b[48;5;0ma\x1b[0m\x1b[38;5;114m\x1b[1m\x1b[48;5;0ma\x1b[0m\x1b[38;5;80m\x1b[1m\x1b[48;5;0m4\x1b[0m\x1b[38;5;86m\x1b[1m\x1b[48;5;0m0\x1b[0m\x1b[38;5;156m\x1b[1m\x1b[48;5;0m5\x1b[0m\x1b[38;5;116m\x1b[1m\x1b[48;5;0m6\x1b[0m\x1b[38;5;85m\x1b[1m\x1b[48;5;0mb\x1b[0m\x1b[38;5;157m\x1b[1m\x1b[48;5;0m4\x1b[0m\x1b[38;5;122m\x1b[1m\x1b[48;5;0m6\x1b[0m\x1b[38;5;86m\x1b[1m\x1b[48;5;0mb\x1b[0m\x1b[38;5;156m\x1b[1m\x1b[48;5;0m2\x1b[0m\x1b[38;5;114m\x1b[1m\x1b[48;5;0m0\x1b[0m\x1b[38;5;80m\x1b[1m\x1b[48;5;0m1\x1b[0m\x1b[38;5;86m\x1b[1m\x1b[48;5;0m6\x1b[0m\x1b[38;5;156m\x1b[1m\x1b[48;5;0m1\x1b[0m\x1b[38;5;116m\x1b[1m\x1b[48;5;0m6\x1b[0m\x1b[38;5;84m\x1b[1m\x1b[48;5;0m0\x1b[0m\x1b[38;5;114m\x1b[1m\x1b[48;5;0mb\x1b[0m\x1b[38;5;80m\x1b[1m\x1b[48;5;0mb\x1b[0m\x1b[38;5;86m\x1b[1m\x1b[48;5;0m9\x1b[0m\x1b[38;5;156m\x1b[1m\x1b[48;5;0m5\x1b[0m\x1b[38;5;116m\x1b[1m\x1b[48;5;0m7\x1b[0m\x1b[38;5;85m\x1b[1m\x1b[48;5;0m4\x1b[0m\x1b[38;5;157m\x1b[1m\x1b[48;5;0m2\x1b[0m\x1b[38;5;122m\x1b[1m\x1b[48;5;0me\x1b[0m\x1b[38;5;86m\x1b[1m\x1b[48;5;0me\x1b[0m\x1b[38;5;156m\x1b[1m\x1b[48;5;0mc\x1b[0m\x1b[38;5;114m\x1b[1m\x1b[48;5;0m2\x1b[0m\x1b[38;5;80m\x1b[1m\x1b[48;5;0mb\x1b[0m")
    'Ba_31d001c1aa4056b46b2016160bb95742eec2b'
    """
    ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    return ansi_escape.sub("", txt)
