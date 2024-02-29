# VocalTuner Application
# This application analyses the timbre and pitch characteristics of an input sound.
# The purpose of the VocalTuner is to assist vocalists when practicing control over their vocal pitch and timbre
# Developed by Suvi Häärä
# 2021-2022

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import *
import numpy as np
import math
import VTsettings
import VTaudio
import VTclass


class VocalTuner(QMainWindow):
    def __init__(self):
        super(VocalTuner, self).__init__()
        self.nearest_note_number_buffered = 69
        self.a4_freq = 440

        # set location and size of the application window
        self.setGeometry(950, 350, 1080, 640)
        # title of application
        self.setWindowTitle("VocalTuner")
        # set background colour to cream white
        self.setStyleSheet("background: #FFFFFF;")
        # polygon with n points, radius, angle of the first point
        self.hexagon = self.create_hex(200, 90)

        # application static text setup
        self.app_text()
        self.timbre_text()
        self.pitch_static()

        self.note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

        self.note = self.create_label(' ', VTsettings.DEF_TEXT, 30, 30, 597, 306, 'Avenir', 20, QtCore.Qt.AlignRight)
        self.h_note = self.create_label(' ', VTsettings.DEF_TEXT, 30, 30, 600, 105, 'Avenir', 20, QtCore.Qt.AlignRight)
        self.l_note = self.create_label(' ', VTsettings.DEF_TEXT, 30, 30, 600, 505, 'Avenir', 20, QtCore.Qt.AlignRight)

        self.freq = 0
        self.nearest_note_num = 0
        self.freq_cents = 0
        self.peak_bw = 0

        self.pitch_bar_height = 0
        self.pitch_colour = 'unknown'

        # create QTimer
        self.qTimer = QTimer()
        # set interval to 0.02 seconds, 2ms = 0.02s
        self.qTimer.setInterval(2)
        # connect timeout signal to signal handler
        self.qTimer.timeout.connect(self.update_values)
        # start timer
        self.qTimer.start()

    # run every time timer is triggered, so that all display values update according to input
    def update_values(self):
        # start_time = time.time()
        note = self.note_set()
        file = VTaudio.audio_in()
        # print(note) # for testing
        if note == VTsettings.DISPLAY_NONE:
            h_note = VTsettings.DISPLAY_NONE
            l_note = VTsettings.DISPLAY_NONE
        else:
            h_note = self.num_to_note(self.nearest_note_num + 1)
            l_note = self.num_to_note(self.nearest_note_num - 1)

        # set size of the displayed bar based on cent difference
        if self.freq == VTsettings.NO_INPUT:
            self.pitch_bar_height = 0
        else:
            self.pitch_bar_height = round(self.freq_cents * 4)

        self.note.setText(note)
        self.h_note.setText(h_note)
        self.l_note.setText(l_note)
        self.note_colour()

        self.assign_timbre(file)
        self.timbre_coordinates()
        # end_time = time.time()
        # total_time_min = (end_time - start_time)
        # print("time taken to calculate everything:" + str(total_time_min) + " seconds")
        print(str(self.freq) + " : " + note)
        self.update()

    # calls the knn to get predicted value of labels and assigns timbre label accordingly
    def assign_timbre(self, file):
        col, vol = VTaudio.get_timbre_knn(file)
        # volume: 1 = full, 0 = hollow ; colour: 1 = bright, 0 = dark
        if vol == 0:
            VTclass.Timbre.volume = 'hollow'
        elif vol == 1:
            VTclass.Timbre.volume = 'full'

        if col == 0:
            VTclass.Timbre.colour = 'dark'
        elif col == 1:
            VTclass.Timbre.colour = 'bright'

        if self.freq == VTsettings.NO_INPUT:
            VTclass.Timbre.colour = VTsettings.DEF_TIMBRE
            VTclass.Timbre.volume = VTsettings.DEF_TIMBRE

    # sets the coordinates for drawing timbre lines based on timbre lables
    def timbre_coordinates(self):
        stable_limit = 40
        vibrato_limit = 70
        # check the value of the base width and set coordinate for vibrato/stable based on that
        self.peak_bw = VTclass.Peak.high_freq - VTclass.Peak.low_freq
        if self.peak_bw < stable_limit:  # very stable note - coordinate is at the tip of the hexagon, near stable
            VTclass.Coordinates.vib_x = 443
            VTclass.Coordinates.vib_y = 420
        elif self.peak_bw > vibrato_limit:  # note has lots of vibrato: coordinate at hexagon tip, near vibrato
            VTclass.Coordinates.vib_x = 97
            VTclass.Coordinates.vib_y = 220
        else:  # is between the two states
            # coordinate value is lowest coordinate value
            VTclass.Coordinates.vib_x = round(443-((self.peak_bw - stable_limit)/(vibrato_limit-stable_limit)) * 346)
            VTclass.Coordinates.vib_y = round(420-((self.peak_bw - stable_limit)/(vibrato_limit-stable_limit)) * 200)

        # check timbre labels and set coordinates accordingly
        if VTclass.Timbre.colour == 'bright':
            VTclass.Coordinates.col_x = 270
            VTclass.Coordinates.col_y = 520
        elif VTclass.Timbre.colour == 'dark':
            VTclass.Coordinates.col_x = 270
            VTclass.Coordinates.col_y = 120

        if VTclass.Timbre.volume == 'full':
            VTclass.Coordinates.vol_x = 97
            VTclass.Coordinates.vol_y = 420
        elif VTclass.Timbre.volume == 'hollow':
            VTclass.Coordinates.vol_x = 443
            VTclass.Coordinates.vol_y = 220

    # sets displayed colours based on note cent difference
    def note_colour(self):
        # determine colour of pitch bar and circle based of cent difference
        # if are 0-25 cents, colour is green
        if self.freq == VTsettings.NO_INPUT:  # no pitch over amplitude threshold limit detected - display blue
            self.pitch_colour = '#C6EDF9'
        elif 0 <= self.freq_cents < 12.5 or 0 >= self.freq_cents > -12.5:
            self.pitch_colour = '#43A105'
        # if are 25-50 cents, colour is yellow
        elif -12.5 <= self.freq_cents < 25 or -12.5 >= self.freq_cents > -25:
            self.pitch_colour = '#FFE529'
        # if are 50-75 cents, colour is orange
        elif 25 <= self.freq_cents < 37.5 or -25 >= self.freq_cents > -37.5:
            self.pitch_colour = '#FF9933'
        # if are 75-100 cents, colour is red
        elif 37.5 <= self.freq_cents < 50 or -37.5 >= self.freq_cents > -50:
            self.pitch_colour = '#C61203'

    # find note name, number and cent difference from target from frequency
    def note_set(self):
        self.freq = VTaudio.find_freq()
        # print(str(self.freq))
        if self.freq != VTsettings.NO_INPUT:
            # getting name, number and cents from input frequency
            num = self.freq_to_num()
            self.nearest_note_num = round(num)
            nearest_note_name = self.num_to_note(self.nearest_note_num)
            nearest_note_freq = self.num_to_freq(self.nearest_note_num, self.a4_freq)
            freq_diff = nearest_note_freq - self.freq
            semitone_step = nearest_note_freq - self.num_to_freq(round(num - 1), self.a4_freq)

            self.freq_cents = (freq_diff / semitone_step) * 100

            note = nearest_note_name

        else:
            note = VTsettings.DISPLAY_NONE

        # print(note) # for testing
        return note

    # convert frequency to number
    def freq_to_num(self):
        # source: https://github.com/TomSchimansky/GuitarTuner
        num = 12 * np.log2(self.freq / self.a4_freq) + 69
        return num

    # convert number to a note name
    def num_to_note(self, num):
        # source: https://github.com/TomSchimansky/GuitarTuner
        name = self.note_names[int(round(num) % 12)]
        return name

    # convert number to a frequency
    def num_to_freq(self, num, a4_freq):
        # source: https://github.com/TomSchimansky/GuitarTuner
        f = a4_freq * 2.0 ** ((num - 69) / 12.0)
        return f

    # set up of general text within the app
    def app_text(self):
        # timbre in upper left corner setup
        t_txt = self.create_label('Timbre', VTsettings.DEF_TEXT, 50, 30, 3, 3, 'Avenir', 16, QtCore.Qt.AlignLeft)
        # pitch in upper right corner setup
        p_txt = self.create_label('Pitch', VTsettings.DEF_TEXT, 50, 30, 1025, 3, 'Avenir', 16, QtCore.Qt.AlignRight)

    # set up of text in pitch screen
    def pitch_static(self):
        sharp = self.create_label('#', VTsettings.DEF_TEXT, 30, 30, 610, 208, 'Avenir', 16, QtCore.Qt.AlignRight)
        flat = self.create_label('b', VTsettings.DEF_TEXT, 30, 30, 610, 408, 'Avenir', 16, QtCore.Qt.AlignRight)

    # set up of text within timbre tuner hexagon
    def timbre_text(self):
        d_txt = self.create_label('Dark', VTsettings.DEF_TEXT, 50, 20, 243, 98, 'Avenir', 14, QtCore.Qt.AlignCenter)
        h_txt = self.create_label('Hollow', VTsettings.DEF_TEXT, 50, 20, 447, 203, 'Avenir', 14,
                                  QtCore.Qt.AlignLeft)
        s_txt = self.create_label('Stable', VTsettings.DEF_TEXT, 50, 20, 447, 417, 'Avenir', 14,
                                  QtCore.Qt.AlignLeft)
        b_txt = self.create_label('Bright', VTsettings.DEF_TEXT, 50, 20, 245, 520, 'Avenir', 14,
                                  QtCore.Qt.AlignCenter)
        f_txt = self.create_label('Full', VTsettings.DEF_TEXT, 50, 20, 40, 420, 'Avenir', 14, QtCore.Qt.AlignRight)
        v_txt = self.create_label('Vibrato', VTsettings.DEF_TEXT, 55, 20, 37, 205, 'Avenir', 14,
                                  QtCore.Qt.AlignRight)

    # create a hexagon with point coordinates
    def create_hex(self, r, s):
        hexagon = QtGui.QPolygonF()
        w = 360 / 6
        for i in range(6):
            t = w * i + s
            x = r * math.cos(math.radians(t))
            y = r * math.sin(math.radians(t))
            hexagon.append(QtCore.QPointF(self.width() / 4 + x, self.height() / 2 + y))
        return hexagon

        # general function for creating pens with certain settings

    def create_pen(self, width, colour, style, cap_style, join_style):
        pen = QtGui.QPen()
        pen.setWidth(width)
        pen.setColor(QtGui.QColor(colour))
        pen.setStyle(style)
        pen.setCapStyle(cap_style)
        pen.setJoinStyle(join_style)
        return pen

    # general function for creating labels
    def create_label(self, text, background, xSize, ySize, xLoc, yLoc, font, fontSize, alignment):
        label = QLabel(text, self)
        label.setStyleSheet(background)
        label.resize(xSize, ySize)
        label.move(xLoc, yLoc)
        label.setFont(QFont(font, fontSize))
        label.setAlignment(alignment)
        return label

    # display shapes and lines in app window
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        self.draw_static(event, painter)
        self.draw_shapes(event, painter)

    # draws all static elements in the GUI, e.g. lines that are not altered as the program runs
    def draw_static(self, event, qp):
        pen = self.create_pen(5, 'black', QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin)
        qp.setPen(pen)
        qp.drawPolygon(self.hexagon)

        # draw pitch grid midline
        qp.drawLine(637, 320, 973, 320)
        # set dash line parameters
        pen = self.create_pen(1, 'black', QtCore.Qt.DashLine, VTsettings.DEF_CAP, VTsettings.DEF_JOIN)
        qp.setPen(pen)
        # lower dashed
        qp.drawLine(644, 420, 973, 420)
        # upper dashed
        qp.drawLine(644, 220, 973, 220)
        # set solid line parameters
        pen = self.create_pen(2, 'black', QtCore.Qt.SolidLine, VTsettings.DEF_CAP, VTsettings.DEF_JOIN)
        qp.setPen(pen)
        # upper solid
        qp.drawLine(637, 120, 980, 120)
        # lower solid
        qp.drawLine(637, 520, 980, 520)

    # draw all dynamic elements that change depending on changing parameters
    def draw_shapes(self, event, qp):
        # draw note circle
        pen = self.create_pen(8, QtGui.QColor(self.pitch_colour), QtCore.Qt.SolidLine, VTsettings.DEF_CAP, VTsettings.DEF_JOIN)
        qp.setBrush(QBrush(QtGui.QColor(self.pitch_colour), QtCore.Qt.SolidPattern))
        qp.setPen(pen)
        qp.drawEllipse(QtCore.QRect(580, 280, 80, 80))

        # draw pitch bar
        pen = self.create_pen(1, QtGui.QColor(self.pitch_colour), QtCore.Qt.SolidLine, VTsettings.DEF_CAP, VTsettings.DEF_JOIN)
        qp.setBrush(QBrush(QtGui.QColor(self.pitch_colour), QtCore.Qt.SolidPattern))
        qp.setPen(pen)
        qp.drawRect(755, 320, 100, self.pitch_bar_height)

        # draw timbre lines
        if self.freq != VTsettings.NO_INPUT:
            pen = self.create_pen(5, '#FF9933', QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin)
            qp.setPen(pen)
            qp.drawLine(VTclass.Coordinates.vib_x, VTclass.Coordinates.vib_y, VTclass.Coordinates.col_x, VTclass.Coordinates.col_y)
            qp.drawLine(VTclass.Coordinates.vib_x, VTclass.Coordinates.vib_y, VTclass.Coordinates.vol_x, VTclass.Coordinates.vol_y)