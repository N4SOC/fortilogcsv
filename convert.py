import csv
import re
import sys

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

pattern = re.compile('\"(\w+)=\"{0,2}([\w\-\.:\ =]+)\"{1,3}') # Regex matches "field=value" or "field=""more words""" syntax
events = [] # List to hold individual event dicts

for line in log_data:
    event={}
    match = pattern.findall(line) # Find all regex matches on each line
    for group in match:
        event[group[0]] = group[1] # add a key,value pair to the dict for each key=value group
    events.append(event) # Add dict to list

print("[+] Processing log fields")
headers=[]
for row in events:
    for key in row.keys():
        if not key in headers:
            headers.append(key) # Compile a deduped list of headers

print("[+] Writing CSV")
with open(filename.split('.')[0] +'.csv', 'w') as fileh:
    csvfile = csv.DictWriter(fileh, headers) # Write headers
    csvfile.writeheader()
    for row in events:
        csvfile.writerow(row) #write data
print("[+] Finished - " + str(len(events)) +
      " rows written to " + filename.split('.')[0] + '.csv')
