import os
import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

LOGGER = logging.getLogger("sLogger")


class BaseConnection:
    def __init__(self, base_url_env: str, fallback_url: str = "http://localhost"):
        self.base_url = os.getenv(base_url_env, fallback_url)
        self.session = self._create_session()

    def _create_session(self):
        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["POST", "PUT", "DELETE", "PATCH"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def _headers(self):
        return {"Content-Type": "application/json"}

    def _url(self, path: str):
        return f"{self.base_url}{path}"

    def _handle_response(self, response: requests.Response, action: str):
        if response.status_code != 200:
            LOGGER.error(f"Erro ao {action}: {response.status_code} - {response.text}")
            raise Exception(
                f"Erro ao {action}: {response.status_code} - {response.text}"
            )
