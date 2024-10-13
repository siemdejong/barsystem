"""User page.

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

import numpy as np
import pandas as pd
import streamlit as st
from st_keyup import st_keyup
from streamlit_gsheets import GSheetsConnection

from barsystem.menu import menu

st.set_page_config(
    page_title="Bar System",
    page_icon=":material/local_bar:",
    layout="wide",
)

menu()

st.title("Bar System")
st.write("Welcome to the Bar System!")

if "new_data" not in st.session_state:
    st.session_state["new_data"] = False

if st.query_params.get("google_sheet_url"):
    conn = st.connection("gsheets", type=GSheetsConnection)

    data_df = conn.read(
        spreadsheet=st.query_params.get("google_sheet_url"),
        ttl=0 if st.session_state["new_data"] else None,
        index_col="name",
    )
    st.session_state["new_data"] = False

    st.session_state["data_df"] = data_df
    data_df = st.session_state["data_df"]

    if "change_df" not in st.session_state:
        change_df = pd.DataFrame().reindex_like(data_df).fillna(0)
        change_df.index = data_df.index
        st.session_state["change_df"] = change_df
    change_df = st.session_state["change_df"]

    name_filter = st_keyup("Name")
    display_data_df = data_df[data_df.index.str.startswith(name_filter)]

    column_spec = (1,) + (2,) * len(display_data_df.columns)
    cols = st.columns(column_spec)
    cols[0].markdown("**Name**")
    for col, field_name in zip(cols[1:], display_data_df.columns, strict=True):
        col.markdown(f"**{field_name}**")

    for name, row in display_data_df.iterrows():
        cols = st.columns(column_spec)
        name_col = cols[0]
        consumable_cols = cols[1:]
        name_col.markdown(name)
        for col, consumable in zip(
            consumable_cols, display_data_df.columns, strict=True
        ):
            col_value, col_add, col_remove = col.columns((1, 1, 1))
            color = "red" if change_df.loc[name, consumable] < 0 else "green"
            arrow = "downward" if change_df.loc[name, consumable] < 0 else "upward"
            value = str(row[consumable])
            if change_df.loc[name, consumable]:
                value = (
                    f"{value} :{color}[:material/arrow_{arrow}:"
                    f"{np.abs(change_df.loc[name, consumable].astype(int))}]"
                )
            col_value.markdown(value)
            col_add.button("", key=f"{name}-add-{consumable}", icon=":material/add:")
            col_remove.button(
                "",
                key=f"{name}-remove-{consumable}",
                icon=":material/remove:",
            )
            if st.session_state.get(f"{name}-add-{consumable}"):
                change_df.loc[name, consumable] += 1
                st.rerun()
            if st.session_state.get(f"{name}-remove-{consumable}"):
                change_df.loc[name, consumable] -= 1
                st.rerun()

    if st.button("Confirm", type="primary"):
        data_df = data_df.add(change_df).astype(int)

        # The google sheet connection does not support updating by index
        # so we have to do funky column adding and dropping.
        data_df.insert(0, "name", data_df.index)
        conn.update(spreadsheet=st.query_params.get("google_sheet_url"), data=data_df)
        data_df = data_df.drop("name", axis=1)

        st.session_state["new_data"] = True
        st.session_state["change_df"] = pd.DataFrame().reindex_like(data_df).fillna(0)
        st.session_state["data_df"] = data_df
        st.rerun()
else:
    st.error("Did not find a database. Did you scan a valid QR code?")
