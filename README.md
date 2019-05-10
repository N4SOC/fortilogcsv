# Forti Log CSV Converter
## Converts fortigate log exports into CSV files

Fortigate logs export in a "field1=value","field2=value" format which isn't easily parsed  
This script pulls out each field and compiles the events into a single CSV file

### Usage
Example: Export logs from Fortianalyzer as "csv"  

![Export Dialog](https://rothe.uk/images/forti.png)  

````Python3 convert.py path/to/fortigate.log````

![Sample Output](https://rothe.uk/images/forti2.png)  