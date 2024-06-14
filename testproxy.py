import pprint
import requests
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get Bright Data proxy credentials from environment variables
username = os.getenv('BRIGHTDATA_PROXY_USER')
password = os.getenv('BRIGHTDATA_PROXY_PASSWORD')

host = 'brd.superproxy.io'
port = 22225

proxy_url = f'http://{username}:{password}@{host}:{port}'

proxies = {
    'http': proxy_url,
    'https': proxy_url
}


url = "http://lumtest.com/myip.json"
response = requests.get(url, proxies=proxies)
pprint.pprint(response.json())
