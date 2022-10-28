import requests

from requests.adapters import HTTPAdapter

http_cli = requests.Session()
http_cli.mount('http://', HTTPAdapter(max_retries=3))
http_cli.mount('https://', HTTPAdapter(max_retries=3))
