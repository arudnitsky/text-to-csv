import argparse
import string
import sys
import time
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
    line = line.rstrip("\n")

    if not line:
        return line

    if line[0] == "=":
        return line

    if not " " in line:
        # single word

        # lowercase the first character
        line = line[:1].lower() + line[1:]

        if line[-1] in string.punctuation:
            # remove trailing punctuation
            line = line[:-1]

    return line


def cleanup_clipping(clipping: Clipping) -> Clipping:
    if type == "highlight":
        for index in range(2, len(clipping) - 1):
            clipping[index] = cleanup_line(clipping[index])
    return clipping


def dump_lines(lines: list[str]):
    line_number = 0
    for line in lines:
        print(f"line {line_number}: '{line}'")
        line_number += 1


def dump_chunk(chunk):
    # only works correctly for type == "highlight"
    # type "note" may be missing some lines
    print("Clipping:")
    print(f" title_and_author:{chunk[0]}")
    print(f" hightlight_location and time '{chunk[1]}'")
    print(f" blank_line                   '{chunk[2]}'")
    print(f" highlight                    '{chunk[3]}'")
    print(f" separator                    '{chunk[4]}'")


def read_chunk(file_object: TextIOWrapper) -> list[str]:
    lines = []
    while True:
        line = file_object.readline()
        if not line:
            break
        lines.append(cleanup_line(line))
        if "====" in line:
            break
    # dump_chunk(lines)
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

        # @@@@AMR Note that this does not correctly store all lines if len(lines) > 5
        clipping: Clipping = Clipping(
            type=type,
            title_and_author=lines[0],
            highlight_location_and_time=lines[1],
            blank_line=lines[2],
            highlight=lines[3],
            separator=lines[4],
        )

        yield clipping


def process_input_file(file_path: str, filter=None):
    with open(file_path, "r", encoding="utf-8-sig") as file:
        for clipping in read_in_clipping(file):
            if not clipping:
                break
            if clipping.type == "unknown":
                break
            if clipping.type == "highlight":
                if filter != None:
                    if filter.casefold() in clipping.title_and_author.casefold():
                        if clipping.highlight != None:
                            cleanup_clipping(clipping)
                            print(clipping.highlight)
                else:
                    print(clipping.highlight)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog=sys.argv[0],
        description="Prints Kindle highlights from a Kindle clippings",
        epilog="Writes highlights to standard out, one highlight per line. \n"
        "Strips trailing punctuation and lowercases single words.\n",
    )
    parser.add_argument("filename", help="Kindle clippings file")
    parser.add_argument(
        "-f", "--filter", help="Select only books with this title or author"
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-w", "--words", help="Select only single words", action="store_true"
    )
    group.add_argument(
        "-p", "--phrases", help="Select only phrases", action="store_true"
    )
    args = parser.parse_args()
    print(f"filename    : {args.filename}")
    print(f"--filter    : {args.filter}")
    print(f"-w --words  : {args.words}")
    print(f"-p --phrases: {args.phrases}")

    # start_time = time.time()
    process_input_file(args.filename, args.filter)
    # end_time = time.time()
    # print("elapsed time: {:.4f} seconds".format(end_time - start_time))

    exit(0)


# def getTitles():
#     "Returns alphabetically sorted list of titles. Removes duplicates."
#     # to-do: allow sorting using keys- last read or alphabetically.
#     from string import ascii_letters
#     titles = []
#     for unit in units:
#         title = unit[0]
#         # handling titles that start with u'\ufeff'.
#         if title[0] not in ascii_letters:
#             titles.append(title[1:])
#         else:
#             titles.append(title)
#     return sorted(list(set(titles)))
