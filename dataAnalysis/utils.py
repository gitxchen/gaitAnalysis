import os
import os.path as path

import numpy as np
import c3d

from scipy.interpolate import interp1d

from errors import *

CURR_FOLDER = path.dirname(__file__)

# Folder containing .c3d files to be imported, subdivided by class
DATA_FOLDER = path.realpath(path.join(CURR_FOLDER, '..', 'data'))

# Folder that will contain processed pickles
OUT_FOLDER = path.realpath(path.join(CURR_FOLDER, '..', "processed"))

# Expected folders representing classes of diplegia
CLASS_FOLDERS = ["0", "1", "2", "3"]

SUGGESTED_MARKERS = list({"C7", "REP", "RUL", "RASIS", "RPSIS", "RCA", "RGT",
                          "RLE", "RFM", "RA", "LEP", "LUL", "LASIS",
                          "LPSIS", "LCA", "LGT", "LLE", "LFM", "LA"})

SUGGESTED_ANGLES = list({"RAAngle", "LAAngle", "RKAngle", "LKAngle", "RHAngle", "LHAngle",
                         "RPelvisAngle", "LPelvisAngle", "RTRKAngle", "LTRKAngle",
                         "LFootProgressionAngle", "RFootProgressionAngle"})


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


# Find frame window that has no bad bits in the borders
def get_valid_window(data):
    bad_bits = data[:, :, 3]  # type: np.ndarray

    # argmax gives index of first True
    first_valid_idx = np.argmax(np.all(bad_bits != -1, axis=1))

    last_valid_idx = np.argmax(np.all(np.flip(bad_bits, axis=0) != -1, axis=1))
    last_valid_idx = data.shape[0] - last_valid_idx - 1

    return first_valid_idx, last_valid_idx


# Interpolate small patches of bad bits
def interp_missing_data(data, interp_kind='slinear', max_bad_perc=0.1):
    bad_bits = data[:, :, 3]  # type: np.ndarray

    bad_count = np.sum(np.any(bad_bits == -1, axis=1))
    bad_ratio = bad_count / data.shape[0]

    if bad_ratio > max_bad_perc:
        raise TooManyBadBitsError()

    # TODO: max_patch threshold and exception if surpassed

    # Interpolate small patches of frames
    # TODO: consider 3d interpolation (RegularGridInterpolator)
    for marker in np.arange(data.shape[1]):
        bad_frames = np.where(bad_bits[:, marker] == -1)[0]
        if len(bad_frames) > 0:
            valid_frames = np.where(bad_bits[:, marker] != -1)[0]
            f = interp1d(valid_frames, data[valid_frames, marker, :], axis=0, kind=interp_kind)
            data[bad_frames, marker, :] = f(bad_frames)

    return data


def get_main_axis(data, center_descriptor_idxs):
    center_descriptor_data = data[:, center_descriptor_idxs, :]
    center_data = np.mean(center_descriptor_data, axis=1)

    range_x = np.max(center_data[:, 0]) - np.min(center_data[:, 0])
    range_y = np.max(center_data[:, 1]) - np.min(center_data[:, 1])

    return 0 if range_x > range_y else 1


def swap_axes(data):
    tmp = data[:, :, 0]
    data[:, :, 0] = data[:, :, 1]
    data[:, :, 1] = tmp
    return data


# Gets steps data
def get_foot_events(reader, first_idx=0, last_idx=None):
    frame_rate = reader.header.frame_rate
    first_frame = reader.header.first_frame

    if last_idx is None:
        last_frame = reader.reader.last_frame
        last_idx = last_frame - first_frame

    event_group = reader.get('EVENT')
    contexts = [context.strip() for context in event_group.get('CONTEXTS').string_array]
    labels = [label.strip() for label in event_group.get('LABELS').string_array]
    times = np.round(event_group.get('TIMES').float_array * frame_rate).astype(int)

    # Times array is parsed with right shape, but is read by columns instead of rows
    times = times.reshape((times.shape[1], times.shape[0]))[:, 1]

    if len(times) == 0:
        raise NoEventsError()

    indices = times - first_frame

    # Only consider events inside valid window
    in_window = (indices >= first_idx) & (indices <= last_idx)

    left = np.array([context == 'Left' for context in contexts])
    strike = np.array([label == 'Foot Strike' for label in labels])

    # Shift indices by window start
    indices -= first_idx

    # Probably already sorted, insertion sort is best but numpy does not implement it
    l_on = np.sort(times[left & strike & in_window])
    l_off = np.sort(times[left & ~strike & in_window])
    r_on = np.sort(times[~left & strike & in_window])
    r_off = np.sort(times[~left & ~strike & in_window])

    return l_on, l_off, r_on, r_off


def get_analysis(reader):
    analysis_group = reader.get('ANALYSIS')
    names = [name.strip().replace('\xb0', '') for name in analysis_group.get('NAMES').bytes_array]
    contexts = [context.strip() for context in analysis_group.get('CONTEXTS').string_array]
    # units = [unit.strip() for unit in analysis_group.get('UNITS').string_array]
    values = analysis_group.get('VALUES').float_array

    rows = []

    if len(names) % 24 != 0:
        raise IncompleteAnalysisError()

    for s in range(0, len(names), 24):
        values_dict = {names[s:s+24][i] + " " + contexts[s:s+24][i]: values[s:s+24][i] for i in range(24)}
        rows.append([
            values_dict['Cadence Left'],
            values_dict['Speed Left'],
            values_dict['Stance Time Left'],
            values_dict['Swing Time Left'],
            values_dict['1 Double Support Left'],
            values_dict['2 Double Support Left'],
            values_dict['1 Single Support Left'],
            values_dict['Opposite Foot Contact Left'],
            values_dict['Stride Length Left'],
            values_dict['Stride Length Normalised Left'],
            values_dict['Cycle Time Left'],
            values_dict['Speed Normalised Left'],

            values_dict['Cadence Right'],
            values_dict['Speed Right'],
            values_dict['Stance Time Right'],
            values_dict['Swing Time Right'],
            values_dict['1 Double Support Right'],
            values_dict['2 Double Support Right'],
            values_dict['1 Single Support Right'],
            values_dict['Opposite Foot Contact Right'],
            values_dict['Stride Length Right'],
            values_dict['Stride Length Normalised Right'],
            values_dict['Cycle Time Right'],
            values_dict['Speed Normalised Right'],
        ])

    return rows

# Extracts rescaled 3d data of selected markers, along with bad bits
def extract_data(reader, sugg_markers='markers', center_descriptor=None):
    # Load presets or use given suggested markers
    if sugg_markers == 'markers':
        sugg_markers = SUGGESTED_MARKERS  # 1089 / 1140
    elif sugg_markers == 'angles':
        sugg_markers = SUGGESTED_ANGLES  # 1110 / 1140
    elif sugg_markers == 'both':
        sugg_markers = list(set(SUGGESTED_MARKERS).union(SUGGESTED_ANGLES))  # 1088 / 1140

    # Load preset or use given center descriptor
    if center_descriptor == 'pelvis':
        center_descriptor = ["RASIS", "RPSIS", "LASIS", "LPSIS"]
    elif center_descriptor is not list:
        center_descriptor = [center_descriptor]

    markers = get_markers(reader)
    unavail_markers = set(sugg_markers).difference(markers)

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

    # If center descriptor available, use it to infer main axis, and swap axes if needed
    if center_descriptor is not None:
        descriptor_idxs = [sugg_markers.index(pelvis_marker) for pelvis_marker in center_descriptor]

        main_axis = get_main_axis(data, descriptor_idxs)
        if main_axis == 0:
            data = swap_axes(data)

    # Rescale data back to meters using provided scale factor
    scale_factor = reader.header.scale_factor
    data[:, :, 0:3] *= abs(scale_factor)
    return data
