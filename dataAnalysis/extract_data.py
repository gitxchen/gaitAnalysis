import os.path as path

from utils import patients_data, extract_data, fix_bad_data, get_foot_events
from exceptions import DataExtractError

skipped = []

# file_filter = '148_2.c3d'  # Bad frame border
file_filter = '12_5.c3d'  # Bad in the middle
# file_filter = None

patients_iterator = patients_data(file_filter=file_filter)
for reader, class_folder, patient_folder, patient_file in patients_iterator:

    try:
        data = extract_data(reader)
        data, offset = fix_bad_data(data)

        l_on, l_off, r_on, r_off = get_foot_events(reader, offset)

        # TODO flip y and x axis when using short side
        # TODO crop frames according to foot events
        # TODO save in external file

    except DataExtractError, e:
        skipped.append([class_folder, patient_file, type(e).__name__])
        continue
