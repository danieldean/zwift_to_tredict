## Zwift to Tredict

Uploads activities from Zwift to Tredict. It works by making an initial
log of activities (and optionally uploading them) before launching Zwift
and rechecking activities on exit.

This is early stages but the script does work for
[Zwift on Linux](https://github.com/netbrain/zwift) and on Windows. At
the moment the following paths are assumed:

- Windows
    - "~\\OneDrive\\Documents\\Zwift\\Activities" for activities (default)
    - "C:\\Program Files (x86)\\Zwift\\ZwiftLauncher.exe" for Zwift (default)
- Linux
    - "~/Zwift/Activities/" for activities
    - "zwift" for Zwift (default)

This is dependant on an API package I created called
[tredictpy](https://github.com/danieldean/tredictpy) which is considered
complete at this stage.

Check out [Tredict](https://www.tredict.com/) for a training platform with
plenty of toys and customisations.
