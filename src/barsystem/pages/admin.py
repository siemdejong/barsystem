"""Administration page.

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

import io

import qrcode
import qrcode.constants
import qrcode.util
import streamlit as st
from streamlit_gsheets import GSheetsConnection

from barsystem.menu import menu

st.set_page_config(
    page_title="Bar System | Admin",
    page_icon=":material/local_bar:",
    layout="wide",
)

menu()


@st.cache_data
def make_qr(data: qrcode.util.QRData) -> io.BytesIO:
    """Make QR code for data."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image()
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format="png")
    return img_byte_arr


google_sheet_url = st.text_input("Google sheet URL")
if google_sheet_url:
    conn = st.connection("gsheets", type=GSheetsConnection)
    data_df = conn.read(ttl=0, spreadsheet=google_sheet_url, index_col="name")
    st.write(data_df)

    site_url = (
        f"https://barsystem.streamlit.app/user?google_sheet_url={google_sheet_url}"
    )
    qr = make_qr(site_url)
    st.download_button("Download QR", qr, "qr.png", mime="image/png")

    xlsx_buffer = io.BytesIO()
    data_df.to_excel(xlsx_buffer)
    st.download_button(
        "Download Excel",
        xlsx_buffer,
        "data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
