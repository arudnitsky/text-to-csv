import sys
from io import TextIOWrapper
from typing import Generator

from pydantic import BaseModel


class Clipping(BaseModel):
    type: str
    title_and_author: str
    highlight_location_and_time: str
    blank_line: str
    highlight: str
    separator: str


def cleanup_line(line: str) -> str:
    # remove punctuation if single word
    # to lowercase if single word
    line = line.rstrip("\n")
    # line = line.translate(
    #     line.maketrans("", "", string.punctuation)
    # )  # remove only the last character if punctuation

    # line = line[:1].lower() + line[1:]
    return line


def dump_lines(lines: list[str]):
    line_number = 0
    for line in lines:
        print(f"line {line_number}: '{line}'")
        line_number += 1


def dump_clipping(clipping):
    print("Clipping:")
    print(f" title_and_author:{clipping[0]}")
    print(f" hightlight_location and time '{clipping[1]}'")
    print(f" blank_line                   '{clipping[2]}'")
    print(f" highlight                    '{clipping[3]}'")
    print(f" separator                    '{clipping[4]}'")


def read_chunk(file_object: TextIOWrapper) -> list[str]:
    lines = []
    while True:
        line = file_object.readline()
        if not line:
            break
        lines.append(cleanup_line(line))
        if "====" in line:
            break
    # dump_lines(lines)
    return lines


def read_in_clipping(file_object: TextIOWrapper) -> Generator[Clipping, None, None]:
    """Lazy function (generator) to read a file piece by piece and group them into Clipping instances."""
    line_number = 0
    type = "unknown"
    while True:
        lines: list[str] = read_chunk(file_object)

        if not lines:
            return None

        line_number += len(lines)

        if "Note" in lines[1]:
            type = "note"
        elif "Highlight" in lines[1]:
            type = "highlight"
        elif "Bookmark" in lines[1]:
            type = "bookmark"

        if lines[len(lines) - 1] != "==========":
            dump_lines(lines)
            raise ValueError(f"No separator found in chunk near {line_number}")

        clipping: Clipping = Clipping(
            type=type,
            title_and_author=lines[0],
            highlight_location_and_time=lines[1],
            blank_line=lines[2],
            highlight=lines[3],
            separator=lines[4],
        )

        yield clipping


def process_input_file(file_path: str, search_string=None):
    with open(file_path, "r", encoding="utf-8-sig") as file:
        for clipping in read_in_clipping(file):
            if not clipping:
                break
            if clipping.type == "unknown":
                break;
            if clipping.type == "highlight":
                if search_string != None:
                    if search_string.casefold() in clipping.title_and_author.casefold():
                        if clipping.highlight != None:
                            print(clipping.highlight)
                else:
                    print(clipping.highlight)


if __name__ == "__main__":
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        sys.stderr.write(
            f"{sys.argv[0]} Parses a Kindle clippings file and prints highlights\n"
        )
        sys.stderr.write(
            f"Usage: {sys.argv[0]} file_to_process [optional book or author name]\n"
        )

        exit(1)

    process_input_file(sys.argv[1], sys.argv[2]) # fix this for no [2]
    exit(0)
