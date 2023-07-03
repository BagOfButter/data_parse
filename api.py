from country_codes import ISO3166
from argparse import ArgumentParser
from re import sub
import csv
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


def parse_companies(api_token, industries, i_operator, revenues, employees, cities, countries, size, page, csv_path):
    url = "https://api.thecompaniesapi.com/v1/companies"
    aliases = {
        "industries": list(map(kebab, industries or [])),
        "revenue": revenues or [],
        "totalEmployees": employees or [],
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

    if response.status_code != 200:
        exit(f"Error in retrieving data ({response.status_code}): {response.reason}")

    data = response.json()
    meta = data["meta"]
    companies = data["companies"]

    if companies == []:
        exit("No companies found")
    elif meta["total"] != len(companies):
        print(f"Found {meta['total']} companies. {size} companies from page {page} will be saved. To access other results, rerun the program with a different page index")
    else:
        print(f"Found {meta['total']} companies")
        
    field_names = ["Company Name", "Employees", "Revenue", "City", "Country", "Working Sphere", "Website", "Phone Number",
                   "Facebook", "Instagram", "LinkedIn", "Pinterest", "Twitter", "YouTube"]
    
    with open(csv_path, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=field_names)

        if file.tell() == 0:
            writer.writeheader()

        for company in companies:
            name = company.get("name") or "N/A"
            employees = company.get("totalEmployees") or "N/A"
            revenues = company.get("revenue") or "N/A"
            city = (company.get("city") or {}).get("name") or "N/A"
            country = (company.get("country") or {}).get("name") or "N/A"
            working_sphere = company.get("industryMain") or "N/A"
            phone_number = company.get("phoneNumber") or "N/A"
            website = "N/A"
            if company.get("domainName") and company.get("domainTld"):
                website = company.get("domainName") + "." + company.get("domainTld")

            social_networks = company.get("socialNetworks") or {}
            facebook = social_networks.get("facebook") or "N/A"
            instagram = social_networks.get("instagram") or "N/A"
            linkedin = social_networks.get("linkedin") or "N/A"
            pinterest = social_networks.get("pinterest") or "N/A"
            twitter = social_networks.get("twitter") or "N/A"
            youtube = social_networks.get("youtube") or "N/A"

            writer.writerow(
                {
                    "Company Name": name,
                    "Employees": employees,
                    "Revenue": revenues,
                    "City": city,
                    "Country": country,
                    "Working Sphere": working_sphere,
                    "Phone Number": phone_number,
                    "Website": website,
                    "Facebook": facebook,
                    "Instagram": instagram,
                    "LinkedIn": linkedin,
                    "Pinterest": pinterest,
                    "Twitter": twitter,
                    "YouTube": youtube,
                }
            )

    print("Data exported to", csv_path)


if __name__ == "__main__":
    parser = ArgumentParser(
        description="A script for parsing companies. All search parameters should be written in kebab-case (something-like-this)."
    )
    
    parser.add_argument("-at", "--api-token", help="An API token for making a request.", required=True)
    parser.add_argument("-o", "--output", help="A file save directory (no spaces). Leave blank to save in the current working directory")
    parser.add_argument("-s", "--size", help="Max amount of companies to search for", type=int, default=10)
    parser.add_argument("-p", "--page", help="Search results page index", type=int, default=1)
    parser.add_argument("-i", "--industries", help="A list of industries separated by spaces (e.g., information-technology computer-science)",
                        nargs="+")
    parser.add_argument("-io", "--i-operator", help="An operator for the list of industries",
                        choices=["and", "or"], default="or")
    parser.add_argument("-r", "--revenues", help="A list of revenue ranges separated by spaces",
                        choices=["under-1m", "1m-10m", "10m-50m", "50m-100m", "100m-200m", "200m-1b", "over-1b"],
                        nargs="+")
    parser.add_argument("-e", "--employees", help="A list of employee amount ranges separated by spaces",
                        choices=["1-10", "10-50", "50-200", "200-500", "500-1k", "1k-5k", "5k-10k", "over-10k"],
                        nargs="+")
    parser.add_argument("-ci", "--cities", help="A list of cities separated by spaces",
                        nargs="+")
    parser.add_argument("-co", "--countries", help="A list of countries (or ISO3166 country codes) separated by spaces",
                        nargs="+")

    args = parser.parse_args()

    is_cli = args.industries or args.revenues or args.employees or args.cities or args.countries
    if args.output and not os.path.exists(args.output):
        exit("Invalid path:", args.output)

    parse_companies(
        api_token=args.api_token, industries=args.industries, i_operator=args.i_operator,
        revenues=args.revenues, employees=args.employees, cities=args.cities,
        countries=args.countries, size=args.size, page=args.page, 
        csv_path=os.path.join(args.output or os.getcwd(), "company_data.csv")
    )
