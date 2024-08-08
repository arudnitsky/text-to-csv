# Text-to-CSV

Text-to-csv.py is a python tool to create a CSV file of translations from Ukrainian to English for importing into Anki. Input is a text file of Ukrainian words or phrases. Uses rozmovnyk for translation.
```
 $ python text-to-csv.py
Usage: text-to-csv.py file_to_translate

text-to-csv.py creates a csv file suitable for importing into Anki
   Input is a text file of Ukrainian words or phrases, one to a line.
   Output is written to stdout. If you redirect it to to a file,
    progress will be written to stderr.
```

This repo includes parse-clipping-file.py, a python utility to produce a suitable input file for text-to-csv.py from a Kindle clippimg file.
```
 $ python parse-clipping-file.py --help
usage: parse-clipping-file.py [-h] [-f FILTER] [-w | -p] filename

Prints Kindle highlights from a Kindle clippings

positional arguments:
  filename              Kindle clippings file

options:
  -h, --help            show this help message and exit
  -f FILTER, --filter FILTER
                        Select only books with this title or author
  -w, --words           Select only single words
  -p, --phrases         Select only phrases

Writes highlights to standard out, one highlight per line. Strips trailing punctuation and lowercases single words.
```
