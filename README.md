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

## How to use

Here is how to get up and running:

1. Download the latest [release](https://github.com/danieldean/zwift_to_tredict/releases) and place it in a folder of your choosing
2. Generate a personal access token using the following guide [Personal API](https://www.tredict.com/faq/personal-api---connect-your-own-scripts-or-personal-applications/) and save it somewhere safe!
3. Download the example secrets file [example-tredict-config.json](https://raw.githubusercontent.com/danieldean/zwift_to_tredict/refs/heads/main/example-tredict-secrets.json)
4. In the line with `"personal_access_token": null` replace the null with your personal access token in double quotes
5. Rename the file to `tredict-secrets.json`
6. Run the executable and you are good to ride!

## Mentions

This is dependant on an API package I created called
[tredictpy](https://github.com/danieldean/tredictpy) which is considered
complete at this stage.

Check out [Tredict](https://www.tredict.com/) for a training platform with
plenty of toys and customisations.
