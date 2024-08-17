import os
import json
import random
import base64
import urllib.parse
from termcolor import colored
from requests import post, get
from dotenv import load_dotenv


load_dotenv()

client_id = os.getenv("SPOTIFY_CLIENT_ID")
client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI")

scope = os.getenv("SPOTIFY_SCOPE")
auth_url = os.getenv("SPOTIFY_AUTH_URL")
token_url = os.getenv("SPOTIFY_TOKEN_URL")
playlist_url = os.getenv("SPOTIFY_PLAYLISTS_URL")


def get_auth_header(token):
    return {"Authorization": "Bearer " + token}


def get_auth_url():
    """
    Returns an authentication URL for Spotify.
    This URL needs to be used for authenticating the app for required permissions.
    """
    params = {
        "response_type": "code",
        "client_id": client_id,
        "scope": scope,
        "redirect_uri": redirect_uri,
        "state": str(random.randint(1, 10)),
    }
    url = auth_url + urllib.parse.urlencode(params)
    return url


def get_token(code, spinner):
    """
    Returns an access token to be used for making Spotify API calls
    """
    try:
        spinner.text = "Generating Spotify access token"
        spinner.start()
        auth_string = "{client_id}:{client_secret}".format(
            client_id=client_id, client_secret=client_secret
        )
        base64_encoded_auth = str(
            base64.b64encode(auth_string.encode("utf-8")), "utf-8"
        )
        headers = {
            "Authorization": "Basic " + base64_encoded_auth,
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
        }
        result = post(token_url, headers=headers, data=data)
        json_result = json.loads(result.content)
        token = json_result["access_token"]
        spinner.stop()
        return token
    except:
        raise RuntimeError(
            "Some error occurred while generating access token for Spotify"
        )


def get_playlists(token, spinner):
    """
    Returns a list of all playlists created or saved by the user
    """
    try:
        spinner.text = "Getting all Spotify playlists"
        spinner.start()
        headers = get_auth_header(token)
        result = get(playlist_url, headers=headers)
        json_result = json.loads(result.content)
        spinner.stop()
        return json_result["items"]
    except:
        raise RuntimeError(
            "Some error occurred while getting your playlists from Spotify"
        )


def get_playlist_tracks(name, url, token, spinner):
    """
    Returns a list of all tracks from a specific playlist based on the playlistId
    """
    try:
        spinner.text = "Getting track list for {name} playlist".format(name=name)
        spinner.start()
        headers = get_auth_header(token)
        result = get(url, headers=headers)
        json_result = json.loads(result.content)
        spinner.stop()
        return json_result["items"]
    except:
        raise RuntimeError(
            "Some error occurred while getting your list of tracks from your playlist"
        )


def write_playlist_to_disk(playlists_directory, file_name, tracks):
    """
    Writes a given playlist to the disk
    """
    try:
        with open(playlists_directory + file_name, "a") as f:
            tracks_list = [
                {
                    "name": x["track"]["name"],
                    "artist": x["track"]["artists"][0]["name"],
                }
                for x in tracks
            ]
            f.write(json.dumps(tracks_list))
            print(
                colored(
                    str(file_name).strip() + " saved to directory",
                    "light_blue",
                )
            )
    except:
        raise RuntimeError("Some error occurred while saving playlist to disk")
