from easygraphics import *
from easygraphics.dialog import *
import csv
import os
import requests
import country_codes
from PyQt5.QtGui import QFont

# Country codes are ISO 3166-1
# All referred to in slim-country.csv


# get data curl "https://www.populationpyramid.net/api/pp/392/[1950-2100:5]/?csv=true" -o pop#1.csv
_Start_year = 1950
_End_year = 2100

_Vertical = 800
_Horizontal = 1400
_Margin = 50
_ActiveColumns = 21
_Columns = 21
_Column_width = (_Horizontal - (2* _Margin)) / (_Columns + 2)

_pink_hue = 320
_pink_saturation = 35/100
_blue_hue= 208
_blue_saturation = 57/100
_sex_scale = 0.08  # More than 10% delta means max saturation

_orange_color = "#FF6600"
_blue_color = "#3399FF"
_purple_color = "#663399"
_green_color = "#55D43F"
_SubFrames = 5


def set_bar_color(m, f, dark, mode, color):
    if mode == "sex":
        if m+f == 0:
            set_fill_color(color_rgb(255, 0, 0))
            return
        relative = m / (m + f) - 0.5
        if relative > _sex_scale:
            relative = _sex_scale
        if relative < -_sex_scale:
            relative = -_sex_scale

        if relative > 0:
            set_fill_color(color_hsv(_blue_hue, int(255*_blue_saturation*relative/_sex_scale), int(255*dark)))
        else:
            set_fill_color(color_hsv(_pink_hue, int(255*-_pink_saturation*relative/_sex_scale), int(255*dark)))

    else:
        if len(color) != 7:
            set_fill_color(color_rgb(255, 0, 0))
        else:
            set_fill_color(color)

def mainloop(country, scale, max, pop_data):
    Speed = 5  # frame per sec

    year = _Start_year
    set_color(color_rgb(80, 80, 80, 255))
    last_pop_m = []
    last_pop_f = []
    first_year = True
    initial_pop = []
    ColorMode = "sex"
    # Initialize last population
    for i in range (0,_ActiveColumns):
        last_pop_m.append(0)
        last_pop_f.append(0)
        initial_pop.append(0)
    while is_run():
        if has_kb_hit():
            mykey = get_char()
            if mykey == "y":
                pause()
            if mykey == "<":
                if Speed > 2:
                    Speed = Speed - 1
            if mykey == ">":
                Speed = Speed + 1
            if mykey == "s":
                ColorMode = "sex"
            if mykey == "c":
                ColorMode = "color"

        if has_mouse_msg():
            while has_mouse_msg():
                get_mouse_msg()
            return
        pop_m = []
        pop_f = []
        # read data
        file_name = "data/"+country+"/pop"+str(year)+".csv"
        with open(file_name, newline='') as csvfile:
            datareader = csv.reader(csvfile, delimiter=',', quotechar='|')
            next(datareader)
            for row in datareader:
                pop_m.append(int(row[1]))
                pop_f.append(int(row[2]))

        if delay_jfps(Speed):
            clear_device()
            startx = _Margin
            starty = _Vertical / 2
            death_m = 0
            death_f = 0
            total_pop_m = 0
            total_pop_f = 0
            for group in range(0,_ActiveColumns):
                if group == 0:
                    initial_pop[0] = pop_m[0] + pop_f[0]
                draw_text(startx + 3, starty + _Margin / 2, str(group*5))
                set_bar_color(pop_m[group],pop_f[group],0.7, ColorMode, _green_color)
                total_pop_f = total_pop_f + pop_f[group]
                total_pop_m = total_pop_m + pop_m[group]
                if first_year or group == 0:
                    # Clean case
                    draw_rect(startx,starty-scale*(pop_m[group]+pop_f[group]), startx+_Column_width, starty)
                else:
                    delta_m = pop_m[group] - last_pop_m[group - 1]
                    delta_f = pop_f[group] - last_pop_f[group - 1]
                    death_m = death_m + delta_m
                    death_f = death_f + delta_f
                    # DEATH
                    if delta_m+delta_f < 0:
                        draw_rect(startx, starty - scale * (pop_m[group]+pop_f[group]), startx + _Column_width, starty)
                        set_bar_color(delta_m, delta_f, 0.4, ColorMode, _purple_color)
                        draw_rect(startx, starty - scale * (pop_m[group] + pop_f[group] - delta_m - delta_f) , startx + _Column_width, starty - scale * (pop_m[group]+pop_f[group]))
                    # IMMIGRATION
                    else:
                        draw_rect(startx, starty - scale * (pop_m[group] + pop_f[group] - delta_m - delta_f), startx + _Column_width, starty)
                        set_bar_color(-delta_m, -delta_f, 0.8, ColorMode, _blue_color)
                        draw_rect(startx, starty - scale * (pop_m[group]+pop_f[group]), startx + _Column_width, starty - scale * (pop_m[group] + pop_f[group] - delta_m - delta_f))

                if initial_pop[group] > 0:
                    set_color(color_rgb(80, 80, 80, 100))
                    move_to(startx, starty - scale * initial_pop[group]-1)
                    line_to(startx + _Column_width, starty - scale * initial_pop[group])
                    set_color(color_rgb(80, 80, 80, 255))

                if (year - group * 5) % 20 == 0:
                    draw_text(startx + 3, _Vertical / 2 - _Margin / 2, (year - 5 * group))
                startx = startx + _Column_width

            startx = startx + _Column_width # Skip one column before death
            draw_text(startx, starty + _Margin / 2, "death")
            set_bar_color(death_m, death_f, 0.4, ColorMode, _purple_color)
            draw_rect(startx, starty + scale * (death_m + death_f), startx + _Column_width, starty)

            startx = _Margin
            starty = _Vertical / 2
            draw_text(_Margin, _Margin/2, country," : ",year, " population ",int((total_pop_m+total_pop_f)/10000)/100, "M % of max : ", int(1000*(total_pop_m+total_pop_f)/max)/10)

        if first_year:
            first_year = False
        for i in range(0, _ActiveColumns):
            last_pop_m[i] = pop_m[i]
            last_pop_f[i] = pop_f[i]
        for i in range(_ActiveColumns-1, 0, -1):
            initial_pop[i] = initial_pop[i-1]

        # Move onto next year
        year = year + 5
        if year > _End_year:
            year = _Start_year
            first_year = True
            clear_device()
            delay(500) # 1/2 second blank
            last_pop_m = []
            last_pop_f = []
            initial_pop = []
            # Initialize last population
            for i in range (0,_ActiveColumns):
                last_pop_m.append(0)
                last_pop_f.append(0)
                initial_pop.append(0)

    print ("EXIT")

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

def cache_country(country):
    pth = "data/" + country
    try:
        os.mkdir(pth)
    except OSError:
        print("Creation of the directory %s failed" % pth)
        exit(0)
    set_color(color_rgb(80, 80, 80, 255))
    clear_device()
    for year in range(1950, 2101, 5):
        while True:
            if delay_jfps(1000):
                clear_device()
                draw_text(_Margin, _Margin / 2, reply, " loading cache : ", str(year))
                set_bar_color(1, 1, 0.4, "color", "#A0A0A0")
                draw_rect(_Margin, _Margin, _Margin + 4 * (2100 - 1950), _Margin + 20)
                set_bar_color(2 + (2100 - year) / 150, 2 + (year - 1950) / 150, 0.8, "color", "#3399ff")
                draw_rect(_Margin, _Margin, _Margin + 4 * (year - 1950), _Margin + 20)
                url = 'https://www.populationpyramid.net/api/pp/' + str(country_codes.countries[country]) + '/' + str(
                    year) + '/?csv=true'  # [1950-2100:5]
                r = requests.get(url)
                file = open("data/" + country + "/pop" + str(year) + ".csv", "w")
                file.write(r.text)
                file.close()
                break   # get out of while True

def main():
    # file_name = "slim-country.csv"
    # with open(file_name, newline='') as csvfile:
    #     datareader = csv.reader(csvfile, delimiter=',', quotechar='|')
    #     next(datareader)    # skip first line
    #     for row in datareader:
    #         countries[row[0]]=row[2]
    #
    # for key in countries:
    #     # https://www.populationpyramid.net/api/pp/392/[1950-2100:5]/?csv=true
    #     r = requests.get('https://www.populationpyramid.net/api/pp/' + str(countries[key]) + '/1950/?csv=true')
    #     if r.status_code == 200:
    #         print(f'"{key}":"{countries[key]}",')

    pth = "data"
    if os.path.isdir(pth):
        cached = os.listdir(pth)
    else:
        try:
            os.mkdir(pth)
            cached = []
        except OSError:
            print("Creation of the directory %s failed" % pth)
            exit(0)

    init_graph(_Horizontal, _Vertical)
    set_render_mode(RenderMode.RENDER_MANUAL)
    set_font(QFont("Courier"))
    set_font_size(14)
    while True:
        # Select country
        country = get_choice("What country", choices=country_codes.countries.keys())
        if country == None:
            break
        # Cache country data if not there
        if country not in cached:
            if cache_country(country):
                cached.append(country)

        # Precalculate data
        pop_data = []
        max_bar = 0
        max_population = 0
        last_death = []
        last_immig = []
        for idx_yr, year in enumerate(range(_Start_year, _End_year+1, 5)):
            live_bars = read_data(country, year)
            population = 0
            death_bars = []
            immig_bars = []
            for idx_bar, bar in enumerate(live_bars):
                population_bar = bar[0]+bar[1]  # add women and men
                if population_bar > max_bar:
                    max_bar = population_bar
                population = population + population_bar
                if idx_bar > 0 and idx_yr > 0:       # Not in first year or column
                    pop_last = pop_data[idx_yr - 1]["live"]
                    new_death = (pop_last[idx_bar - 1][0] - bar[0] if bar[0] < pop_last[idx_bar - 1][0] else 0) +\
                                (pop_last[idx_bar - 1][1] - bar[1] if bar[1] < pop_last[idx_bar - 1][1] else 0)
                    new_immig = (bar[0] - pop_last[idx_bar - 1][0] if bar[0] > pop_last[idx_bar - 1][0] else 0) +\
                                (bar[1] - pop_last[idx_bar - 1][1] if bar[1] > pop_last[idx_bar - 1][1] else 0)
                else:
                    new_death = 0
                    new_immig = 0
                death_bars.append(new_death)
                immig_bars.append(new_immig)
            if population > max_population:
                max_population = population


            pop_data.append({"year":year, "population":population, "live":live_bars, "death":death_bars, "immigration":immig_bars})

        print(f"Pop {max_population} and bar {max_bar}")
        mainloop(country, (_Vertical / 2 - 2 * _Margin) / max_bar, max_population, pop_data)
    close_graph()
easy_run(main)