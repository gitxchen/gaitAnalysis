import os.path as path
import pandas as pd

from utils import patients_data

# This was a first attempt to store all data in a csv and load it on demand
# in a Pandas DataFrame, but the data is too much to be kept in tabular form in RAM

OUT_FOLDER = 'extracted'

# TODO: remove this and use anonymized data which is already numeric
patients_map = {}
files_map = {}
markers_map = {}

# WARNING: this is slow and memory-intensive
# use only for analysis of small samples


def class_to_csv(class_filter, filename):

    out_file = open(filename, 'w')

    for reader, class_folder, patient_folder, patient_file in patients_data(class_filter=class_filter):

        data = []
        print "Reading", class_folder, patient_folder, patient_file

        # Gets trimmed marker in the order specified in the c3d file
        markers = reader.get("POINT").get("LABELS").string_array
        markers = [marker.strip() for marker in markers]

        if patient_folder not in patients_map:
            patients_map[patient_folder] = len(patients_map)

        if patient_file not in files_map:
            files_map[patient_file] = len(files_map)

        for frame, points, analog in reader.read_frames():
            # idx = frame - first_frame
            # data[idx, :, :] = points[markers_indexes, 0:3]

            for marker, point in enumerate(points):
                # marker_label = markers[marker] if marker in markers else 'null'
                try:
                    marker_label = markers[marker]
                except:
                    marker_label = 'err'

                if marker_label not in markers_map:
                    markers_map[marker_label] = len(markers_map)

                row = [
                    int(class_folder),
                    patients_map[patient_folder],
                    files_map[patient_file],
                    frame,
                    markers_map[marker_label],
                    point[0],
                    point[1],
                    point[2],
                    # There are only two cases: both 0, or both -1
                    # except for 168_5.c3d
                    1 if point[3] == -1.0 and point[4] == -1.0 else 0,
                ]

                data.append(row)

        print "Adding to csv.."
        df = pd.DataFrame(data, columns=['class', 'patient', 'file', 'frame', 'marker', 'x', 'y', 'z', 'bad'])
        df.to_csv(out_file, index=False)
    print "CSV written."


class_to_csv("0", path.join(OUT_FOLDER, "class0.csv"))
class_to_csv("1", path.join(OUT_FOLDER, "class1.csv"))
class_to_csv("2", path.join(OUT_FOLDER, "class2.csv"))
class_to_csv("3", path.join(OUT_FOLDER, "class3.csv"))


# Save maps to file for future reference
# TODO: remove this

'''df = pd.DataFrame(patients_map)
df.to_csv(path.join(OUT_FOLDER, "patients_map.csv"), index=False)

df = pd.DataFrame(files_map)
df.to_csv(path.join(OUT_FOLDER, "files_map.csv"), index=False)

df = pd.DataFrame(markers_map)
df.to_csv(path.join(OUT_FOLDER, "markers_map.csv"), index=False)'''