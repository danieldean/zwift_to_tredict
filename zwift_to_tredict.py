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


from tredictpy import tredict
import time
import os
import json
import psutil
import sys
from api_secrets import CLIENT_ID, CLIENT_SECRET, TOKEN_APPEND, ENDPOINT_APPEND


def main():

    json_db = "./zwift_to_tredict.json"
    in_progress = "inProgressActivity.fit"
    activity_dir = os.path.expanduser("~/Zwift/Activities/")
    upload_past_activities = False

    client = tredict.TredictPy(CLIENT_ID, CLIENT_SECRET, TOKEN_APPEND, ENDPOINT_APPEND)

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
                except tredict.APIException:
                    print(
                        f"Upload of '{activity_dir}{activity['activity']}' failed! Activity skipped."
                    )
                    activity["uploaded"] = False

        last_checked = int(time.time())

        # Write to file to keep track
        with open(json_db, "wt") as f:
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
    with open(json_db, "rt") as f:
        activities = json.loads(f.read())

    print("Launching Zwift...")
    zwift = psutil.subprocess.run("zwift")

    if zwift.returncode != 0:
        print("Zwift failed to launch!")
        sys.exit()

    while True:
        time.sleep(10)
        if not [
            p.info["name"]
            for p in psutil.process_iter(["name"])
            if "zwift" in p.info["name"].lower()
        ]:
            print("Zwift exited!")
            break

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
        except tredict.APIException:
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
    with open(json_db, "wt") as f:
        f.write(json.dumps(activities, indent=4))


if __name__ == "__main__":
    main()
