import csv
import json
import os
import country
import country_codes

_Start_year = 1950
_End_year = 2100


def left(s, amount):
    return s[:amount]

def right(s, amount):
    return s[-amount:]

def mid(s, offset, amount):
    return s[offset:offset+amount]

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
    return total,diff

def compare_region_to_countries(region_name):
    region = country.find_one(region_name,'m49Name')
    if region == None:
        print(f"Cannot find {region_name}")
        return

    summed_country_code = region['m49Code']

    with open('CountryRegions.json', 'r') as infile:
        hierar = json.load(infile)

    allParts = country.find_all(summed_country_code, 'm49Parent')

    selectParts = []
    for part in allParts:
        if 'oldCode' in part:  # only add countries that have an old code
            selectParts.append(part)

    if selectParts == []:
        print(f"No subparts to {region_name}")
        return

    parts = ""
    for part in selectParts:
        if parts == "":
            parts = part['m49Name']
        else:
            parts = parts + " + " + part['m49Name']
    print(f"Calculating {region['m49Name']} = {parts}")

    ov_total = 0
    ov_diff = 0
    for idx_yr, year in enumerate(range(_Start_year, _End_year, 5)):
        # read parent region data for year
        summed_data = country.read_data(region, year)
        summed_parts = []
        # read and add each sub
        for part in selectParts:
            part_data = country.read_data(part, year)
            summed_parts = year_add(summed_parts, part_data)
        th_total, th_diff = year_compare(summed_data, summed_parts)
        #       print(f"Comparing to {summed_directory['name']} {year} {100*th_diff/th_total}% = {th_diff}/{th_total}")
        ov_total = ov_total + th_total
        ov_diff = ov_diff + th_diff
    rel_dif = round(1000 * ov_diff / ov_total) / 100
    print(f"Comparing to {region_name} {ov_diff / ov_total}% = {ov_diff}/{ov_total}")


def create_summed_region(countries, sum_region):
    country_a = countries[0]
    country_b = countries[1]

    # Create directory if needed
    path = "data/" + sum_region['m49Name']
    if (os.path.isdir(path)):
        print(f"{path} directory is there")
    else:
        try:
            os.mkdir(path)
        except OSError:
            print("Creation of the directory %s failed" % path)
            exit(0)

    for idx_yr, year in enumerate(range(_Start_year, _End_year+1, 5)):
        ac = country.read_full_data(country_a,year)
        bc = country.read_full_data(country_b,year)
        sumc = []
        for idx_ln, line in enumerate(ac):
            if (idx_ln == 0):
                sumc.append(line)
            else:
                sumc.append([line[0], ac[idx_ln][1] + bc[idx_ln][1], ac[idx_ln][2] + bc[idx_ln][2]])

        # Write out csv
        country.write_full_data(sum_region,year,sumc)

def Create_Americas():
    sum_region = [
        country.find_one("Latin America and the Caribbean","m49Name"),
        country.find_one("Northern America","m49Name")
    ]
    create_summed_region(sum_region, country.find_one("Americas",'m49Name'))

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

# name	M49	parent	alpha-2	full
def fill_hier(elem):
    myDict = {}
    myDict['code'] = right("000" + str(elem['m49Code']),3)
    if 'usual' in elem:
        myDict['name'] = elem['usual']
    else:
        myDict['name'] = elem['m49Name']
    if 'alpha2' in elem:
        myDict['a2'] = elem['alpha2']
    if 'm49Parent' in elem:
        myDict['parent'] = right("000" + str(elem['m49Parent']),3)
    myDict['sub'] = []

    myCountries = country.find_all(elem['m49Code'],'m49Parent')
    for ct in myCountries:
        # found a child
        myDict['sub'].append(fill_hier(ct))
    return myDict

def output_hierarchy():
    name = "CountryRegions"
    root = country.find_one(1,'m49Code')
    if root == None:
        exit(0)
    hierar = fill_hier(root)
    print(hierar)
    print('Read data')
    with open(name + '.json', 'w') as outfile:
        json.dump(hierar, outfile)
    print('Output data')


def main():
#    for reg in country_codes.extended:
#        if not 'alpha2' in reg:
#            compare_region_to_countries(reg['m49Name'])

#    Create_Americas()

   output_hierarchy()


main()
