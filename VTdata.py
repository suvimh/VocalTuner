# VocalTuner Application
# This application analyses the timbre and pitch characteristics of an input sound.
# The purpose of the VocalTuner is to assist vocalists when practicing control over their vocal pitch and timbre

# Developed by Suvi Häärä
# 2021-2022

import numpy as np
from sklearn.utils import Bunch
import csv


# loads the dataset from a designated file for use in program
import VTsetup


def load_data(file):
    # source: https://stackoverflow.com/questions/42432850/how-to-create-my-own-datasets-using-in-scikit-learn
    # modified to work with my dataset
    with open(file) as csv_file:
        data_reader = csv.reader(csv_file)
        feature_names = next(data_reader)[1:-2]
        data = []
        target = []
        for row in data_reader:
            features = row[:-2]
            label = row[-2]
            data.append([float(num) for num in features])
            target.append(int(label))

        data = np.array(data)
        target = np.array(target)
    return Bunch(data=data, target=target, feature_names=feature_names)


# convert csv files to arrays that can be used for knn
MY_DATA_COL = load_data(VTsetup.COL_DATA)
MY_DATA_VOL = load_data(VTsetup.VOL_DATA)
