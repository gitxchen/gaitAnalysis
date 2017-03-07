import os
import numpy
from sklearn.model_selection import train_test_split
from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation,Flatten
from keras.layers.recurrent import LSTM
from keras.optimizers import Adam
import pandas
from sklearn.preprocessing import MinMaxScaler
import sys

numpy.random.seed(10)
sys.setrecursionlimit(40000)

#carico dati
BASE_FOLDER = "../processed_1/"
l = [f for f in os.listdir(BASE_FOLDER) if "c3d" in f]
#ordino la lista
l= sorted(l,cmp=lambda x,y: 1 if int(x.split(".")[0]) > int(y.split(".")[0]) else -1)
#parametri
SEQ_NUM = 9
SEQ_LEN = 75
NUM_PARAMS = 43
NUM_COORDS = 1
data = numpy.zeros((len(l)*SEQ_NUM,SEQ_LEN,NUM_PARAMS,NUM_COORDS))
labels = numpy.zeros((len(l)*SEQ_NUM,1,NUM_PARAMS,NUM_COORDS))
labels_classes = numpy.load(BASE_FOLDER+"labels_classes.npy")
labels_patients = numpy.load(BASE_FOLDER+"labels_patients.npy")
index = 0
for f in l:
    arr = numpy.load(BASE_FOLDER+f)
    arr_0 = arr["arr_0"]
    arr_1 = arr['arr_1']
    data[index:index+len(arr_0)] = arr_0
    labels[index:index+len(arr_1)] = arr_1
    index+=len(arr_0)
#adesso so il numero
data = data[0:index]
labels = labels[0:index]


data_train = []
data_test = []
labels_train = []
labels_test = []
labels_classes_train = []
labels_classes_test = []
labels_patient_train = []
labels_patient_test = []

#devo dividere le classi
for i in range(0,4):

    data_sel = data[labels_classes == i]
    labels_sel = labels[labels_classes == i]
    labels_patients_sel = labels_patients[labels_classes == i]
    #divido i pazienti
    labels_patients_sel_train_unique,labels_patients_sel_test_unique = train_test_split(numpy.unique(labels_patients_sel),train_size=0.9)
    #prendo data
    data_sel_train = data_sel[numpy.in1d(labels_patients_sel,labels_patients_sel_train_unique)]
    data_sel_test = data_sel[numpy.in1d(labels_patients_sel,labels_patients_sel_test_unique)]
    #prendo labels
    labels_sel_train = labels_sel[numpy.in1d(labels_patients_sel,labels_patients_sel_train_unique)]
    labels_sel_test = labels_sel[numpy.in1d(labels_patients_sel,labels_patients_sel_test_unique)]
    #prendo il paziente
    labels_patients_sel_train = labels_patients_sel[numpy.in1d(labels_patients_sel,labels_patients_sel_train_unique)]
    labels_patients_sel_test = labels_patients_sel[numpy.in1d(labels_patients_sel,labels_patients_sel_test_unique)]
    #per la classe mi serve semplicemente i
    labels_classes_sel_train = numpy.ones_like(labels_patients_sel_train)*i
    labels_classes_sel_test = numpy.ones_like(labels_patients_sel_test)*i

    data_train.append(data_sel_train)
    data_test.append(data_sel_test)
    labels_train.append(labels_sel_train)
    labels_test.append(labels_sel_test)
    labels_classes_train.append(labels_classes_sel_train)
    labels_classes_test.append(labels_classes_sel_test)
    labels_patient_train.append(labels_patients_sel_train)
    labels_patient_test.append(labels_patients_sel_test)


data_train = numpy.vstack(data_train)
data_test = numpy.vstack(data_test)
labels_train =numpy.vstack(labels_train)
labels_test=numpy.vstack(labels_test)
labels_classes_train= numpy.hstack(labels_classes_train)
labels_classes_test= numpy.hstack(labels_classes_test)
labels_patient_train= numpy.hstack(labels_patient_train)
labels_patient_test= numpy.hstack(labels_patient_test)

#pandas

labels_classes_train = pandas.get_dummies(labels_classes_train).values
labels_classes_test = pandas.get_dummies(labels_classes_test).values
#reshape
data_train = data_train.reshape(-1,SEQ_LEN,NUM_PARAMS*NUM_COORDS)
data_test = data_test.reshape(-1,SEQ_LEN,NUM_PARAMS*NUM_COORDS)

perm = numpy.random.permutation(len(data_train))
data_train = data_train[perm]
labels_train = labels_train[perm]
labels_classes_train = labels_classes_train[perm]
labels_patient_train = labels_patient_train[perm]


model = Sequential()
model.add(LSTM(16, input_shape=data_train.shape[1:],init="uniform",inner_init="uniform",return_sequences=True))

model.add(Flatten())
#model.add(Dense(256,init="uniform"))
#model.add(Activation('tanh'))
#model.add(Dense(64,init="uniform"))
#model.add(Activation('sigmoid'))
model.add(Dense(4))
#model.add(Dropout(0.1))
model.add(Activation('softmax'))

model.summary()

model.compile(loss='categorical_crossentropy',
              optimizer=Adam(),
              metrics=['accuracy'])

while True:
    epochs = int(raw_input("epochs"))
    history = model.fit(data_train, labels_classes_train,
                        batch_size=100, nb_epoch=epochs,shuffle=False,
                        verbose=2, validation_data=(data_test, labels_classes_test))
    #score = model.evaluate(data_test, labels_test, verbose=0)
