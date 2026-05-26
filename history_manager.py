import json
import os

from datetime import datetime


# =========================
# SAVE GENERATION HISTORY
# =========================

def save_generation_history(
    username,
    ats_score,
    job_description
):

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    history_data = {

        "username": username,

        "timestamp": timestamp,

        "ats_score": ats_score,

        "job_description_preview": (
            job_description[:300]
        )
    }

    history_file = (
        f"data/history/{username}_{timestamp}.json"
    )

    with open(
        history_file,
        "w"
    ) as file:

        json.dump(
            history_data,
            file,
            indent=2
        )


# =========================
# LOAD USER HISTORY
# =========================

def load_user_history(username):

    history_files = sorted(
        os.listdir("data/history"),
        reverse=True
    )

    user_history = []

    for file in history_files:

        if file.startswith(username):

            file_path = (
                f"data/history/{file}"
            )

            with open(
                file_path,
                "r"
            ) as history_file:

                data = json.load(
                    history_file
                )

                user_history.append(
                    data
                )

    return user_history


# =========================
# TOTAL GENERATIONS
# =========================

def get_total_generations():

    return len(
        os.listdir("data/history")
    )


# =========================
# TOTAL USERS
# =========================

def get_total_users():

    users = set()

    for file in os.listdir(
        "data/history"
    ):

        username = file.split("_")[0]

        users.add(username)

    return len(users)