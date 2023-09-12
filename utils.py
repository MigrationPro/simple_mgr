import logging
import sys
import requests


def find_logger(name: str):
    logger = logging.getLogger(name)
    handler = logging.StreamHandler(sys.stdout)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def get_products(source_url, source_token):
    url = f"https://{source_url}.myshopify.com/admin/api/2023-07/products.json"

    payload = {}
    headers = {
        'X-Shopify-Access-Token': f'{source_token}'
    }

    response = requests.get(url, headers=headers, data=payload)

    return response.json()
