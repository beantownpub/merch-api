import logging
import requests


def sendNotifications(data):
    url = 'http://172.17.0.5:5012/v1/contact/merch'
    headers = {'Content-Type': 'application/json'}
    req = requests.post(url, headers=headers, json=data)
    logging.info('Contact Request: %s', req.status_code)
