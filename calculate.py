import csv
import country_codes
import json
import os


_Start_year = 1950
_End_year = 2100

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
            return i
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

def year_add(into,what):
    if into == []:
        return what
    else:
        for idx, group in enumerate(what):
            into[idx][0] = into[idx][0] + what[idx][0]
            into[idx][1] = into[idx][1] + what[idx][1]
        return into

def year_compare(a, b):
    diff = 0
    total = 0
    for idx, group in enumerate(a):
        total = total + a[idx][0] + a[idx][1]
        delta = abs(a[idx][0] - b[idx][0]) + abs(a[idx][1] - b[idx][1])
        diff = diff + delta
        if delta > 0:
            print(f"delta @{idx * 5 + _Start_year}:{delta}")
    return total,diff

def main():
    summed_country_name = "EASTERN ASIA"
    summed_country_code = country_codes.countries[summed_country_name]
    print(f"Calculating {summed_country_name} code {find_countryname(summed_country_code)}")

    with open('CountryRegions.json','r') as infile:
        hierar = json.load(infile)
    summed_directory = find_directory_by_type(hierar,summed_country_name,'name')

    ov_total = 0
    ov_diff = 0
    for idx_yr, year in enumerate(range(_Start_year, _End_year, 5)):
        summed_data = read_data(summed_country_name, year)
        summed_parts = []
        for part in summed_directory['sub']:
            part_data = read_data(find_countryname(part['code']),year)
            summed_parts = year_add(summed_parts,part_data)
        th_total,th_diff = year_compare(summed_data, summed_parts)
 #       print(f"Comparing to {summed_directory['name']} {year} {100*th_diff/th_total}% = {th_diff}/{th_total}")
        print(f"Comparing to {summed_directory['name']} {year} {th_diff}/{th_total}")
        ov_total = ov_total + th_total
        ov_diff = ov_diff + th_diff
    print(f"Comparing to {summed_directory['name']} {100 * ov_diff / ov_total}% = {ov_diff}/{ov_total}")


main()
