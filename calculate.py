import csv
import country_codes
import json
import os


def read_data(country, year):
    pop = []
    # read data
    file_name = "data/" + country + "/pop" + str(year) + ".csv"
    with open(file_name, newline='') as csvfile:
        datareader = csv.reader(csvfile, delimiter=',', quotechar='|')
        next(datareader)
        for row in datareader:
            pop.append([int(row[1]),int(row[2])])
    return pop


def find_countryname(code):
    for i in country_codes.countries:
        if country_codes.countries[i] == code:
            return country_codes.countries[i]
    return None

def find_directory_by_type(hierar,to_find,type):
    if hierar[type] == to_find:
        return hierar
    else:
        if hierar['sub'] == []:
            return None
        for sub in hierar['sub']:
            what = find_directory_by_type(sub,to_find,type)
            if what != None:
                return what
        return None


def main():
    summed_country_name = "CENTRAL ASIA"
    summed_country_code = country_codes.countries[summed_country_name]
    print(f"Calculating {summed_country_name} code {find_countryname(summed_country_code)}")

    with open('CountryRegions.json','r') as infile:
        hierar = json.load(infile)
    summed_directory = find_directory_by_type(hierar,summed_country_name,'name')
    print(summed_directory)



main()
