import time
import numpy as np
from PIL import Image
import streamlit as st

from src.components.subject_card import subject_card
from src.components.footer import footer_dashboard
from src.components.header import header_dashboard
from src.components.dialog_enroll import enroll_dialog

from src.database.db import (
    create_student,
    get_all_students,
    get_student_subjects,
    unenroll_student_from_subject,
)
from src.database.config import supabase

from src.pipelines.face_pipeline import (
    get_face_embeddings,
    predict_attendance,
    train_classifier,
)
from src.pipelines.voice_pipeline import get_voice_embedding
from src.ui.base_layout import style_background_dashboard, style_base_layout


def get_student_attendance(student_id):
    """Get attendance records for the logged-in student."""
    response = (
        supabase
        .table("attendance_logs")
        .select("*")
        .eq("student_id", student_id)
        .execute()
    )

    return response.data


def student_dashboard():

    student_data = st.session_state.student_data
    student_id = student_data["student_id"]

    c1, c2 = st.columns(
        2,
        vertical_alignment="center",
        gap="xxlarge"
    )

    with c1:
        header_dashboard()

    with c2:
        st.subheader(f"Welcome, {student_data['name']}")

        if st.button(
            "Logout",
            type="secondary",
            key="dashboard_logout_btn",
            shortcut="control+backspace"
        ):
            st.session_state["is_logged_in"] = False
            st.session_state["user_role"] = None
            st.session_state.pop("student_data", None)

            st.rerun()

    st.space()

    c1, c2 = st.columns(2)

    with c1:
        st.header("Your Enrolled Subjects")

    with c2:
        if st.button(
            "Enroll in Subject",
            type="primary",
            width="stretch"
        ):
            enroll_dialog()

    st.divider()

    with st.spinner("Loading your enrolled subjects..."):

        subjects = get_student_subjects(student_id)
        logs = get_student_attendance(student_id)

    # -----------------------------------------
    # Attendance statistics
    # -----------------------------------------

    stats_map = {}

    for log in logs:

        sid = log.get("subject_id")

        if sid is None:
            continue

        if sid not in stats_map:
            stats_map[sid] = {
                "total": 0,
                "attended": 0
            }

        stats_map[sid]["total"] += 1

        if log.get("is_present"):
            stats_map[sid]["attended"] += 1

    # -----------------------------------------
    # Display subjects
    # -----------------------------------------

    if not subjects:
        st.info("You are not enrolled in any subjects yet.")
    else:

        cols = st.columns(2)

        for i, sub in enumerate(subjects):

            sid = sub["subject_id"]

            stats = stats_map.get(
                sid,
                {
                    "total": 0,
                    "attended": 0
                }
            )

            def unenroll_button(
                student_id=student_id,
                subject_id=sid,
                subject_name=sub["name"]
            ):

                if st.button(
                    "Unenroll from this course",
                    type="tertiary",
                    width="stretch",
                    icon=":material/delete_forever:",
                    key=f"unenroll_{subject_id}"
                ):

                    unenroll_student_from_subject(
                        student_id,
                        subject_id
                    )

                    st.toast(
                        f"Unenrolled from {subject_name} successfully!"
                    )

                    st.rerun()

            with cols[i % 2]:

                subject_card(
                    name=sub["name"],
                    code=sub["subject_code"],
                    section=sub["section"],
                    stats=[
                        (
                            "📅",
                            "Total",
                            stats["total"]
                        ),
                        (
                            "✅",
                            "Attended",
                            stats["attended"]
                        ),
                    ],
                    footer_callback=unenroll_button
                )

    footer_dashboard()


def student_screen():

    style_background_dashboard()
    style_base_layout()

    # -----------------------------------------
    # IMPORTANT:
    # If the student is already logged in,
    # show the dashboard instead of FaceID again.
    # -----------------------------------------

    if (
        st.session_state.get("is_logged_in")
        and st.session_state.get("user_role") == "student"
    ):
        student_dashboard()
        return

    # -----------------------------------------
    # Student login screen
    # -----------------------------------------

    c1, c2 = st.columns(
        2,
        vertical_alignment="center",
        gap="xxlarge"
    )

    with c1:
        header_dashboard()

    with c2:

        if st.button(
            "Go back to Home",
            type="secondary",
            key="loginbackbtn",
            shortcut="control+backspace",
        ):

            st.session_state["login_type"] = None
            st.rerun()

    st.header(
        "Login using FaceID",
        anchor=False
    )

    photo_source = st.camera_input(
        "Position your face in the center"
    )

    show_registration = False

    # -----------------------------------------
    # Face login
    # -----------------------------------------

    if photo_source:

        img = np.array(
            Image.open(photo_source)
        )

        with st.spinner("AI is scanning.."):

            detected, all_ids, num_faces = predict_attendance(img)

            if num_faces == 0:

                st.warning("Face not found!")

            elif num_faces > 1:

                st.warning("Multiple faces found")

            else:

                if detected:

                    student_id = list(
                        detected.keys()
                    )[0]

                    all_students = get_all_students()

                    student = next(
                        (
                            s
                            for s in all_students
                            if s["student_id"] == student_id
                        ),
                        None,
                    )

                    if student:

                        st.session_state["is_logged_in"] = True
                        st.session_state["user_role"] = "student"
                        st.session_state["student_data"] = student

                        st.toast(
                            f"Welcome Back {student['name']}"
                        )

                        time.sleep(1)

                        st.rerun()

                else:

                    st.info(
                        "Face not recognized! "
                        "You might be a new student!"
                    )

                    show_registration = True

    # -----------------------------------------
    # New student registration
    # -----------------------------------------

    if show_registration:

        with st.container(border=True):

            st.header("Register new Profile")

            new_name = st.text_input(
                "Enter your name",
                placeholder="E.g. Hamza Rizvi"
            )

            st.subheader(
                "Optional : Voice Enrollment"
            )

            st.info(
                "Enroll your voice for voice-only attendance"
            )

            audio_data = None

            try:

                audio_data = st.audio_input(
                    "Record a short phrase like "
                    "'I am present, My name is Akash.'"
                )

            except Exception:

                st.error("Audio Data failed!")

            if st.button(
                "Create Account",
                type="primary"
            ):

                if new_name:

                    with st.spinner(
                        "Creating profile.."
                    ):

                        img = np.array(
                            Image.open(photo_source)
                        )

                        encodings = get_face_embeddings(
                            img
                        )

                        if encodings:

                            face_emb = encodings[0].tolist()

                            voice_emb = None

                            if audio_data:

                                voice_emb = get_voice_embedding(
                                    audio_data.read()
                                )

                            response_data = create_student(
                                new_name,
                                face_embedding=face_emb,
                                voice_embedding=voice_emb,
                            )

                            if response_data:

                                train_classifier()

                                st.session_state[
                                    "is_logged_in"
                                ] = True

                                st.session_state[
                                    "user_role"
                                ] = "student"

                                st.session_state[
                                    "student_data"
                                ] = response_data[0]

                                st.toast(
                                    f"Profile Created! "
                                    f"Hi {new_name}!"
                                )

                                time.sleep(1)

                                st.rerun()

                        else:

                            st.error(
                                "Couldn't capture your "
                                "facial features for registration"
                            )

                else:

                    st.warning(
                        "Please enter your name!"
                    )

    footer_dashboard()