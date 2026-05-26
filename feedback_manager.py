import json
import os

from datetime import datetime


# =========================
# SAVE FEEDBACK
# =========================

def save_feedback(
    username,
    feedback_type,
    feedback_comment
):

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    feedback_data = {

        "username": username,

        "timestamp": timestamp,

        "feedback": feedback_type,

        "comment": feedback_comment
    }

    feedback_file = (
        f"data/feedback/{username}_{timestamp}.json"
    )

    with open(
        feedback_file,
        "w"
    ) as file:

        json.dump(
            feedback_data,
            file,
            indent=2
        )


# =========================
# LOAD FEEDBACK DATA
# =========================

def load_feedback_data():

    feedback_files = os.listdir(
        "data/feedback"
    )

    feedback_data = []

    for file in feedback_files:

        file_path = (
            f"data/feedback/{file}"
        )

        with open(
            file_path,
            "r"
        ) as feedback_file:

            data = json.load(
                feedback_file
            )

            feedback_data.append(
                data
            )

    return feedback_data


# =========================
# TOTAL FEEDBACK
# =========================

def get_total_feedback():

    return len(
        os.listdir("data/feedback")
    )