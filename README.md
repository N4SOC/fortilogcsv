# Forti Log CSV Converter
## Converts fortigate log exports into CSV files

Fortigate logs export in a "field1=value","field2=value" format which isn't easily parsed  
This script pulls out each field and compiles the events into a single CSV file

### Usage
1. Export .log file from Fortigate
2. Convert log to csv:

````Python3 convert.py path/to/fortigate.log````


