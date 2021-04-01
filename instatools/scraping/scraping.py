import itertools
import json
import logging
from pathlib import Path
import shutil
from time import sleep
import requests

logging.basicConfig(filename='scraper.log',
                    level=logging.INFO,
                    format='%(asctime)s | %(levelname)s | %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    )


def set_api_session(sessionid, timeout=3, max_retries=2):
    """Set up the Requests package session to access Instagram API.

    Provides authorization between consecutive requests.

    Args:
      sessionid: Obtained from the browser's cookie,
        user must be logged in with their Instagram account.
      timeout: In seconds (Default value = 3).
      max_retries:  (Default value = 2)

    Returns:
      Requests session along with its parameters.
    """

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    instagram_adapter = requests.adapters.HTTPAdapter(max_retries=max_retries)
    session = requests.Session()
    session.cookies['sessionid'] = sessionid
    session.mount('https://www.instagram.com/', instagram_adapter)
    return (session, headers, timeout)


def extract_posts(base_url, output_path, session_setup):

    session, headers, timeout = session_setup
    Path(output_path).mkdir(exist_ok=True)

    max_id = ''

    for i in itertools.count(start=1):

        if max_id:
            url = base_url + f"&max_id={max_id}"
        else:
            url = base_url

        try:
            response = session.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            response_content = response.json()
        except Exception:
            logging.info(f'API Response & parsing, {i} interation', exc_info=True)

        file_name = Path(output_path, str(i) + '.json')
        with open(file_name, "w", encoding='utf8') as file:
            json.dump(response_content, file, ensure_ascii=False)

        if '/locations/' in base_url:
            api_endpoint = 'location'
        elif '/tags/' in base_url:
            api_endpoint = 'hashtag'
        max_id = response_content['graphql'][api_endpoint][f'edge_{api_endpoint}_to_media']['page_info']['end_cursor']
        if not max_id or max_id is None:
            logging.info(f'All {i} available pages scrapped')
            break

        sleep(2)


def _request_image(url, file_name, output_path, session_setup):

    session, headers, timeout = session_setup

    try:
        response = session.get(
            url, stream=True, headers=headers, timeout=timeout)
        response.raise_for_status()
    except Exception:
        logging.info(f'API Response, filename: {file_name}', exc_info=True)

    file_name = Path(output_path, file_name + '.jpg')
    with open(file_name, 'wb') as file:
        shutil.copyfileobj(response.raw, file)


def extract_images(posts, output_path, session_setup):

    Path(output_path).mkdir(exist_ok=True)
    paths = Path(output_path).glob('**/*.jpg')
    extracted_images = [path.stem for path in paths]

    print(f'Already extracted images: {len(extracted_images)}')

    for id, post in posts.items():

        id = id
        img_url = post['display_url']

        if id not in extracted_images:
            _request_image(img_url, id, output_path, session_setup)
            sleep(2)
