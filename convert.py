import argparse
import csv
import re
import sys
import logging
from pathlib import Path
from typing import Dict, List, Tuple

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger("fortilog_csv")

_COLOUR_GREEN = "\033[32m"
_COLOUR_BLUE = "\033[34m"
_COLOUR_YELLOW = "\033[93m"
_COLOUR_END = "\033[0m"


def print_success(message, *args) -> None:
    if args:
        message = message % args
    logger.info("🟢 %s%s%s", _COLOUR_GREEN, message, _COLOUR_END)


def print_info(message, *args) -> None:
    if args:
        message = message % args
    logger.info("🔵 %s%s%s", _COLOUR_BLUE, message, _COLOUR_END)


def print_warn(message, *args) -> None:
    if args:
        message = message % args
    logger.warning("🟠 %s%s%s", _COLOUR_YELLOW, message, _COLOUR_END)


# Regex matches "field=value" or "field=""more words""" syntax
PATTERN = re.compile(
    r'(\w+)(?:=)(?:"{1,3}([^"]+)"{1,3})|(\w+)=(?:([^\s]+))'
)


def write_to_file(headers: List[str], events: List[Dict[str, str]], outfile: str) -> None:
    """Write events to the specified output file, using the specified headers

    Args:
        headers (List[str]): headers to be used
        events (List[Dict[str, str]]): events to be written to the file
        outfile (str): output file
    """
    print_info("Writing CSV to %s", outfile)

    # Added the newline option to prevent blank rows from outputting to CSV
    with open(outfile, "w", newline="", encoding="UTF-8") as fileh:
        csvfile = csv.DictWriter(fileh, headers)
        csvfile.writeheader()  # Write headers
        for row in events:
            csvfile.writerow(row)  # write data

    print_success(
        "CSV write to %s done: rows=%d, cols=%d",
        outfile,
        len(events),
        len(headers)
    )


def process_log_lines(lines: List[str]) -> Tuple[List[Dict[str, str]], List[str]]:
    """Process log lines

    Args:
        lines (List[str]): Log lines to be processed

    Returns:
        Tuple[List[Dict[str, str]], List[str]]: Returns tuple of events and headers
    """
    events: List[Dict[str, str]] = []  # List to hold individual event dicts
    headers: List[str] = []
    headers_seen: set[str] = set()

    print_info("Processing log lines")
    for line in lines:
        event = {}
        match = PATTERN.findall(line)  # Find all regex matches on each line
        for group in match:
            # add a key,value pair to the dict for each key=value group
            if group[0] != "":
                key, val = group[0], group[1]
            else:
                key, val = group[2], group[3]
            event[key] = val

            if key not in headers_seen:
                headers_seen.add(key)
                headers.append(key)
        events.append(event)  # Add dict to list
    return events, headers


def convert_file(infile: str, outfile: str) -> None:
    """Convert a single Forti log file to CSV.

    Args:
        infile (str): input file path
        outfile (str): output file path
    """
    print_info("Reading logs from %s", infile)

    try:
        with open(infile, "r", encoding="UTF-8") as f:
            lines = f.readlines()
    except UnicodeDecodeError:
        print_warn("Errors during data extraction - non UTF8 data in file")
        sys.exit("Cannot continue without valid input data, program exiting")
    except:
        print_warn("Unexpected error reading input file")
        sys.exit("Cannot continue without valid input data, program exiting")

    events, headers = process_log_lines(lines)

    write_to_file(headers, events, outfile)

def convert_directory(dir_path: str, outfile: str) -> None:
    """Merge all .log files in the dir_path and convert them to a single CSV.add()

    Args:
        dir_path (str): Input directory containing .log files
        out_path (str): Output file
    """
    print_info("Merging log files from directory %s", dir_path)

    all_lines: List[str] = []
    path = Path(dir_path)
    for file in path.glob("*.log"):
        if file.is_file() and file.name.endswith(".log"):
            print_info("Reading logs from %s", file)
            with open(file, "r", encoding="UTF-8", buffering=1 << 20) as f:
                all_lines.extend(f.readlines())

    events, headers = process_log_lines(all_lines)

    write_to_file(headers, events, outfile)

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Script for converting fortigate CSV export to true CSV",
        prog="forticonvert.py",
        usage="%(prog)s --infile=filepath --outfile=filepath",
    )
    parser.add_argument(
        "--infile", type=str, help="Fortigate export file to convert", required=True
    )
    parser.add_argument(
        "--outfile", type=str, help="Location to save converted CSV file", required=True
    )
    parser.add_argument(
        "-d", "--directory",
        action="store_true",
        help="Indicates that the input is a directory containing multiple .log files to merge and convert",
    )
    args = parser.parse_args()

    # Check for existance of input and output files
    isInputDirectory = args.directory
    inputFile = Path(args.infile)
    if not isInputDirectory and not inputFile.is_file():
        print_warn("Source file not found")
        sys.exit("Cannot continue without valid input data, program exiting")
        
    if isInputDirectory and not inputFile.is_dir():
        print_warn("Source directory not found")
        sys.exit("Cannot continue without valid input data, program exiting")

    outputFile = Path(args.outfile)

    if not outputFile.parent.is_dir():
        print_warn("Output directory does not exist")
        sys.exit("Cannot continue without valid output path, program exiting")

    if outputFile.exists() and outputFile.is_dir():
        print_warn("Output path is a directory, please specify a file")
        sys.exit("Cannot continue without valid output file, program exiting")

    if outputFile.is_file():
        print_warn("Destination file already exists - script will overwrite this")

    if isInputDirectory:
        convert_directory(args.infile, args.outfile)
    else:
        convert_file(args.infile, args.outfile)


if __name__ == "__main__":
    main()
