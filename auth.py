import bcrypt
import yaml
import streamlit as st
import streamlit_authenticator as stauth

from yaml.loader import SafeLoader


# =========================
# LOAD CONFIG
# =========================

def load_auth_config():

    with open(
        "users.yaml",
        "r"
    ) as file:

        return yaml.load(
            file,
            Loader=SafeLoader
        )


# =========================
# SAVE CONFIG
# =========================

def save_auth_config(config):

    with open(
        "users.yaml",
        "w"
    ) as file:

        yaml.dump(
            config,
            file,
            default_flow_style=False
        )


# =========================
# AUTHENTICATOR
# =========================

def get_authenticator(config):

    return stauth.Authenticate(
        config["credentials"],
        config["cookie"]["name"],
        config["cookie"]["key"],
        config["cookie"]["expiry_days"]
    )


# =========================
# CREATE USER
# =========================

def save_user(
    config,
    name,
    email,
    username,
    password
):

    hashed_password = bcrypt.hashpw(
        password.encode(),
        bcrypt.gensalt()
    ).decode()

    config["credentials"]["usernames"][username] = {

        "email": email,

        "name": name,

        "password": hashed_password,

        "role": "user",

        "daily_limit": 5
    }

    save_auth_config(config)


# =========================
# SIGNUP FORM
# =========================

def render_signup_form(config):

    st.subheader(
        "Create Account"
    )

    signup_name = st.text_input(
        "Full Name"
    )

    signup_email = st.text_input(
        "Email"
    )

    signup_username = st.text_input(
        "Username"
    )

    signup_password = st.text_input(
        "Password",
        type="password"
    )

    signup_confirm_password = st.text_input(
        "Confirm Password",
        type="password"
    )

    if st.button(
        "Create Account"
    ):

        existing_emails = [

            user_data["email"]

            for user_data in config["credentials"]["usernames"].values()
        ]

        # =========================
        # VALIDATIONS
        # =========================

        if not signup_name:

            st.error(
                "Please enter full name."
            )

            return

        if not signup_email:

            st.error(
                "Please enter email."
            )

            return

        if not signup_username:

            st.error(
                "Please enter username."
            )

            return

        if not signup_password:

            st.error(
                "Please enter password."
            )

            return

        if (
            signup_username
            in config["credentials"]["usernames"]
        ):

            st.error(
                "Username already exists."
            )

            return

        if signup_email in existing_emails:

            st.error(
                "Email already exists."
            )

            return

        if (
            signup_password
            != signup_confirm_password
        ):

            st.error(
                "Passwords do not match."
            )

            return

        # =========================
        # SAVE USER
        # =========================

        save_user(
            config,
            signup_name,
            signup_email,
            signup_username,
            signup_password
        )

        st.success(
            "Account created successfully."
        )

        st.info(
            "Refresh the page and login."
        )


# =========================
# AUTH PAGE
# =========================

def render_auth_page():

    config = load_auth_config()

    authenticator = get_authenticator(
        config
    )

    login_tab, signup_tab = st.tabs(
        [
            "Login",
            "Sign Up"
        ]
    )

    # =========================
    # LOGIN TAB
    # =========================

    with login_tab:

        authenticator.login()

    # =========================
    # SIGNUP TAB
    # =========================

    with signup_tab:

        render_signup_form(
            config
        )

    return authenticator, config


# =========================
# AUTH STATUS
# =========================

def check_authentication():

    authentication_status = st.session_state.get(
        "authentication_status"
    )

    name = st.session_state.get(
        "name"
    )

    username = st.session_state.get(
        "username"
    )

    if authentication_status is False:

        st.error(
            "Incorrect username or password."
        )

        st.stop()

    if authentication_status is None:

        st.warning(
            "Please login to continue."
        )

        st.stop()

    return {
        "authentication_status": authentication_status,
        "name": name,
        "username": username
    }