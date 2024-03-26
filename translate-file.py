import os
import sys
from typing import List

import requests
from pydantic import BaseModel
from requests.adapters import HTTPAdapter, Retry


class DeeplTranslateRequest(BaseModel):
    text: List[str]
    source_lang: str
    target_lang: str


class DeeplTranslateResponse(BaseModel):
    text: str
    stressed_text: str
    translation: str
    stressed_translation: str
    detected_language: str


# https://stackoverflow.com/questions/15431044/can-i-set-max-retries-for-requests-request/35504626#35504626
retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
adapter = HTTPAdapter(max_retries=retries)


def call_api(
    translation_request: DeeplTranslateRequest,
) -> List[DeeplTranslateResponse]:
    url = "https://api.rozmovnyk.net/api/v1/deepl/translate"
    with requests.session() as session:
        session.mount("https://", adapter)
        response = session.post(url, json=translation_request.dict())
        # Assuming the response is a list of DeeplTranslateResponse objects
        api_result = [DeeplTranslateResponse(**item) for item in response.json()]
        return api_result


def output_csv(batch: List[DeeplTranslateResponse]):
    for item in batch:
        print(f'"{item.stressed_text}","{item.translation}"')


def print_only_if_redirected(message):
    if not os.isatty(sys.stdout.fileno()):
        # stdout is not connected to a terminal
        sys.stderr.write(message)


def process_file(file_path: str):
    unique_lines = {}
    with open(file_path, "r") as file:
        for line in file:
            line = line.strip()
            if line == "" or line.startswith("#"):
                continue
            unique_lines[line] = None
    print_only_if_redirected(f"Processing {len(unique_lines)} unique entries.\n")

    batch_number = 1
    lines_list = list(unique_lines.keys())
    for i in range(0, len(lines_list), 20):
        print_only_if_redirected(f"Translating batch {batch_number}.\n")
        batch = lines_list[i : i + 20]
        api_result = call_api(
            DeeplTranslateRequest(text=batch, source_lang="uk", target_lang="en-us")
        )
        for line in batch:
            del unique_lines[line]
        batch_number += 1
        output_csv(api_result)

    print_only_if_redirected("Done.\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.stderr.write(f"Usage: {sys.argv[0]} file_to_translate\n")
        exit(1)
    process_file(sys.argv[1])
    exit(0)

# Bug rendering Ukrainian letters in VSCode Terminal when using Menlo for Powerline: 
# print("ро́зголосу рете́льно розми́та")
# If I run the above statement via Run and Debug, the pronunciation stress accent is on the wrong letter in the VSCode terminal output.
# Same thing happens if I run it via python3 in the VSCode terminal
# It works correctly if I run the code in Mac iTerm2 or the Mac terminal. 
# Terminal › External: Osx Exec is set to iterm.app.
# I use Menlo for Powerline in the VSCode terminal, editor windows, and in iTerm2. There are no issues in the VSCode editors or in iTerm2. 
# Also, if I copy the incorrectly stressed text from the VSCode terminal into a VSCode editor window or into iTerm2 or terminal, the stress marks appear in the correct places.
# If I switch the terminal font to Monaco, the stress marks then appear in the correct places.
# This leads me to believe there is a problem with correctly rendering Ukrainian in the VSCode terminal in Menlo for Powerline