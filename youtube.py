import os
import re
import json
from ytmusicapi import YTMusic

from yaspin import yaspin
from termcolor import colored


credentials = "oauth.json"


if os.path.exists(credentials) == False:
    colored(
        "Missing YouTube music credentials. Please follow the steps mentioned in README file.",
        "light_red",
    )
    exit(0)

ytmusic = YTMusic(credentials)


def create_playlist(playlist_name):
    """
    This function created a new playlist on YouTube music
    """
    try:
        playlist_id = ytmusic.create_playlist(
            re.sub(r"[^a-zA-Z0-9\s]", "", playlist_name),
            "Created by Spotify to YT Music migration tool",
        )
        return playlist_id
    except:
        raise RuntimeError(
            "Some error occurred while creating a new playlist on YouTube music"
        )


def add_to_playlist(playlists_directory, playlist_file):
    try:
        video_ids = []
        playlist_path = playlists_directory + playlist_file
        playlist_name = playlist_file.split(".")[0]

        print(
            "\nMigrating playlist: "
            + colored(playlist_name, "light_blue")
            + " to YouTube music"
        )
        with open(playlist_path) as f:
            tracks = json.load(f)
            for track in tracks:
                search_term = "{name} {artist}".format(
                    name=track["name"], artist=track["artist"]
                )
                result = ytmusic.search(search_term)
                top_songs = [obj for obj in result if obj["resultType"] == "song"]
                video_id = top_songs[0]["videoId"]
                video_ids.append(video_id)
                print(colored("> adding to playlist: " + search_term, "light_yellow"))
        playlist_id = create_playlist(playlist_name=playlist_name)
        ytmusic.add_playlist_items(playlistId=playlist_id, videoIds=video_ids)

        print(
            "\nSuccessfully migrated playlist: "
            + colored(playlist_name, "light_blue")
            + " to YouTube music"
        )
    except:
        raise RuntimeError(
            "Some error occurred while creating playlist or while adding tracks to the playlist on YouTube music"
        )
