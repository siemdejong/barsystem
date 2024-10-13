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

import numpy as np
import pandas as pd
import streamlit as st
from st_keyup import st_keyup

st.set_page_config(
    page_title="Bar System",
    page_icon=":material/local_bar:",
    layout="wide",
)

st.title("Bar System")
st.write("Welcome to the Bar System!")

uploaded_file = st.file_uploader("Choose a file", type=["csv"])
if uploaded_file is not None:
    if not np.any(st.session_state.get("data_df")):
        data_df = pd.read_csv(
            uploaded_file,
            index_col="name",
        )
        st.session_state["data_df"] = data_df
    data_df = st.session_state["data_df"]

    name_filter = st_keyup("Name")

    data_df = data_df[data_df.index.str.startswith(name_filter)]
    if "change_df" not in st.session_state:
        change_df = pd.DataFrame().reindex_like(data_df).fillna(0)
        change_df.index = data_df.index
        st.session_state["change_df"] = change_df
    change_df = st.session_state["change_df"]

    column_spec = (1,) + (2,) * len(data_df.columns)
    cols = st.columns(column_spec)
    cols[0].markdown("**Name**")
    for col, field_name in zip(cols[1:], data_df.columns, strict=True):
        col.markdown(f"**{field_name}**")

    for name, row in data_df.iterrows():
        cols = st.columns(column_spec)
        name_col = cols[0]
        consumable_cols = cols[1:]
        name_col.markdown(name)
        for col, consumable in zip(consumable_cols, data_df.columns, strict=True):
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
                st.session_state["change_df"] = change_df
                st.rerun()
            if st.session_state.get(f"{name}-remove-{consumable}"):
                change_df.loc[name, consumable] -= 1
                st.session_state["change_df"] = change_df
                st.rerun()

    if st.button("Confirm", type="primary"):
        data_df = data_df.add(change_df).astype(int)
        data_df.to_csv(uploaded_file)
        st.session_state["change_df"] = pd.DataFrame().reindex_like(data_df).fillna(0)
        st.session_state["data_df"] = data_df
        st.rerun()

    st.download_button(
        "Download updated data", data_df.to_csv(), "data.csv", "Download"
    )
