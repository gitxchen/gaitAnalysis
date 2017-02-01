'''Trains a simple deep NN on the MNIST dataset.

Gets to 98.40% test accuracy after 20 epochs
(there is *a lot* of margin for parameter tuning).
2 seconds per epoch on a K520 GPU.
'''

from __future__ import print_function
import numpy as np

from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation
from keras.optimizers import Adam
from keras.utils import np_utils
from sklearn.model_selection import train_test_split
from generator_reggio import generator_reggio
import numpy
#TEST MLP KERAS
batch_size = 256
nb_epoch = 20

# the data, shuffled and split between train and test sets
generator = generator_reggio("../processed/")
generator.next()
data,labels = generator.next()
perm = numpy.random.permutation(len(data))
data = data[perm]
labels = labels[perm]

data_train,data_test,labels_train,labels_test = train_test_split(data,labels,train_size=0.9,stratify=numpy.argmax(labels,axis=1))



data_train = data_train.reshape(len(data_train),-1).astype("float32")
data_test = data_test.reshape(len(data_test),-1).astype("float32")

# convert class vectors to binary class matrices

model = Sequential()
model.add(Dense(512, input_shape=(len(data_train[0]),)))
model.add(Activation('sigmoid'))
model.add(Dropout(0.4))
model.add(Dense(1024))
model.add(Activation('sigmoid'))
model.add(Dropout(0.4))
model.add(Dense(512))
model.add(Activation('sigmoid'))
model.add(Dropout(0.2))
model.add(Dense(256))
model.add(Activation('sigmoid'))
model.add(Dropout(0.4))
model.add(Dense(4))
model.add(Activation('softmax'))

model.summary()

model.compile(loss='categorical_crossentropy',
              optimizer=Adam(),
              metrics=['accuracy'])

history = model.fit(data_train, labels_train,
                    batch_size=batch_size, nb_epoch=nb_epoch,
                    verbose=1, validation_data=(data_test, labels_test))
score = model.evaluate(data_test, labels_test, verbose=0)
print('Test score:', score[0])
print('Test accuracy:', score[1])