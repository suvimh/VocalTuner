# VocalTuner Application
# This application analyses the timbre and pitch characteristics of an input sound.
# The purpose of the VocalTuner is to assist vocalists when practicing control over their vocal pitch and timbre

# Developed by Suvi Häärä
# 2021-2022
import VTsettings


# class to store coordinates for drawing lines on timbre hexagon
class Coordinates:
    vib_x = 0
    vib_y = 0
    col_x = 0
    col_y = 0
    vol_x = 0
    vol_y = 0


# class to store timbre characteristics
class Timbre:
    volume = VTsettings.DEF_TIMBRE
    colour = VTsettings.DEF_TIMBRE


# class to store peak start and end information
class Peak:
    low_freq = 0
    high_freq = 0
