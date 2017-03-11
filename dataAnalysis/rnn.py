import numpy as np
from keras.models import Model
from keras.layers import LSTM, Input, Dense, Flatten, MaxPooling1D, Masking
from keras.preprocessing.sequence import pad_sequences

import os
import os.path as path
from utils import OUT_FOLDER


def dir_iterator(filepath, type='dir'):
    files = [path.join(filepath, f) for f in os.listdir(filepath)]

    if type == 'dir':
        files = [f for f in files if path.isdir(f)]
    else:
        files = [f for f in files if f.endswith("." + type)]

    files.sort(key=lambda s: s.lower())
    return files


def flatten_and_pad_data(data, max_len):
    padded = np.zeros((len(data), max_len), dtype=np.float64)
    for i, sequence in enumerate(data):
        padded[i, :len(sequence)] = sequence
    return padded


def load_data(test_size=0.3):

    max_len = 0

    for class_folder in dir_iterator(OUT_FOLDER):
        for patient_folder in dir_iterator(class_folder):
            for patient_file in dir_iterator(patient_folder, 'npz'):
                with np.load(patient_file) as archive:
                    lengths = [len(archive[name]) for name in archive.files]
                    max_len = max(max_len, np.max(lengths))

    Xtrain = []
    Xtest = []

    Ytrain = []
    Ytest = []

    for class_folder in dir_iterator(OUT_FOLDER):
        for patient_folder in dir_iterator(class_folder):

            sequences = []

            for patient_file in dir_iterator(patient_folder, 'npz'):
                with np.load(patient_file) as archive:
                    sequences.extend([archive[name] for name in archive.files])

            for sequence in sequences:
                max_len = max(max_len, len(sequence))

            # Randomize train test split
            np.random.shuffle(sequences)

            cut = int(test_size * len(sequences))
            Xtest.extend(sequences[:cut])
            Xtrain.extend(sequences[cut:])

            y = int(path.basename(class_folder))
            Ytest.extend(np.repeat(y, cut))
            Ytrain.extend(np.repeat(y, len(sequences) - cut))

    Xtrain = flatten_and_pad_data(Xtrain, max_len=max_len)
    Xtest = flatten_and_pad_data(Xtest, max_len=max_len)


    x = 2


load_data(test_size=0.3)

exit()


model_in = Input(shape=())

x = Masking(mask_value=0, input_shape=())(model_in)
x = LSTM(32, output_dim=())(x)

model_out = Dense(1, activation='sigmoid')(x)

model = Model(input=model_in, output=model_out)
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

model.fit_generator(generate_batch(), nb_epoch=1, samples_per_epoch=10, validation_data=generate_batch(), nb_val_samples=10)