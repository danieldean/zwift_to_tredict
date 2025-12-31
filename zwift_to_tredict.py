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

IN_PROGRESS = "inProgressActivity.fit"
DEFAULT_LINUX_DB_PATH = "./zwift_to_tredict.json"
DEFAULT_WINDOWS_DB_PATH = ".\\zwift_to_tredict.json"
DEFAULT_LINUX_ACTIVITY_DIR = "~/Zwift/Activities/"
DEFAULT_WINDOWS_ACTIVITY_DIR = "~\\OneDrive\\Documents\\Zwift\\Activities\\"
DEFAULT_LINUX_ZWIFT_PATH = "zwift"
DEFAULT_WINDOWS_ZWIFT_PATH = "C:\\Program Files (x86)\\Zwift\\ZwiftLauncher.exe"
DEFAULT_LINUX_CHECK_FOR = "/bin/run_zwift.sh"
DEFAULT_WINDOWS_CHECK_FOR = "C:\\Program Files (x86)\\Zwift\\ZwiftApp.exe"


class ZwiftToTredict:

    def __init__(
        self,
        db_path: str = None,
        activity_dir: str = None,
        zwift_path: str = None,
        check_for: str = None,
    ) -> None:

        self._platform = platform.system()

        # fmt: off
        if self._platform == "Linux":
            self._db_path = os.path.expanduser(db_path or DEFAULT_LINUX_DB_PATH)
            self._activity_dir = os.path.expanduser(activity_dir or DEFAULT_LINUX_ACTIVITY_DIR)
            self._zwift_path = os.path.expanduser(zwift_path or DEFAULT_LINUX_ZWIFT_PATH)
            self._check_for = check_for or DEFAULT_LINUX_CHECK_FOR
        elif self._platform == "Windows":
            self._db_path = os.path.expanduser(db_path or DEFAULT_WINDOWS_DB_PATH)
            self._activity_dir = os.path.expanduser(activity_dir or DEFAULT_WINDOWS_ACTIVITY_DIR)
            self._zwift_path = os.path.expanduser(zwift_path or DEFAULT_WINDOWS_ZWIFT_PATH)
            self._check_for = check_for or DEFAULT_WINDOWS_CHECK_FOR
        else:
            raise SystemError(f"Operating system '{self._platform}' is not supported.")
        # fmt: on

        self._client = TredictPy(
            CLIENT_ID, CLIENT_SECRET, TOKEN_APPEND, ENDPOINT_APPEND
        )
        self._json_db = None

    def authorise(self) -> None:

        try:
            # First run, need to authorise and get an access token
            # Or was run before but did not complete authorisation
            if not self._client.is_authorised():
                self._client.request_auth_code()
                self._client.request_user_access_token()

            # An access token was obtained before but it has expired
            # can refresh using the refresh token
            if not self._client.is_user_access_token_valid():
                self._client.request_user_access_token(refresh=True)
        except APIException as e:
            raise e

    def db_init_and_load(self) -> None:

        # Create an empty database if none exists
        if not os.path.exists(self._db_path):
            print("Creating database as none exists...")
            with open(self._db_path, "wt", encoding="ascii") as f:
                f.write(
                    json.dumps(
                        {"last_checked": None, "activities": [], "workouts": []},
                        indent=4,
                    )
                )

        print("Loading database...")
        with open(self._db_path, "rt", encoding="ascii") as f:
            self._json_db = json.loads(f.read())

    def db_save(self) -> None:

        print("Writing database...")
        with open(self._db_path, "wt", encoding="ascii") as f:
            f.write(json.dumps(self._json_db, indent=4))

    def check_activities(self) -> None:

        # Check for new activities against old activities
        print("Checking activities...")
        new_activities = [
            new_activity
            for new_activity in os.listdir(self._activity_dir)
            if new_activity
            not in [
                old_activity["activity"] for old_activity in self._json_db["activities"]
            ]
            and new_activity != IN_PROGRESS
        ]

        print(f"Found {len(new_activities)} new activities...")
        for new_activity in new_activities:
            self._json_db["activities"].append(
                {
                    "activity": new_activity,
                    "uploaded": False,
                    "processed": not self._json_db["last_checked"],
                }
            )

        self._json_db["last_checked"] = int(time.time())

    def process_activities(self) -> None:

        for activity in self._json_db["activities"]:

            if not activity["processed"] and not activity["uploaded"]:

                # Upload new activities
                print(f"Uploading '{activity["activity"]}'...")
                try:
                    self._client.activity_upload(
                        f"{self._activity_dir}{activity["activity"]}",
                        activity_notes="Uploaded by Zwift to Tredict",
                    )
                    uploaded = True
                except APIException:
                    print(
                        f"Upload of '{self._activity_dir}{activity}' failed! Activity skipped."
                    )
                    uploaded = False

                # Update the record
                activity["uploaded"] = uploaded
                activity["processed"] = True

        self._json_db["last_checked"] = int(time.time())

    @staticmethod
    def _process_cmd(p: psutil.Process) -> list:
        try:
            return p.cmdline()
        except psutil.Error:
            return []

    @staticmethod
    def _check_for_process_cmd(cmd: str) -> bool:
        for process in psutil.process_iter():
            if cmd in ZwiftToTredict._process_cmd(process):
                return True
        return False

    def launch_zwift_and_wait(self) -> None:

        print("Launching Zwift...")
        psutil.subprocess.run(self._zwift_path, check=True)

        # Need to wait for Zwift to start
        while not ZwiftToTredict._check_for_process_cmd(self._check_for):
            time.sleep(2)
        print("Zwift started!")

        # Wait while Zwift is running
        while ZwiftToTredict._check_for_process_cmd(self._check_for):
            time.sleep(10)
        print("Zwift exited!")


def main():

    ztt = ZwiftToTredict()

    ztt.authorise()

    ztt.db_init_and_load()

    ztt.check_activities()

    ztt.launch_zwift_and_wait()

    ztt.check_activities()

    ztt.process_activities()

    ztt.db_save()

    input("Press [Enter] to exit...")


if __name__ == "__main__":
    main()
