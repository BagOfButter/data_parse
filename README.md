# Collecting data about companies using The Companies API
### Receiving an API token
To receive an API token, go to The Companies API website (https://www.thecompaniesapi.com/). Log in or create your account. Then, navigate to the "API tokens & usage" page (https://www.thecompaniesapi.com/settings/api-tokens-and-usage/), where you can find your API token.
### Limitations
You are limited to 500 credits per month. Each company info request costs 0.25 credits.
### Using a script
This script allows you to parse company data using The Companies API. It retrieves information such as company names, employees, revenues, locations, and social network profiles. The data is saved in a CSV file for further analysis. To use this script, run it in the command line with the following arguments:  
- `-at` or `--api-token`: An API token for making the request (required).  
- `-o` or `--output`: A file save directory (no spaces). Leave blank to save in the current working directory.  
- `-s` or `--size`: Maximum number of companies to search for (default: 10).  
- `-p` or `--page`: Search results page index (default: 1).  
- `-i` or `--industries`: A list of industries separated by spaces (e.g., information-technology computer-science).  
- `-io` or `--i-operator`: An operator for the list of industries (choices: "and", "or"; default: "or").  
- `-r` or `--revenues`: A list of revenue ranges separated by spaces (choices: "under-1m", "1m-10m", "10m-50m", "50m-100m", "100m-200m", "200m-1b", "over-1b").  
- `-e` or `--employees`: A list of employee amount ranges separated by spaces (choices: "1-10", "10-50", "50-200", "200-500", "500-1k", "1k-5k", "5k-10k", "over-10k").  
- `-ci` or `--cities`: A list of cities separated by spaces.  
- `-co` or `--countries`: A list of countries (or ISO3166 country codes) separated by spaces.  
### Example
To search for companies in the data science industry in the United States and the United Kingdom, use the following command:  
`python api.py -at YOUR_TOKEN -o /path/to/save/directory -i data-science -io or -co US GB`
