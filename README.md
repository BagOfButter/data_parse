# Collecting data about companies using The Companies API
### Receiving an API token
To receive an API token, go to The Companies API website (https://www.thecompaniesapi.com/). Log in or create your account. Then, navigate to the "API tokens & usage" page (https://www.thecompaniesapi.com/settings/api-tokens-and-usage/), where you can find your API token.
### Limitations
You are limited to 500 credits per month. Each company info request costs 0.25 credits.
### Using a script
To use data parsing script, simply launch `app.py`, it will create a localhost server (default `http://127.0.0.1:5000/`) then type in all the desired parameters and get your data.  
API token is required.  
All parameters that require input from a keyboard must be entered via comma.  
In checkboxes, you can choose either multiple parameters or None, which will select all of them. The same applies to input fields.  
Size determines how many data you request. If size equals 5, you will get information about 5 companies. (default is 5)  
Page is a search results page index (default is 1)  
To export data, you should check the checkbox `Submit export` and enter the directory where you want to save data. If you don't input path, the file will be saved in the current location.  
Press `apply` to apply all parameters.
