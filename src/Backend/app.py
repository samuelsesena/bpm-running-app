from flask import Flask, jsonify
import requests
import json
import time
from http import HTTPStatus
from dotenv import load_dotenv
import os

load_dotenv()  # loads variables from .env into environment

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
BPM_KEY = os.getenv("BPM_KEY")
TOKEN_FILE_PATH = "spotify_token.json"



app = Flask(__name__)

@app.route("/")
def hello_world():
    return "hello, it is working!"

def get_new_spotify_token():
    try:
        spotify_token_url = "https://accounts.spotify.com/api/token"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "grant_type": "client_credentials",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET
        }
        response = requests.post(spotify_token_url, headers=headers, data=data)
        response.raise_for_status()
        res_data = response.json()
        token_info = res_data
        token_info["expires_in"] += time.time()
        with open("spotify_token.json", "w") as f:
            json.dump(token_info, f)

        print(f"Status Code: {response.status_code}")
        print(f"Response Body: Grabbed a new token! {token_info}")

        return token_info
        

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return e.response.json()
    
'''
TO DO:
- When a user tries using one of the endpoints, first check the token
    - get_token() function
        - function needs to check if token is valid
        - if so, return the token
        - if not, call the token endpoint
'''

def ensure_token_file_exists(path="spotify_token.json"):
    if not os.path.exists(path):
        default_data = {}
        with open(path, "w") as f:
            json.dump(default_data, f, indent=4)
        print(f"{path} created with default structure.")

def get_token():
    ensure_token_file_exists(TOKEN_FILE_PATH)

    with open("spotify_token.json","r") as f:
        token_info = json.load(f)
    
    if not token_info or time.time() >= token_info["expires_in"]:
        token_info = get_new_spotify_token()
    else:
        print(f"Status Code: {HTTPStatus.OK}")
        print(f"Response Body: Token is still valid! {token_info}")
    return token_info

@app.route("/playlist")
def grab_playlist_info():
    try:
        playlist_id = "6u3D6UiOmbGnQWMnLo713A"
        spotify_playlist_api = f"https://api.spotify.com/v1/playlists/{playlist_id}"

        spotify_token = get_token()
        params = {
            "fields" : "tracks.items(track(name,href,album(artists,name,href,images)))"
        }
        headers ={
            "Authorization": f"{spotify_token["token_type"]} {spotify_token["access_token"]}"
        }

        response = requests.get(spotify_playlist_api, headers=headers, params=params)
        response.raise_for_status()

        res_data = response.json()
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {res_data}")
        return jsonify(res_data)

    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

@app.route("/artist")
def grab_artist_info():
    try:
        sample_artist_id = "630wzNP2OL7fl4Xl0GnMWq"
        spotify_artist_api = f"https://api.spotify.com/v1/artists/{sample_artist_id}"

        spotify_token = get_token()
        headers ={
            "Authorization": f"{spotify_token["token_type"]} {spotify_token["access_token"]}"
        }

        response = requests.get(spotify_artist_api, headers=headers)
        response.raise_for_status()

        res_data = response.json()
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {res_data}")
        return jsonify(res_data)

    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/song-bpm")
def grab_song_bpm():
    try:
        song_id = "16D5bGymrzpi9ZlnYXB5ql"
        bpm_song_api = f"https://api.getsong.co/song/"

        params = {
            "api_key": BPM_KEY,
            "id": song_id
        }

        response = requests.get(bpm_song_api, params=params)
        response.raise_for_status()

        res_data = response.json()
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {res_data}")
        return jsonify(res_data)

    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500