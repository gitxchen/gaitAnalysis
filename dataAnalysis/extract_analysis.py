import os
import os.path as path
import numpy as np
import pandas as pd

from utils import patients_data, get_analysis
from errors import DataExtractError

from utils import OUT_FOLDER

skipped = []
data = []

# file_filter = '148_2.c3d'  # Bad frame border
# file_filter = '12_5.c3d'  # Bad in the middle
file_filter = None

patients_iterator = patients_data(file_filter=file_filter)
for reader, class_folder, patient_folder, patient_file in patients_iterator:
    try:
        rows = get_analysis(reader)

        for row in rows:
            data.append([int(class_folder), int(patient_folder), patient_file] + row)

    except DataExtractError, e:
        exception_name = type(e).__name__
        skipped.append([class_folder, patient_folder, patient_file, exception_name])
        continue


log_file = path.join(OUT_FOLDER, 'error_log.csv')
analysis_file = path.join(OUT_FOLDER, 'analysis.csv')

skipped = pd.DataFrame(skipped, columns=['class', 'patient', 'file', 'error'])
skipped.to_csv(log_file, sep=';', index=False)

analysis = pd.DataFrame(data, columns=[
    'class',
    'patient',
    'file',

    'Cadence Left',
    'Speed Left',
    'Stance Time Left',
    'Swing Time Left',
    '1 Double Support Left',
    '2 Double Support Left',
    '1 Single Support Left',
    'Opposite Foot Contact Left',
    'Stride Length Left',
    'Stride Length Normalised Left',
    'Cycle Time Left',
    'Speed Normalised Left',
    'Cadence Right',
    'Speed Right',
    'Stance Time Right',
    'Swing Time Right',
    '1 Double Support Right',
    '2 Double Support Right',
    '1 Single Support Right',
    'Opposite Foot Contact Right',
    'Stride Length Right',
    'Stride Length Normalised Right',
    'Cycle Time Right',
    'Speed Normalised Right',
])

analysis.to_csv(analysis_file, sep=';', index=False)
