import numpy
import os
#i file sono matrici numpy
#le classi sono ordinate quindi leggere a batch non ha senso
#conviene restituire
#labels contiene le labels come matrice one-hot numpy


def generator_reggio(folder_path):
    #leggo numero gait data
    file_names = [folder_path+f for f in os.listdir(folder_path) if f[-7:] == "c3d.npy" ]
    total_size = len(file_names)
    #leggo labels
    res_label = numpy.load(folder_path+"labels.npy")

    assert total_size == len(res_label)



    yield [total_size]
    #devo capire quanti elementi allocare
    file_shape = numpy.load(file_names[0]).shape
    res_data = numpy.zeros((total_size,file_shape[0],file_shape[1],3))
    for i in xrange(total_size):
        res_data[i] = numpy.load(file_names[i])

    yield [res_data,res_label]

