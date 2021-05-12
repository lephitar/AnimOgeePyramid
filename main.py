from easygraphics import *
import csv
import colorsys

_Country = "usa"
# get data curl "https://www.populationpyramid.net/api/pp/392/[1950-2100]/?csv=true" -o pop#1.csv
_Start_year = 1950
_End_year = 2100

_Vertical = 600
_Horizontal = 1200
_Margin = 50
_Columns = 21
_Column_width = (_Horizontal - (2* _Margin)) / (_Columns + 2)
_Speed = 5

_pink_hue = 320/360
_pink_saturation = 35/100
_blue_hue= 208/360
_blue_saturation = 57/100
_sex_scale = 0.1  # More than 20% delta means max saturation


def set_bar_color(m, f, dark):
    if m+f == 0:
        set_fill_color(color_rgb(255, 0, 0))
        return
    relative = m / (m + f) - 0.5
    if relative > _sex_scale:
        relative = _sex_scale
    if relative < -_sex_scale:
        relative = -_sex_scale

    if relative > 0:
        (red, green, blue) = colorsys.hsv_to_rgb(_blue_hue, _blue_saturation*relative/_sex_scale, dark)
    else:
        (red, green, blue) = colorsys.hsv_to_rgb(_pink_hue, -_pink_saturation*relative/_sex_scale, dark)

    cr, cg, cb = int(255 * red), int(255 * green), int(255 * blue)
    set_fill_color(color_rgb(cr, cg, cb))

def mainloop(scale):

    year = _Start_year
    set_color(color_rgb(80, 80, 80))
    last_pop_m = []
    last_pop_f = []
    first_year = True
    # Initialize last population
    for i in range (0,_Columns):
        last_pop_m.append(0)
        last_pop_f.append(0)
    while is_run():
        pop_m = []
        pop_f = []
        # read data
        file_name = "data/"+_Country+"/pop"+str(year)+".csv"
        with open(file_name, newline='') as csvfile:
            datareader = csv.reader(csvfile, delimiter=',', quotechar='|')
            next(datareader)
            for row in datareader:
                pop_m.append(int(row[1]))
                pop_f.append(int(row[2]))

        if delay_jfps(_Speed):
            clear_device()
            startx = _Margin
            starty = _Vertical - _Margin
            draw_text(_Margin, _Margin/2, _Country," : ",year)
            death_m = 0
            death_f = 0
            for group in range(0,_Columns):
                draw_text(startx, starty + _Margin / 2, str(group*5))
                set_bar_color(pop_m[group],pop_f[group],0.7)
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
                        set_bar_color(delta_m, delta_f, 0.4)
                        draw_rect(startx, starty - scale * (pop_m[group] + pop_f[group] - delta_m - delta_f) , startx + _Column_width, starty - scale * (pop_m[group]+pop_f[group]))
                    # IMMIGRATION
                    else:
                        draw_rect(startx, starty - scale * (pop_m[group] + pop_f[group] - delta_m - delta_f), startx + _Column_width, starty)
                        set_bar_color(-delta_m, -delta_f, 0.8)
                        draw_rect(startx, starty - scale * (pop_m[group]+pop_f[group]), startx + _Column_width, starty - scale * (pop_m[group] + pop_f[group] - delta_m - delta_f))

                startx = startx + _Column_width
            startx = startx + _Column_width
            draw_text(startx, starty + _Margin / 2, "death")
            set_bar_color(death_m, death_f, 0.4)
            draw_rect(startx, starty + scale * (death_m + death_f), startx + _Column_width, starty)

        if first_year:
            first_year = False
        for i in range(0, _Columns):
            last_pop_m[i] = pop_m[i]
            last_pop_f[i] = pop_f[i]

        # Move onto next year
        year = year + 5
        if year > _End_year:
            year = _Start_year
            first_year = True
            clear_device()
            delay(_Speed*100)


def find_max():
    year = _Start_year
    max = 0

    while year <= _End_year:
        # read data
        file_name = "data/"+_Country+"/pop"+str(year)+".csv"
        with open(file_name, newline='') as csvfile:
            datareader = csv.reader(csvfile, delimiter=',', quotechar='|')
            next(datareader)
            for row in datareader:
                agegroup = int(row[1])+int(row[2])
                if agegroup > max:
                    max = agegroup

        # Move onto next year
        year = year + 5
    return max

def main():
    init_graph(_Horizontal, _Vertical)
    set_render_mode(RenderMode.RENDER_MANUAL)
    mainloop((_Vertical - 2 * _Margin) / find_max())
    close_graph()

easy_run(main)