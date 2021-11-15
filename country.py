import csv
import country_codes


# Country is a dict
def read_data(country, year):
    pop = []
    # read data
    file_name = "data/" + country['m49Name'] + "/pop" + str(year) + ".csv"
    with open(file_name, newline='') as csvfile:
        datareader = csv.reader(csvfile, delimiter=',', quotechar='|')
        next(datareader)
        for row in datareader:
            pop.append([int(row[1]),int(row[2])])
    return pop

# Country is a dict
def read_full_data(country, year):
    pop = []
    # read data
    file_name = "data/" + country['m49Name'] + "/pop" + str(year) + ".csv"
    with open(file_name, newline='') as csvfile:
        datareader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in datareader:
            pop.append(row)
    return pop

# Country is a dict
def write_full_data(country, year, data):
    file_name = "data/" + country['m49Name'] + "/pop" + str(year) + ".csv"
    f = open(file_name, 'w')
    datawriter = csv.writer(f , dialect='excel')
    datawriter.writerows(data)
    f.close()

# Return the entire country dict
def find_one(data, type):
    for ct in country_codes.extended:
        if type in ct:
            if str(ct[type]) == str(data):
                return ct
    return None


# Return all countries matching
def find_all(data, type):
    found = []
    for ct in country_codes.extended:
        if type in ct:
            if str(ct[type]) == str(data):
                found.append(ct)
    return found

