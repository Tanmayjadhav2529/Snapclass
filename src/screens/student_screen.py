import streamlit as st

from src.screens.home_screen import home_screen


def main():
    st.set_page_config(
        page_title="SnapClass - Making Attendance Faster Using AI",
        page_icon="https://i.ibb.co/YTYGn5qV/logo.png"
    )

    home_screen()


if __name__ == "__main__":
    main()