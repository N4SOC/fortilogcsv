import argparse
import codecs
import csv
import re
import sys
from pathlib import Path

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

args = parser.parse_args()


def print_success(message):
    colourGREEN = "\33[32m"
    colourEND = "\033[0m"
    print(f"🟢 {colourGREEN}{message}{colourEND}")


def print_info(message):
    colourBLUE = "\33[34m"
    colourEND = "\033[0m"
    print(f"🔵 {colourBLUE}{message}{colourEND}")


def print_warn(message):
    colourRED = "\033[91m"
    colourEND = "\033[0m"
    print(f"🟠 {colourRED}{message}{colourEND}")


# Check for existance of input and output files
inputFile = Path(args.infile)
if not inputFile.is_file():
    print_warn("Source file not found")
    sys.exit("Cannot continue without valid input data, program exiting")

outputFile = Path(args.outfile)
if inputFile.is_file():
    print_warn("Destination file already exists - script will overwrite this")


# Open log file for read if exists
print_info("Reading logs from " + args.infile)
try:
    log_data = codecs.open(args.infile, "r", encoding="UTF-8")
except:
    print_warn("Invalid input file specified")
    sys.exit("Cannot continue without valid input data, program exiting")

# Regex matches "field=value" or "field=""more words""" syntax
pattern = re.compile(
    r'(\w+)(?:=)(?:"{1,3}([^"]+)"{1,3})|(\w+)=(?:([^\s]+))'
)
events = []  # List to hold individual event dicts

print_info("Parsing CSV and extracting data")
try:
    for line in log_data:
        event = {}
        match = pattern.findall(line)  # Find all regex matches on each line
        for group in match:
            # add a key,value pair to the dict for each key=value group
            if group[0] != "":
                event[group[0]] = group[1]
            else:
                event[group[2]] = group[3]
        events.append(event)  # Add dict to list
except IndexError:
    print_warn("Errors during data extraction - CSV doesn't match expected format")
    sys.exit("Cannot continue without valid input data, program exiting")
except UnicodeDecodeError:
    print_warn("Errors during data extraction - non UTF8 data in file")
    sys.exit("Cannot continue without valid input data, program exiting")

print_info("Processing log fields")
headers = []
for row in events:
    for key in row.keys():
        if not key in headers:
            headers.append(key)  # Compile a deduped list of headers
print_success(f"{len(headers)} fields identified")

print_info("Writing new CSV")
# Added the newline option to prevent blank rows from outputting to CSV
with open(args.outfile, "w", newline="") as fileh:
    csvfile = csv.DictWriter(fileh, headers)  # Write headers
    csvfile.writeheader()
    for row in events:
        csvfile.writerow(row)  # write data

print_success(f"Finished {str(len(events))} rows written to {args.outfile}")
