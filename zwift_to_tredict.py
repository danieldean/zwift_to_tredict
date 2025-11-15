#!/usr/bin/python3

#
# zwift_to_tredict
#
# Copyright (c) 2025 Daniel Dean <dd@danieldean.uk>.
#
# Licensed under The MIT License a copy of which you should have
# received. If not, see:
#
# http://opensource.org/licenses/MIT
#


import time
import os
import json
import platform
import psutil
from tredictpy.tredict import TredictPy, APIException
from api_secrets import CLIENT_ID, CLIENT_SECRET, TOKEN_APPEND, ENDPOINT_APPEND


def process_cmd(p):
    try:
        return p.cmdline()
    except psutil.Error:
        return []


def main():

    in_progress = "inProgressActivity.fit"
    upload_past_activities = False

    # These paths need to be customisable
    # For now they are hardcoded
    if platform.system() == "Windows":
        json_db = ".\\zwift_to_tredict.json"
        activity_dir = os.path.expanduser("~\\OneDrive\\Documents\\Zwift\\Activities\\")
        zwift_path = "C:\\Program Files (x86)\\Zwift\\ZwiftLauncher.exe"
        check_for = "C:\\Program Files (x86)\\Zwift\\ZwiftApp.exe"
    elif platform.system() == "Linux":
        json_db = "./zwift_to_tredict.json"
        activity_dir = os.path.expanduser("~/Zwift/Activities/")
        zwift_path = "zwift"
        check_for = "/bin/run_zwift.sh"
    else:
        raise SystemError(f"Operating system '{platform.system}' is not supported.")

    client = TredictPy(CLIENT_ID, CLIENT_SECRET, TOKEN_APPEND, ENDPOINT_APPEND)

    print("Checking for authorisation and access...")

    # First run, need to authorise and get an access token
    # Or was run before but did not complete authorisation
    if not client.is_authorised():
        client.request_auth_code()
        client.request_user_access_token()

    # An access token was obtained before but it has expired
    # can refresh using the refresh token
    if not client.is_user_access_token_valid():
        client.request_user_access_token(refresh=True)

    if not os.path.exists(json_db):

        print("Creating database of past activities...")

        # Get a list of present activities
        activities = [
            dict(
                [("activity", activity), ("uploaded", False), ("already_present", True)]
            )
            for activity in os.listdir(activity_dir)
            if activity.endswith(".fit") and activity != in_progress
        ]

        # Upload past activities if set
        if upload_past_activities:
            for activity in activities:
                print(f"Uploading '{activity_dir}{activity['activity']}'...")
                try:
                    client.activity_upload(
                        f"{activity_dir}{activity['activity']}",
                        activity_notes="Uploaded by Zwift to Tredict",
                    )
                    activity["uploaded"] = True
                except APIException:
                    print(
                        f"Upload of '{activity_dir}{activity['activity']}' failed! Activity skipped."
                    )
                    activity["uploaded"] = False

        last_checked = int(time.time())

        # Write to file to keep track
        with open(json_db, "wt", encoding="ascii") as f:
            f.write(
                json.dumps(
                    {
                        "last_checked": last_checked,
                        "activities": activities,
                    },
                    indent=4,
                )
            )

    print("Loading activity database...")
    with open(json_db, "rt", encoding="ascii") as f:
        activities = json.loads(f.read())

    print("Launching Zwift...")
    psutil.subprocess.run(zwift_path, check=True)

    # Need to wait for Zwift to start
    while (
        len(
            [
                process_cmd(p)
                for p in psutil.process_iter()
                if check_for in process_cmd(p)
            ]
        )
        == 0
    ):
        time.sleep(2)
    print("Zwift started!")

    while (
        len(
            [
                process_cmd(p)
                for p in psutil.process_iter()
                if check_for in process_cmd(p)
            ]
        )
        > 0
    ):
        time.sleep(10)
    print("Zwift exited!")

    # Check for new activities against old activities
    new_activities = [
        activity
        for activity in os.listdir(activity_dir)
        if activity not in [a["activity"] for a in activities["activities"]]
        and activity != in_progress
    ]

    for activity in new_activities:

        # Upload new activities
        print(f"Uploading '{activity_dir}{activity}'...")
        try:
            client.activity_upload(
                f"{activity_dir}{activity}",
                activity_notes="Uploaded by Zwift to Tredict",
            )
            uploaded = True
        except APIException:
            print(f"Upload of '{activity_dir}{activity}' failed! Activity skipped.")
            uploaded = False

        # Add to the record
        activities["activities"].append(
            {
                "activity": activity,
                "uploaded": uploaded,
                "already_present": False,
            }
        )

    activities["last_checked"] = int(time.time())

    print("Writing activity database...")
    with open(json_db, "wt", encoding="ascii") as f:
        f.write(json.dumps(activities, indent=4))

    input("Press [Enter] to exit...")


if __name__ == "__main__":
    main()
