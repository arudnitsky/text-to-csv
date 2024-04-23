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
    text_lemma: str
    text_stressed_lemma: str
    translation: str
    stressed_translation: str
    translation_lemma: str
    translation_stressed_lemma: str
    detected_source_lang: str


deduplicated_entries: dict = {}


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


def deduplicate_and_save_batch(batch: List[DeeplTranslateResponse]):
    for item in batch:
        csv_line = f'"{item.text_stressed_lemma}'
        if " " in item.text or item.text == item.text_lemma:
            # phrase or text is the same as lemma. No need to print lemma
            csv_line += '",'
        else:
            # csv_line += f' ({item.stressed_text})",'
            csv_line += '",'
        csv_line += f'"{item.translation_stressed_lemma}"'

        # if (item.text_stressed_lemma) in deduplicated_entries:
        #     saved_line = deduplicated_entries[item.text_stressed_lemma]
        #     if len(csv_line) > len(saved_line):
        #         # keep the longer item
        #         deduplicated_entries[item.text_stressed_lemma] = csv_line
        # else:
        #     deduplicated_entries[item.text_stressed_lemma] = csv_line
        deduplicated_entries[item.text_stressed_lemma] = csv_line


def print_only_if_redirected(message: str):
    if not os.isatty(sys.stdout.fileno()):
        # stdout is not connected to a terminal
        sys.stderr.write(message)


def process_input_file(file_path: str):
    unique_lines = {}
    with open(file_path, "r") as file:
        for line in file:
            line = line.strip()
            if line == "" or line.startswith("#"):
                continue
            if not " " in line:
                line = line[:1].lower() + line[1:]
            # perform early deduplication
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

        deduplicate_and_save_batch(api_result)

    for line in deduplicated_entries.values():
        print(line)

    print_only_if_redirected("Done.\n")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.stderr.write(f"Usage: {sys.argv[0]} file_to_translate\n\n")
        sys.stderr.write(
            f"{sys.argv[0]} creates a csv file suitable for importing into Anki\n"
        )
        sys.stderr.write(
            "   Input is a text file of Ukrainian words or phrases, one to a line.\n"
            "   Output is written to stdout. If you redirect it to to a file,\n"
            "    progress will be written to stderr.\n"
        )

        exit(1)

    process_input_file(sys.argv[1])
    exit(0)
