import os
import os.path as path

import numpy as np
import c3d

from scipy.interpolate import interp1d

from exceptions import *

CURR_FOLDER = path.dirname(__file__)

# Folder containing .c3d files to be imported, subdivided by class
DATA_FOLDER = path.realpath(path.join(CURR_FOLDER, '..', 'data'))

# Folder that will contain processed pickles
OUT_FOLDER = path.realpath(path.join(CURR_FOLDER, '..', "processed"))

# Expected folders representing classes of diplegia
CLASS_FOLDERS = ["0", "1", "2", "3"]

SUGGESTED_MARKERS = {"C7", "REP", "RUL", "RASIS", "RPSIS", "RCA", "RGT",
                     "RLE", "RFM", "RA", "LEP", "LUL", "LASIS",
                     "LPSIS", "LCA", "LGT", "LLE", "LFM", "LA"}

SUGGESTED_ANGLES = {"RAAngle", "LAAngle", "RKAngle", "LKAngle", "RHAngle", "LHAngle",
                    "RPelvisAngle", "LPelvisAngle", "RTRKAngle", "LTRKAngle",
                    "LFootProgressionAngle", "RFootProgressionAngle"}


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
    point = reader.get("POINT")
    labels = point.get("LABELS")
    labels2 = point.get("LABELS2")

    markers = labels.string_array
    if labels2 is not None:
        markers.extend(labels2.string_array)

    return [marker.strip().split(':')[-1] for marker in markers]


# Gets steps data
def get_foot_events(reader, offset=0):
    frame_rate = reader.header.frame_rate
    first_frame = reader.header.first_frame + offset

    event_group = reader.groups['EVENT']
    contexts = [context.strip() for context in event_group.get('CONTEXTS').string_array]
    labels = [label.strip() for label in event_group.get('LABELS').string_array]
    times = np.round(event_group.get('TIMES').float_array * frame_rate).astype(int)

    # Times array is parsed with right shape, but is read by columns instead of rows
    times = times.reshape((times.shape[1], times.shape[0]))[:, 1] - first_frame

    if len(times) == 0:
        raise NoEventsError()

    # All events should be after the first frame
    # Nevermind...
    # assert times.min() > 0

    positive = times > 0

    left = np.array([context == 'Left' for context in contexts])
    strike = np.array([label == 'Foot Strike' for label in labels])

    # Probably already sorted, insertion sort is best but numpy does not implement it
    l_on = np.sort(times[left & strike & positive])
    l_off = np.sort(times[left & ~strike & positive])
    r_on = np.sort(times[~left & strike & positive])
    r_off = np.sort(times[~left & ~strike & positive])

    return l_on, l_off, r_on, r_off


# Try to crop border with bad bits and interpolate small patches of bad bits in the middle
def fix_bad_data(data, interp_kind='slinear'):
    bad_bits = data[:, :, 3]

    # argmax used as firstIndexOf
    first_valid_idx = np.argmax(np.all(bad_bits != -1, axis=1))

    last_valid_idx = np.argmax(np.all(np.flip(bad_bits, axis=0) != -1, axis=1))
    last_valid_idx = data.shape[0] - last_valid_idx - 1

    # Crop border with bad bits
    data = data[first_valid_idx:last_valid_idx+1]
    bad_bits = bad_bits[first_valid_idx:last_valid_idx+1]

    bad_count = np.sum(np.any(bad_bits == -1, axis=1))
    bad_ratio = bad_count / data.shape[0]

    if bad_ratio > 0.1:
        raise TooManyBadBitsError()

    # Interpolate small patches of frames
    # TODO: try 3d interpolation (RegularGridInterpolator)
    for marker in np.arange(data.shape[1]):
        bad_frames = np.where(bad_bits[:, marker] == -1)[0]
        if len(bad_frames) > 0:
            valid_frames = np.where(bad_bits[:, marker] != -1)[0]
            f = interp1d(valid_frames, data[valid_frames, marker, :], axis=0, kind=interp_kind)
            data[bad_frames, marker, :] = f(bad_frames)

    offset = first_valid_idx
    return data, offset


# Extracts rescaled 3d data of selected markers, along with bad bits
def extract_data(reader, sugg_markers='markers'):

    # Load presets or use given suggested markers
    if sugg_markers == 'markers':
        sugg_markers = SUGGESTED_MARKERS    # 1089 / 1140
    elif sugg_markers == 'angles':
        sugg_markers = SUGGESTED_ANGLES     # 1110 / 1140
    elif sugg_markers == 'both':
        sugg_markers = SUGGESTED_MARKERS.union(SUGGESTED_ANGLES)    # 1088 / 1140
    else:
        sugg_markers = set(sugg_markers)

    markers = get_markers(reader)
    unavail_markers = sugg_markers.difference(markers)

    if len(unavail_markers) > 0:
        raise MissingMarkersError()

    # Just in case
    assert reader.header.point_count == len(markers)
    assert reader.header.frame_rate == 100.0

    sugg_markers_idxs = [markers.index(sugg_marker) for sugg_marker in sugg_markers]

    first_frame = reader.header.first_frame
    last_frame = reader.header.last_frame

    n_markers = len(sugg_markers)
    n_frames = last_frame - first_frame + 1

    data = np.zeros((n_frames, n_markers, 4))

    for frame, points, analog in reader.read_frames():
        idx = frame - first_frame
        data[idx] = points[sugg_markers_idxs, 0:4]

    # Rescale data back to meters using provided scale factor
    scale_factor = reader.header.scale_factor
    data[:, :, 0:3] *= abs(scale_factor)
    return data

