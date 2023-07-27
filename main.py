import requests
from dotenv import load_dotenv
import os
import random


def select_random_comic():
    last_comic_url = "https://xkcd.com/info.0.json"
    response = requests.get(last_comic_url)
    response.raise_for_status()
    last_comic_number = response.json()["num"]
    random_comic_number = random.randint(1, last_comic_number)
    url = f'https://xkcd.com/{random_comic_number}/info.0.json'
    response = requests.get(url)
    response.raise_for_status()
    comic_info = response.json()
    comic_url = comic_info["img"]
    comment = comic_info['alt']
    name = comic_info['title']
    return comic_url, comment, name


def save_image(url, name):
    filename = f"{name}.png"
    response = requests.get(url)
    response.raise_for_status()
    with open(filename, 'wb') as file:
        file.write(response.content)


def upload_comic_on_server(token, version, group_id, name):
    params = {
        "access_token": token,
        "group_id": group_id,
        "v": version
     }
    url = "https://api.vk.com/method/photos.getWallUploadServer"
    response = requests.get(url, params = params)
    response.raise_for_status()
    check_errors(response)
    upload_url = response.json()["response"]["upload_url"]
    with open(f'{name}.png', 'rb') as file:
        url = upload_url
        files = {
            'photo': file
         }
        response = requests.post(url, files = files)
    response.raise_for_status()
    check_errors(response)
    upload_response = response.json()
    server = upload_response['server']
    photo = upload_response['photo']
    upload_hash = upload_response['hash']
    return server, photo, upload_hash


def save_comic_to_wall(photo, server, upload_hash, token, version, group_id):
    url = "https://api.vk.com/method/photos.saveWallPhoto"
    params = {
        "access_token": token,
        "group_id": group_id,
        "v": version,
        "photo": photo,
        "server": server,
        "hash": upload_hash
     }
    response = requests.post(url, params = params)
    response.raise_for_status()
    check_errors(response)
    upload_response = response.json()['response'][0]
    media_id = upload_response['id']
    owner_id = upload_response['owner_id']
    return media_id, owner_id


def publish_comic_to_group(owner_id, media_id, token, version, group_id, comment):
    url = 'https://api.vk.com/method/wall.post'
    attachments = f"photo{owner_id}_{media_id}"
    params = {
        "access_token": token,
        "v": version,
        "attachments": attachments,
        "owner_id": -group_id,
        "message": comment,
        "from_group": '1'
     }
    response = requests.post(url, params = params)
    response.raise_for_status()
    check_errors(response)


def delete_image(name):
    myfile = f'{name}.png'
    if os.path.isfile(myfile):
        os.remove(myfile)


def check_errors(response):
    if "error" in response:
        message = response["error"]["error_msg"]
        code = response["error"]["error_code"]
        raise requests.HTTPError(code, message)


def main():
    load_dotenv()
    vk_apikey = os.getenv("VK_TOKEN")
    group_id = int(os.getenv("GROUP_ID"))
    version = 5.131
    try:
        comic_url, comment, name = select_random_comic()
        save_image(comic_url, name)
        server, photo, upload_hash = upload_url_on_server(vk_apikey, version, group_id, name)
        media_id, owner_id = save_comic_to_wall(photo, server, upload_hash, vk_apikey, version, group_id)
        publish_comic_to_group(owner_id, media_id, vk_apikey, version, group_id, comment)
    finally:
        delete_image(name)


if __name__ == "__main__":
    main()

