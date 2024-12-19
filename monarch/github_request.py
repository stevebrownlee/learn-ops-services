import os, json, time, requests

class GithubRequest(object):
    def __init__(self):
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/vnd.github+json",
            "User-Agent": "nss/ticket-migrator",
            "X-GitHub-Api-Version": "2022-11-28",
            "Authorization": f'Bearer {os.getenv("GITHUB_PAT")}'
        }

    def get(self, url):
        return self.request_with_retry(lambda: requests.get(url=url, headers=self.headers, timeout=10))

    def put(self, url, data):
        json_data = json.dumps(data)

        return self.request_with_retry(lambda: requests.put(url=url, data=json_data, headers=self.headers, timeout=10))

    def post(self, url, data):
        json_data = json.dumps(data)

        try:
            result = self.request_with_retry(lambda: requests.post(url=url, data=json_data, headers=self.headers, timeout=10))
            return result

        except TimeoutError:
            print("Request timed out. Trying next...")

        except ConnectionError:
            print("Request timed out. Trying next...")

        return None

    def request_with_retry(self, request):
        retry_after_seconds = 1800
        number_of_retries = 0

        response = request()

        while response.status_code == 403 and number_of_retries <= 10:
            number_of_retries += 1
            self.sleep_with_countdown(retry_after_seconds)
            response = request()

        return response

    def sleep_with_countdown(self, countdown_seconds):
        ticks = countdown_seconds * 2
        for count in range(ticks, -1, -1):
            if count:
                time.sleep(0.5)
