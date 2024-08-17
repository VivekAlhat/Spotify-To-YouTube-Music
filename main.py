import os
import shutil
from yaspin import yaspin
from pyfiglet import Figlet
from termcolor import colored
from youtube import add_to_playlist
from spotify import (
    get_auth_url,
    get_token,
    get_playlists,
    get_playlist_tracks,
    write_playlist_to_disk,
)

playlists_directory = "playlists/"


if __name__ == "__main__":
    f = Figlet(font="slant", width=200)
    print(f.renderText("Spotify to YT Music"))

    spinner = yaspin()

    if os.path.exists(playlists_directory):
        shutil.rmtree(playlists_directory)

    auth_url = get_auth_url()
    print(
        colored(
            "Click on below URL or copy in browser to authenticate the app with Spotify:\n",
            "light_green",
        )
    )
    print(auth_url)

    try:
        code = input(
            colored(
                "\nPaste the code generated after Spotify authentication: ",
                "light_green",
            )
        )
        if len(code) <= 0:
            raise RuntimeError("Invalid code")

        print("\n")
        # get access token
        token = get_token(code, spinner)

        # get user playlists
        playlists = get_playlists(token, spinner)
        if len(playlists) <= 0:
            raise RuntimeError("No playlist found for the user")

        for item in playlists:
            file_name = "{name}.json".format(name=item["name"])
            # get tracks for each playlist
            tracks = get_playlist_tracks(
                name=item["name"],
                url=item["tracks"]["href"],
                token=token,
                spinner=spinner,
            )

            # create playlists directory if it doesn't exist
            if os.path.exists(playlists_directory) == False:
                os.makedirs(playlists_directory)

            # write all tracks for a given playlist in a json file
            write_playlist_to_disk(
                playlists_directory=playlists_directory,
                file_name=file_name,
                tracks=tracks,
            )

        yt_continue = input(
            colored(
                "\nPress 1 to start migration to YouTube music: ",
                "light_green",
            )
        )
        if yt_continue == "1":
            all_playlists = os.listdir(playlists_directory)

            if len(all_playlists) <= 0:
                print(
                    colored(
                        "\nNo playlists found",
                        "light_red",
                    )
                )
                exit(1)

            print("\nAvailable playlists:")
            for index, playlist_file in enumerate(all_playlists):
                playlist_name = playlist_file.split(".")[0]
                print("{index}. {name}".format(index=index + 1, name=playlist_name))

            playlist_selection = input(
                colored(
                    "\nEnter the number of playlist (enter * for all): ",
                    "light_green",
                )
            )

            if playlist_selection == "*":
                for playlist_file in all_playlists:
                    add_to_playlist(
                        playlists_directory=playlists_directory,
                        playlist_file=playlist_file,
                    )
            else:
                if int(playlist_selection) <= 0 or int(playlist_selection) > len(
                    all_playlists
                ):
                    print("Invalid playlist")
                else:
                    idx = int(playlist_selection) - 1
                    add_to_playlist(
                        playlists_directory=playlists_directory,
                        playlist_file=all_playlists[idx],
                    )

        else:
            print("\nYouTube music migration cancelled.")
            exit(1)
    except Exception as e:
        print("\n" + colored(str(e), "light_red"))
        spinner.stop()
        exit(1)
