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
_Columns = 28
_Column_width = (_Horizontal - (2* _Margin)) / (_Columns + 2)

_pink_hue = 320
_pink_saturation = 35/100
_blue_hue= 208
_blue_saturation = 57/100
_sex_scale = 0.08  # More than 8% delta means max saturation

_orange_color = "#FF6600"
_blue_color = "#3399FF"
_purple_color = "#663399"
_green_color = "#55D43F"
_SubFrames = 4
_FPS = 10


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

def mainloop(country, max_bar, max_population, pop_data):
    Speed = _SubFrames  # frame per sec

    year = _Start_year
    set_color(color_rgb(80, 80, 80, 255))
    ColorMode = "sex"
    scale = (_Vertical - 2 * _Margin) / 2 / max_bar
    sub = 0

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

        if delay_jfps(_FPS):
            clear_device()
            startx = _Margin
            starty = _Vertical / 2
            idx_yr = int((year - _Start_year) / 5)
            total_death = 0

            for group in range(0,_ActiveColumns):
                pop_m = pop_data[idx_yr]["live"][group][0]
                pop_f = pop_data[idx_yr]["live"][group][1]
                set_bar_color(pop_m, pop_f,0.7, ColorMode, _green_color)

                # Label groups
                draw_text(_Margin + 3 + group * _Column_width, starty + _Margin / 2, str(group * 5))

                # First column fill in from left to righ
                if group == 0:
                    width = int(_Column_width * sub / Speed)
                else:
                    width = _Column_width

                # First column fill in progressively

                death = int(pop_data[idx_yr]["death"][group] * sub / Speed)
                total_death += int(pop_data[idx_yr]["death"][group])

                # Draw live
                draw_rect(startx, starty - scale * (pop_m + pop_f - death), startx + width, starty)

                # Draw Death
                set_bar_color(1, 1, 0.4, ColorMode, _purple_color)
                last_death = pop_data[idx_yr]["previous_death"][group]
                draw_rect(startx, starty, startx + width, starty + scale * last_death)
                draw_rect(startx, starty + scale * last_death, startx + width, starty + scale * (last_death + death))

                # Every 4 columns, print birth year
                if (year - group * 5) % 20 == 0:
                    draw_text(startx + 3, _Vertical / 2 - _Margin / 2, (year - 5 * group))
                startx = startx + width

            group = _ActiveColumns
            while group < _Columns:
                # Label groups
                draw_text(_Margin + 3 + group * _Column_width, starty + _Margin / 2, str(group * 5))
                if group < len(pop_data[idx_yr]["previous_death"]):
                    last_death = pop_data[idx_yr]["previous_death"][group]
                    draw_rect(startx, starty, startx + _Column_width, starty + scale * last_death)
                startx = startx + _Column_width
                group = group + 1

            startx = _Horizontal - _Margin - _Column_width # Skip one column before death
            draw_text(startx, starty - _Margin / 2, "death")
            set_bar_color(1, 1, 0.4, ColorMode, _purple_color)
            draw_rect(startx, starty + scale * total_death, startx + _Column_width, starty)

            startx = _Margin
            starty = _Vertical / 2
            draw_text(_Margin, _Margin/2, country," : ",year, " population ",int(pop_data[idx_yr]["population"]/10000)/100, "M % of max : ", int(1000*pop_data[idx_yr]["population"]/max_population)/10)

            # Move onto next year
            sub += 1
            if sub > Speed - 1:
                year = year + 5
                sub = 0
                if year >= _End_year:
                    year = _Start_year
                    clear_device()
                    delay(500)  # 1/2 second blank
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

def c_u(nb):
    return int(nb/100000)

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
        previous_death = []
        death_bars = []
        previous_immig = []
        immig_bars = []

        live_bars = read_data(country, _Start_year)
        for idx_yr, year in enumerate(range(_Start_year, _End_year, 5)):
            # Read live data a column ahead
            next_bars = read_data(country, year+5)

            # Handle previous deaths
            if idx_yr > 0:
                for idx_bar in range(0,len(live_bars)):
                    previous_death[idx_bar] += death_bars[idx_bar]
                    previous_immig[idx_bar] += immig_bars[idx_bar]
                previous_death.insert(0, 0)
                previous_immig.insert(0, 0)
            else:
                # Initialize
                for bar in range(0, len(live_bars)):
                    previous_death.append(0)
                    previous_immig.append(0)

            population = 0
            death_bars = []
            immig_bars = []
            pre_deaths = []
            pre_immig = []
            for idx_bar, bar in enumerate(live_bars):
                population_bar = bar[0]+bar[1]  # add women and men
                if population_bar > max_bar:
                    max_bar = population_bar
                population = population + population_bar
                if idx_bar < len(live_bars)-1:       # Not last column
                    new_death = (bar[0] - next_bars[idx_bar + 1][0] if bar[0] > next_bars[idx_bar + 1][0] else 0) +\
                                (bar[1] - next_bars[idx_bar + 1][1] if bar[1] > next_bars[idx_bar + 1][1] else 0)
                    new_immig = (next_bars[idx_bar + 1][0] - bar[0] if bar[0] < next_bars[idx_bar + 1][0] else 0) +\
                                (next_bars[idx_bar + 1][1] - bar[1] if bar[1] < next_bars[idx_bar + 1][1] else 0)
                else:
                    new_death = bar[0] + bar[1]     # All die
                    new_immig = 0
                death_bars.append(new_death)
                immig_bars.append(new_immig)
                pre_deaths.append(previous_death[idx_bar])
                pre_immig.append(previous_immig[idx_bar])

            idx_bar = len(live_bars)
            while idx_bar < len(previous_death):
                pre_deaths.append(previous_death[idx_bar])
                idx_bar += 1

            if population > max_population:
                max_population = population

            pop_data.append({"year":year, "population":population, "live":live_bars, "death":death_bars, "immigration":immig_bars, "previous_death":pre_deaths, "previous_immig":pre_immig})
            live_bars = next_bars

        mainloop(country, max_bar, max_population, pop_data)
    close_graph()
easy_run(main)