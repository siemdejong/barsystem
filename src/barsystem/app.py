"""A minimal bar system app.

Copyright (C) 2024 Siem de Jong

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import sys
from pathlib import Path

import streamlit as st

sys.path.append(str(Path(__file__).absolute().parent.parent))

from barsystem.menu import menu

st.set_page_config(
    page_title="Bar System",
    page_icon=":material/local_bar:",
    layout="wide",
)

menu()
