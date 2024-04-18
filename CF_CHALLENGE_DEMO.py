# -*- coding: utf-8 -*-
import requests
import time
import tls_client

# TODO: Your api key
API_KEY = ""
proxy = ""

# TODO: Your target site url:
page_url = ''



def call_capsolver():
    data = {
        "clientKey": API_KEY,
        "task": {
            "type": 'AntiCloudflareTask',
            "websiteURL": page_url,
            "proxy": proxy,
        }
    }
    uri = 'https://api.capsolver.com/createTask'
    res = requests.post(uri, json=data)
    resp = res.json()
    task_id = resp.get('taskId')
    if not task_id:
        print("no get taskId:", res.text)
        return
    print('created taskId:', task_id)

    while True:
        time.sleep(1)
        data = {
            "clientKey": API_KEY,
            "taskId": task_id
        }
        response = requests.post('https://api.capsolver.com/getTaskResult', json=data)
        resp = response.json()
        status = resp.get('status', '')
        if status == "ready":
            print("successfully => ", response.text)
            return resp.get('solution')
        if status == "failed" or resp.get("errorId"):
            print("failed! => ", response.text)
            return


def request_site(solution):
    session = tls_client.Session(
        client_identifier="chrome_120",
        random_tls_extension_order=True
    )
    return session.get(
        page_url,
        headers=solution.get('headers'),
        cookies=solution.get('cookies'),
        proxy=proxy,
    )


def main():
    solution = {
        "headers": {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "sec-fetch-site": "none",
            "sec-fetch-mode": "navigate",
            "sec-fetch-user": "?1",
            "sec-fetch-dest": "document",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en-US,en;q=0.9",
        }
    }
    # first request (check your proxy):
    res = request_site(solution)
    print('1. response status code:', res.status_code)
    if res.status_code != 403:
        print("your proxy is good and didn't get the cloudflare challenge")
        return
    elif 'window._cf_chl_opt' not in res.text:
        print('==== proxy blocked ==== ')
        return

    # call capSolver:
    solution = call_capsolver()
    if not solution:
        return

    # second request (verify solution):
    res = request_site(solution)
    print('2. response status code:', res.status_code)


if __name__ == '__main__':
    main()
