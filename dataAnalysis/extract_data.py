import os
import os.path as path
import numpy as np
import pandas as pd

from utils import patients_data, extract_data, get_valid_window, interp_missing_data, get_foot_events
from errors import DataExtractError

from utils import OUT_FOLDER

skipped = []

# file_filter = '148_2.c3d'  # Bad frame border
# file_filter = '12_5.c3d'  # Bad in the middle
file_filter = None

patients_iterator = patients_data(file_filter=file_filter)
for reader, class_folder, patient_folder, patient_file in patients_iterator:

    out_folder = path.join(OUT_FOLDER, class_folder, patient_folder)
    out_file = path.join(out_folder, patient_file[:-4])

    if not path.exists(out_folder):
        os.makedirs(out_folder)

    try:
        # Get data for specified markers, and try to fix bad bits
        data = extract_data(reader, sugg_markers='markers', center_descriptor='pelvis')

        first_idx, last_idx = get_valid_window(data)
        data = interp_missing_data(data[first_idx:last_idx+1], max_bad_perc=0.1)

        # Get foot events for valid window
        l_on, l_off, r_on, r_off = get_foot_events(reader, first_idx, last_idx)

        # TODO crop frames according to foot events
        # TODO visualize steps event, and verify their correctness

        np.save(out_file, data)

    except DataExtractError, e:
        exception_name = type(e).__name__
        skipped.append([class_folder, patient_folder, patient_file, exception_name])
        continue

log_file = path.join(OUT_FOLDER, 'error_log.csv')

skipped = pd.DataFrame(skipped, columns=['class', 'patient', 'file', 'error'])
skipped.to_csv(log_file, sep=';', index=False)