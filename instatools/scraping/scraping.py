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
                    datefmt='%Y-%m-%d %H:%M:%S',)


class Scraper:
    """
    Retrieve posts and images from Instragram API.

    Attributes:
        session_id (str): Obtained from the browser's cookie,
            user must be logged in with their Instagram account.
        session_path (str): Directory to store the extracted content.

    Methods:
        set_api_session: Set up the Requests package session
            to access Instagram API.
        extract_posts: Retrieve posts from Instagram API.
        extract_images: Retrieve images from Instagram posts.


    """

    def __init__(self, session_id, session_path):
        self.session_id = session_id
        self.session_path = session_path
        self._session = None
        self._headers = None
        self._timeout = 0
        self._api_endpoint = None

    def set_api_session(self, timeout=3, max_retries=2):
        """Set up the Requests package session to access Instagram API.

        Provides authorization between consecutive requests.

        Args:
            timeout (int): Default value = 3.
            max_retries (int): Default value = 2.

        """
        adapter = requests.adapters.HTTPAdapter(max_retries=max_retries)
        self._session = requests.Session()
        self._session.cookies['sessionid'] = self.session_id
        self._session.mount('https://www.instagram.com/', adapter)
        self._headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
        }
        self._timeout = timeout
        return self

    def extract_posts(self, base_url):
        """Retrieve posts from Instagram API.

        Results are stored in batches of ~60 posts in JSON files.

        Args:
            base_url (str): Full url to Instagram content,
                e.g. 'https://www.instagram.com/explore/tags/medialabkatowice/'

        """
        Path(self.session_path, 'posts', self._api_endpoint).mkdir(parents=True, exist_ok=True)
        max_id = ''

        for i in itertools.count(start=1):

            if max_id:
                url = f"{base_url}?__a=1&max_id={max_id}"
            else:
                url = f"{base_url}?__a=1"

            try:
                response = self._session.get(url, headers=self._headers, timeout=self._timeout)
                response.raise_for_status()
                response_content = response.json()
            except Exception:
                logging.info(f'API Response & parsing, {i} interation', exc_info=True)

            file_name = Path(self.session_path, 'posts', self._api_endpoint, str(i) + '.json')
            with open(file_name, "w", encoding='utf8') as file:
                json.dump(response_content, file, ensure_ascii=False)

            if '/tags/' in base_url:
                max_id = response_content['data']['recent'].get('next_max_id')

            elif '/locations/' in base_url:
                max_id = response_content['native_location_data']['recent'].get('next_max_id')
            if not max_id or max_id is None:
                break

            sleep(2)

    def _request_image(self, url, file_name):
        """Helper method to retrieve an image (jpg) from Instagram API.

        Args:
            url (str): Path to the image extracted from Instagram post.
            file_name (str): Output file name coresponding to the post id.

        """
        try:
            response = self._session.get(
                url, stream=True, headers=self._headers, timeout=self._timeout)
            response.raise_for_status()
        except Exception:
            logging.info(f'API Response, filename: {file_name}', exc_info=True)

        file_path = Path(self.session_path, 'images', str(file_name) + '.jpg')
        with open(file_path, 'wb') as file:
            shutil.copyfileobj(response.raw, file)

    def extract_images(self, posts):
        """Retrieve images from Instagram posts.

        Checks recursively for already downloaded images to facilitate
        extraction in batches.

        Args:
            posts (dict): Collection of preprocessed posts.

        """
        Path(self.session_path, 'images').mkdir(parents=True, exist_ok=True)
        image_paths = Path(self.session_path).glob('**/*.jpg')
        extracted_images = [path.stem for path in image_paths]

        for id, post in posts.items():
            id = id
            img_url = post['display_url']

            if id not in extracted_images:
                self._request_image(img_url, id)
                sleep(2)


class HashtagScraper(Scraper):
    """Retrieve posts and images from Instragram API for a selected hashtag.

    Attributes:
        session_id (str): Obtained from the browser's cookie,
            user must be logged in with their Instagram account.
        session_path (str): Directory to store the extracted content.

    """

    def __init__(self, session_id, session_path):
        super().__init__(session_id, session_path)
        self._api_endpoint = 'hashtag'


class LocationScraper(Scraper):
    """Retrieve posts and images from Instragram API for a selected location.

    Attributes:
        session_id (str): Obtained from the browser's cookie,
            user must be logged in with their Instagram account.
        session_path (str): Directory to store the extracted content.

    """

    def __init__(self, session_id, session_path):
        super().__init__(session_id, session_path)
        self._api_endpoint = 'location'
