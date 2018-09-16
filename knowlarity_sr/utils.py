import json

import requests


def call(k_number=False, agent_number=False, customer_number=False, x_api_key=False, authorization=False):
    url = "https://kpi.knowlarity.com/Basic/v1/account/call/makecall"
    payload = {
        "k_number": k_number,
        "agent_number": agent_number,
        "customer_number": customer_number,
    }
    headers = {
        'x-api-key': x_api_key,
        'authorization': authorization,
        'content-type': "application/json",
        'cache-control': "no-cache",
    }
    response = requests.request("POST", url, data=json.dumps(payload), headers=headers)
    return eval(response.text)
