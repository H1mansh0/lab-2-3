"""Module for spotify"""
import os
import json
import base64
import folium
from geopy.geocoders import Nominatim
import pycountry
from dotenv import load_dotenv
from requests import post,get


load_dotenv()

geocoder = Nominatim(user_agent="my_requests")

client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')


def get_token() -> str:
    """
    Gets autorization token
    """
    auth_string = client_id + ':' + client_secret
    auth_bytes = auth_string.encode('utf-8')
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = 'https://accounts.spotify.com/api/token'
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {'grant_type': "client_credentials"}
    result = post(url, headers=headers, data=data)

    j_file = json.loads(result.content)
    token_ = j_file['access_token']

    return token_

def auth_header(token_: str) -> dict:
    """
    Gets authorization header
    """
    return {'Authorization': "Bearer " + token_}

def search_for_artist(token_: str, name: str, artist=True) -> dict:
    """
    Gets json file for artist
    """
    url = 'https://api.spotify.com/v1/search'
    headers = auth_header(token_)
    if artist:
        query = f'?q={name}&type=artist&limit=1'
        q_url = url + query
        result = get(q_url, headers=headers)
        j_file = json.loads(result.content)['artists']['items']
        return j_file[0]
    else:
        query = f'?q={name}&type=track&limit=1'
        q_url = url + query
        result = get(q_url, headers=headers)
        j_file = json.loads(result.content)
        return j_file

def the_most_popular_trecks(token_: str, art_id: str) -> list:
    """
    Gets 10 the most popular songs
    """
    url = f'https://api.spotify.com/v1/artists/{art_id}/top-tracks?country=US'
    header = auth_header(token_)

    result = get(url, headers=header)
    j_file = json.loads(result.content)['tracks']
    result = [ele['name'] for ele in j_file]
    return result

def available_markets(token_: str):
    """
    Gets available markets
    """
    url = '	https://api.spotify.com/v1/markets'
    header = auth_header(token_)

    result = get(url, headers=header)
    j_file = json.loads(result.content)

    return j_file['markets']

def main(artist_name):
    html = """
    <b>Song name</b>: {}<br>
    <b>Country</b>: {}
    """
    token = get_token()
    artist_id = search_for_artist(token, artist_name)['id']
    track = the_most_popular_trecks(token, artist_id)[0]
    markets = search_for_artist(token, track, artist=False)['tracks']['items'][0]['available_markets']
    country_names = [pycountry.countries.get(alpha_2=ele).name.split(', ')[0]
                      for ele in markets if pycountry.countries.get(alpha_2=ele)]
    country_coords = [(ele, geocoder.geocode(ele).latitude, geocoder.geocode(ele).longitude) for ele in country_names]
    
    
    map = folium.Map()
    fg = folium.FeatureGroup(name="Films")
    fg.add_child(folium.GeoJson(data=open('world1.json', 'r', encoding='utf-8-sig').read(),
                                 style_function=lambda x: {'fillColor':'green'
                                                    if x['properties']['NAME'] in country_names else 'darkblue'}))
    for ele in country_coords:
        iframe = folium.IFrame(html=html.format(track, ele[0]), width=380, height=80)
        fg.add_child(folium.Circle(location=[ele[1], ele[2]], popup=folium.Popup(iframe), color = 'green'))
    map.add_child(fg)
    return map.save('templates/vlad.html')
