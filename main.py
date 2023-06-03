import requests
import pprint

filename = "comic.png"
url = "https://xkcd.com/353/info.0.json"
response = requests.get(url)
response.raise_for_status()
comic_info = response.json()
comic_url = comic_info["img"]
response = requests.get(comic_url)
response.raise_for_status()

with open(filename, 'wb') as file:
    file.write(response.content)

