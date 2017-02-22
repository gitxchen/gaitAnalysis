import os
import os.path as path

import c3d

CURR_FOLDER = path.dirname(__file__)

# Folder containing .c3d files to be imported, subdivided by class
DATA_FOLDER = path.realpath(path.join(CURR_FOLDER, '..', 'data'))

# Folder that will contain processed pickles
OUT_FOLDER = path.realpath(path.join(CURR_FOLDER, '..', "processed"))

# Expected folders representing classes of diplegia
CLASS_FOLDERS = ["0", "1", "2", "3"]


# WARNING: this doesn't make data completely anonymous, as some fields in the c3ds still contains the patients info
# This should at least avoid printing the patients name in notebooks.
def anonymize_data():
    patient_index = 1

    for class_folder in CLASS_FOLDERS:
        class_path = path.join(DATA_FOLDER, class_folder)
        patients_folders = os.listdir(class_path)
        patients_folders.sort(key=lambda s: s.lower())

        for patient_folder in patients_folders:
            patient_path = path.join(class_path, patient_folder)
            patients_files = [f for f in os.listdir(patient_path) if f.endswith(".c3d")]
            patients_files.sort(key=lambda s: s.lower())

            file_index = 1

            for patient_file in patients_files:
                file_path = path.join(patient_path, patient_file)
                an_file_path = path.join(patient_path, str(patient_index) + '_' + str(file_index) + '.c3d')
                os.rename(file_path, an_file_path)
                file_index += 1

            an_patient_path = path.join(class_path, str(patient_index))
            os.rename(patient_path, an_patient_path)
            patient_index += 1


def filtered(filter_value, value):
    if filter_value is None:
        return False

    # TODO maybe manage list of filters

    return filter_value != value


# Flattened patients data iterator
def patients_data(class_filter=None, patient_filter=None, file_filter=None, verbose=1):
    for class_folder in CLASS_FOLDERS:
        if filtered(class_filter, class_folder):
            continue

        class_path = path.join(DATA_FOLDER, class_folder)
        patient_folders = os.listdir(class_path)
        patient_folders.sort(key=lambda s: s.lower())

        if verbose >= 1:
            print 'Reading class', class_folder

        for patient_folder in patient_folders:
            if filtered(patient_filter, patient_folder):
                continue

            patient_path = path.join(class_path, patient_folder)
            patient_files = [f for f in os.listdir(patient_path) if f.endswith(".c3d")]
            patient_files.sort(key=lambda s: s.lower())

            # Should be EXTRA CAREFUL in printing patient names
            # It would be best to anonymize data first
            ignore_warnings = False
            if verbose >= 2 and ignore_warnings:
                print 'Reading patient', patient_folder

            for patient_file in patient_files:
                if filtered(file_filter, patient_file):
                    continue

                file_path = path.join(patient_path, patient_file)

                if verbose >= 3:
                    print 'Reading file', patient_file

                try:
                    reader = c3d.Reader(open(file_path, 'rb'))
                    yield (reader, class_folder, patient_folder, patient_file)
                except Exception:
                    if verbose >= 1:
                        print 'Error reading', patient_file
                    continue


# Gets trimmed marker in the order specified in the c3d file
def get_markers(reader):
    markers = reader.get("POINT").get("LABELS").string_array
    return [marker.strip() for marker in markers]


def extract_data(class_filter=None, patient_filter=None, patient_file=None):
    data = []

    patients_iterator = patients_data(class_filter, patient_filter, patient_file)
    for reader, class_folder, patient_folder, patient_file in patients_iterator:

        # Gets trimmed marker in the order specified in the c3d file
        markers = reader.get("POINT").get("LABELS").string_array
        markers = [marker.strip() for marker in markers]

        for frame, points, analog in reader.read_frames():
            # idx = frame - first_frame
            # data[idx, :, :] = points[markers_indexes, 0:3]

            for marker, point in enumerate(points):
                if marker >= 255:
                    # Manage unexpected marker
                    continue

                row = [
                    int(class_folder),
                    patient_folder,
                    patient_file,
                    frame,
                    markers[marker],
                    point[0],
                    point[1],
                    point[2],
                    # There are only two cases: both 0, or both -1
                    # except for SM_scalza_gait18.c3d
                    1 if point[3] == -1.0 and point[4] == -1.0 else 0,
                ]

                data.append(row)

    return data
