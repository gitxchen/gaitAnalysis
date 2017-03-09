import os.path as path

from utils import patients_data, extract_data, fix_bad_data, get_foot_events

from utils import DataExtractError

skipped = []

patients_iterator = patients_data(file_filter='148_2.c3d')
for reader, class_folder, patient_folder, patient_file in patients_iterator:

    try:
        data = extract_data(reader)
        data, offset = fix_bad_data(data)

        l_on, l_off, r_on, r_off = get_foot_events(reader, offset)

        # TODO interpolate bad frames in the middle
        # TODO flip y and x axis when using short side
        # TODO crop frames according to foot events
        # TODO save in external file

    except DataExtractError, e:
        skipped.append([class_folder, patient_file, type(e).__name__])
        continue
