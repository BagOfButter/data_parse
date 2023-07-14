from flask import Flask, render_template, url_for, request, redirect
import pandas as pd
import numpy as np

from country_codes import ISO3166
from re import sub
import os
import json
import requests


def kebab(s):
    return '-'.join(
        sub(r"(\s|_|-)+"," ",
        sub(r"[A-Z]{2,}(?=[A-Z][a-z]+[0-9]*|\b)|[A-Z]?[a-z]+[0-9]*|[A-Z]|[0-9]+",
        lambda mo: ' ' + mo.group(0).lower(), s)).split()
    )


def country_to_code(country):
    country = kebab(country)
    if country in ISO3166.values():
        return country
    elif country in ISO3166:
        return ISO3166[country]
    else:
        exit(f"Unknown country: {country}. The possible options are provided in country_codes.py")


def parse_companies(api_token, industries, i_operator, revenues, employees, cities, countries, size, page, export_params):
    url = "https://api.thecompaniesapi.com/v1/companies"
    aliases = {
        "industries": list(map(kebab, industries or [])),
        "revenue": revenues,
        "totalEmployees": employees,
        "country.code": list(map(country_to_code, countries or [])),
        "city.code": list(map(kebab, cities or [])),
    }

    query = []
    for attribute, values in aliases.items():
        if not values:
            continue

        search_condition = {
            "attribute": attribute,
            "operator": "or",
            "sign": "equals",
            "values": values
        }

        if attribute == "industries":
            search_condition["operator"] = i_operator

        query.append(search_condition)
        
    params = {"query": json.dumps(query), "size": size, "page": page}
    headers = {"Authorization": f"Basic {api_token}"}
    response = requests.get(url, headers=headers, params=params)
    
    error = ''
    if response.status_code != 200:
        error = f"Error in retrieving data ({response.status_code}): {response.reason}"
        return '', error
        
    data = response.json()
    meta = data["meta"]
    companies = data["companies"]

    if companies == []:
        error = "No companies found"
        return '', error
    
        
    field_names = ["Company Name", "Employees", "Revenue", "City", "Country", "Working Sphere", "Website", "Phone Number",
                   "Facebook", "Instagram", "LinkedIn", "Pinterest", "Twitter", "YouTube"]
    
    dataset = []
    
    for company in companies:
        name = company.get("name") or "N/A"
        employees = company.get("totalEmployees") or "N/A"
        revenues = company.get("revenue") or "N/A"
        city = (company.get("city") or {}).get("name") or "N/A"
        country = (company.get("country") or {}).get("name") or "N/A"
        working_sphere = company.get("industryMain") or "N/A"
        website = "N/A"
        if company.get("domainName") and company.get("domainTld"):
            website = company.get("domainName") + "." + company.get("domainTld")
        phone_number = company.get("phoneNumber") or "N/A"
        social_networks = company.get("socialNetworks") or {}
        facebook = social_networks.get("facebook") or "N/A"
        instagram = social_networks.get("instagram") or "N/A"
        linkedin = social_networks.get("linkedin") or "N/A"
        pinterest = social_networks.get("pinterest") or "N/A"
        twitter = social_networks.get("twitter") or "N/A"
        youtube = social_networks.get("youtube") or "N/A"
        
        dataset.append([name, employees, revenues, city, country, working_sphere, website, phone_number, facebook, instagram, linkedin, pinterest, twitter, youtube])
    
    df = pd.DataFrame(dataset, columns=field_names)
    
    if export_params['submitted']:
        df.to_csv(export_params['path'], index=False)
    return df, error

revenues_possible_values = ['under-1m', '1m-10m', '10m-50m', '50m-100m', '100m-200m', '200m-1b', 'over-1b']
employees_possible_values = ['1-10', '10-50', '50-200', '200-500', '500-1k', '1k-5k', '5k-10k', 'over-10k']
r_chosen_values = []
e_chosen_values = []
    
app = Flask(__name__)

@app.route('/', methods=['GET'])
def dropdowns():
    return render_template('index.html', api_token = '', countries = '', output_size = 5, page = 1,
                           revenues_possible_values = revenues_possible_values, r_chosen_values = r_chosen_values,
                           employees_possible_values = employees_possible_values, e_chosen_values = e_chosen_values,
                           i_operator = 'or', 
                           tables=[], titles=[])

@app.route('/', methods=['GET','POST'])
def update():
    data = dict(
        api_token = request.form.get('api_token'),
        countries_names = request.form.get('countries').replace(' ', '').split(',') if request.form.get('countries') != '' else [],
        industries = request.form.get('industries').replace(' ', '').split(',') if request.form.get('industries') != '' else [],
        cities = request.form.get('cities').replace(' ', '').split(',') if request.form.get('cities') != '' else [],
        revenues = request.form.getlist('revenue'),
        employees = request.form.getlist('employees'),
        size = int(request.form.get('output_size')),
        page = int(request.form.get('page')),
        i_operator = request.form.get('i_operator'),
        csv = {
            'submitted': request.form.get('csv_checkbox'),
            'path': os.path.join(request.form.get('csv_path') or os.getcwd(), "company_data.csv")
        }
    )
    
    r_chosen_values = data['revenues']
    e_chosen_values = data['employees']
    
    df, error = parse_companies(
        api_token= data['api_token'], size=data['size'], page=data['page'], 
        countries=data["countries_names"], cities=data['cities'],
        industries=data['industries'], i_operator=data['i_operator'],
        revenues=data['revenues'], employees=data['employees'], 
        export_params = data['csv']
    )
    
    return render_template('index.html', api_token= data['api_token'], output_size = data['size'], page = data['page'],
                           countries = data['countries_names'], cities = data["cities"],
                           industries = data["industries"], i_operator = data['i_operator'],
                           revenues_possible_values = revenues_possible_values, r_chosen_values = r_chosen_values,
                           employees_possible_values = employees_possible_values, e_chosen_values = e_chosen_values,
                           tables=[df.to_html(classes='data')] if type(df) != str else '', error = error)
    

if __name__ == "__main__":
    app.run()