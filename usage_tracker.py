import json
import os

from datetime import datetime


# =========================
# USAGE FILE
# =========================

def get_usage_file(username):

    today = datetime.now().strftime(
        "%Y-%m-%d"
    )

    return (
        f"data/usage/{username}_{today}.json"
    )


# =========================
# GET USER USAGE
# =========================

def get_user_usage(username):

    usage_file = get_usage_file(
        username
    )

    if os.path.exists(usage_file):

        with open(
            usage_file,
            "r"
        ) as file:

            data = json.load(file)

            return data.get(
                "generations",
                0
            )

    return 0


# =========================
# INCREMENT USAGE
# =========================

def increment_user_usage(username):

    usage_file = get_usage_file(
        username
    )

    current_usage = get_user_usage(
        username
    )

    data = {

        "username": username,

        "generations": current_usage + 1
    }

    with open(
        usage_file,
        "w"
    ) as file:

        json.dump(
            data,
            file,
            indent=2
        )


# =========================
# DAILY LIMIT
# =========================

def get_daily_limit(
    config,
    username
):

    user_data = (
        config["credentials"]["usernames"][username]
    )

    return user_data.get(
        "daily_limit",
        5
    )


# =========================
# REMAINING USAGE
# =========================

def get_remaining_usage(
    config,
    username
):

    daily_limit = get_daily_limit(
        config,
        username
    )

    current_usage = get_user_usage(
        username
    )

    remaining_usage = max(
        daily_limit - current_usage,
        0
    )

    return remaining_usage


# =========================
# LIMIT CHECK
# =========================

def has_remaining_usage(
    config,
    username
):

    daily_limit = get_daily_limit(
        config,
        username
    )

    current_usage = get_user_usage(
        username
    )

    return current_usage < daily_limit