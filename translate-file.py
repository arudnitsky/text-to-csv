import requests
from requests.adapters import HTTPAdapter, Retry

# https://stackoverflow.com/questions/15431044/can-i-set-max-retries-for-requests-request/35504626#35504626
retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
adapter = HTTPAdapter(max_retries=retries)


def call_api(line):
    url = "https://api.rozmovnyk.net/api/v1/deepl/translate"
    with requests.session() as session:
        session.mount("https://", adapter)
        response = session.post(
            url, json={"text": [line], "source_lang": "uk", "target_lang": "en-us"}
        )
        print(response.json()[0])
    return {
        "text": response.json()[0]["stressed_text"],
        "translation": response.json()[0]["translation"],
    }


def process_file(file_path):
    unique_lines = set()
    with open(file_path, "r") as file:
        for line in file:
            line = line.strip()
            if line == "" or line.startswith("#"):
                continue
            unique_lines.add(line)

    for line in unique_lines:
        api_result = call_api(line)
        print(f'"{api_result["text"]}","{api_result["translation"]}"')


process_file("words.txt")

# Bugs: In the output, the stress accent is on the wrong letter when running in VSCode. Works fine with python3 ...
