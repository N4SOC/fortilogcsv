import csv
import re
import sys

#fetch filename
import os.path


if len(sys.argv) > 1:
    filename = str(sys.argv[1])
else:
    raise Exception("No input file specified")

# Open log file for read if exists
print("[+] Reading logs from " + filename)
try:
    log_data = open(filename, "r")
except:
    raise Exception("Invalid input file")
# Regex matches "field=value" or "field=""more words""" syntax
pattern = re.compile('(\w+)(?:=)(?:"{1,3}([\w\-\.:\ =\+/%\(\)\[\],\?/\*>]+)"{1,3})|(\w+)=(?:([\w\-\.:\={}/]+))')
events = []  # List to hold individual event dicts

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

print("[+] Processing log fields")
headers = []
for row in events:
    for key in row.keys():
        if not key in headers:
            headers.append(key)  # Compile a deduped list of headers

print("[+] Writing CSV")

newfilename = os.path.splitext(filename)[0]+'.csv' # Get base file name from logfile

#Added the newline option to prevent blank rows from outputting to CSV
with open(newfilename, 'w', newline='') as fileh:
    csvfile = csv.DictWriter(fileh, headers)  # Write headers
    csvfile.writeheader()
    for row in events:
        csvfile.writerow(row)  # write data
print("[+] Finished - " + str(len(events)) + " rows written to " + newfilename)
