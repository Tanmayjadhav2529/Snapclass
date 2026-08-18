import streamlit as st

from src.ui.base_layout import style_background_dashboard, style_base_layout
from src.components.header import header_dashboard
from src.database.db import check_teacher_exists, create_teacher, teacher_login


def teacher_screen():

    style_background_dashboard()
    style_base_layout()

    if 'teacher_login' not in st.session_state:



        st.session_state['teacher_login'] = False

    if st.session_state['teacher_login']:
        teacher_screen_register()
    else:
        teacher_screen_login()


def register_teacher(teacher_username, teacher_name, teacher_pass, teacher_pass_confirm):
    if not teacher_username or not teacher_name or not teacher_pass:
        return False, "All Fields are required!"

    if check_teacher_exists(teacher_username):
        return False, "Username already taken"

    if teacher_pass != teacher_pass_confirm:
        return False, "Password doesn't match"

    try:
        create_teacher(teacher_username, teacher_pass, teacher_name)
        return True, "Successfully Created"
    except Exception as e:
        return False, "Unexpected Error!"


def teacher_screen_login():

    c1, c2 = st.columns(2, vertical_alignment='center', gap='xxlarge')

    with c1:
        header_dashboard()

    with c2:
        if st.button(
            "Go back to Home",
            type='secondary',
            key='loginbackbtn',
            shortcut="control+backspace"
        ):
            st.session_state['teacher_login'] = False
            # TODO: hook this up to your app's actual "home" navigation
            st.rerun()

    st.header('Login using password')
    st.space()
    st.space()

    teacher_username = st.text_input(
        "Enter username",
        key='login_username'
    )
    teacher_password = st.text_input(
        "Enter password",
        type="password",
        key='login_password'
    )

    st.divider()

    btnc1, btnc2, btnc3 = st.columns(
        [1, 1, 1],
        gap="large"
    )

    with btnc1:
        if st.button(
            "Login",
            type='primary',
            key='loginbtn',
            icon=':material/person:',
            shortcut='ctrl+enter'
        ):
            if not teacher_username or not teacher_password:
                st.error("Please enter both a username and password.")
            elif validate_teacher_login(teacher_username, teacher_password):
                st.session_state['teacher_username'] = teacher_username
                st.session_state['teacher_password'] = teacher_password
                st.session_state['login_type'] = 'teacher'
                st.rerun()
            else:
                st.warning("We couldn't find that account. Let's get you registered.")
                st.session_state['register_username'] = teacher_username
                st.session_state['teacher_login'] = True
                st.rerun()

    with btnc2:
        if st.button(
            "Register Instead",
            type='secondary',
            key='registerbtn',
            icon=':material/person:'
        ):
            st.session_state['teacher_login'] = True
            st.rerun()


def validate_teacher_login(username, password):
    teacher = teacher_login(username, password)
    return teacher is not None


def teacher_screen_register():

    c1, c2 = st.columns(
        2,
        vertical_alignment='center',
        gap='xxlarge'
    )

    with c1:
        header_dashboard()

    with c2:
        if st.button(
            "Go back to Home",
            type='secondary',
            key='registerbackbtn',
            shortcut="control+backspace"
        ):
            st.session_state['teacher_login'] = False
            st.rerun()

    st.header('Register your teacher profile')
    st.space()
    st.space()

    teacher_username = st.text_input(
        "Enter username",
        value=st.session_state.get('register_username', ''),
        key='register_username_input'
    )
    teacher_name = st.text_input(
        "Enter name",
        key='register_name'
    )
    teacher_password = st.text_input(
        "Enter password",
        type="password",
        key='register_password'
    )
    teacher_confirm_password = st.text_input(
        "Confirm your password",
        type="password",
        key='register_confirm_password'
    )

    st.divider()

    btnc1, btnc2, btnc3 = st.columns(
        [1, 1, 1],
        gap="large"
    )

    with btnc1:
        if st.button(
            "Register now",
            type='primary',
            key='createaccountbtn',
            icon=':material/person:',
            shortcut='ctrl+enter'
        ):
            success, message = register_teacher(
                teacher_username,
                teacher_name,
                teacher_password,
                teacher_confirm_password
            )
            if success:
                st.session_state['teacher_username'] = teacher_username
                st.session_state['teacher_name'] = teacher_name
                st.session_state['login_type'] = 'teacher'
                st.session_state['teacher_login'] = False
                st.success(message)
                st.rerun()
            else:
                st.error(message)

    with btnc2:
        if st.button(
            "Login Instead",
            type='secondary',
            key='backtologinbtn',
            icon=':material/person:'
        ):
            st.session_state['teacher_login'] = False
            st.rerun()