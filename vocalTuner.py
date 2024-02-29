# VocalTuner Application
# This application analyses the timbre and pitch characteristics of an input sound.
# The purpose of the VocalTuner is to assist vocalists when practicing control over their vocal pitch and timbre
# Developed by Suvi Häärä
# 2021-2022

import sys
from PyQt5.QtWidgets import *
import VTgui

# run and display application
app = QApplication(sys.argv)
vocal_tuner = VTgui.VocalTuner()
vocal_tuner.show()
sys.exit(app.exec_())
