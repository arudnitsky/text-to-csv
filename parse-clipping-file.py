import string
import sys
from io import TextIOWrapper
from typing import Generator

from pydantic import BaseModel


class Clipping(BaseModel):
    title_and_author: str
    highlight_location_and_time: str
    blank_line: str
    highlight:str
    separator: str

def cleanup_line( line:str) -> str:
    line = line.rstrip('\n')
    line = line.translate(line.maketrans('', '', string.punctuation))
    line = line[:1].lower() + line[1:]
    return line

def read_in_clipping(file_object: TextIOWrapper ) -> Generator[Clipping, None, None]:
    """Lazy function (generator) to read a file piece by piece and group them into Clipping instances."""
    chunk_size=5
    while True:
        lines = []
        for _ in range(chunk_size):
            line = file_object.readline()
            if not line:
                break
            lines.append(cleanup_line(line))
        if not lines:
            break
        if len(lines) == chunk_size:
            yield Clipping(
                title_and_author=lines[0],
                highlight_location_and_time=lines[1],
                blank_line=lines[2],
                highlight=lines[3],
                separator=lines[4]
            )
        else:
            raise ValueError(f"Truncated data. Did not read {chunk_size} lines.")

def process_input_file(file_path: str):
    with open(file_path, 'r') as file:
        for clippings in read_in_clipping(file):
            if clippings:
                print(clippings.highlight)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.stderr.write(f"Usage: {sys.argv[0]} file_to_process\n\n")
        sys.stderr.write(
            f"{sys.argv[0]} Parses a Kindle clippings file and prints highlights\n"
        )

        exit(1)

    process_input_file(sys.argv[1])
    exit(0)
