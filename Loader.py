import tensorflow.keras as keras
import numpy as np
import math
import ctypes

def scaled_sigmoid(x):
    x = x.astype(float)
    return 1/(1+pow(2.71828, -(x/410)))

class DataLoader(keras.utils.Sequence):

    def __init__(self, batch_size, name, val=False):
        if val:
            self.lib = ctypes.CDLL('./val_loader.so')
        else:
            self.lib = ctypes.CDLL('./loader.so')
        
        self.lib.init(int(val), batch_size)
        self.lib.generate_features.restype = ctypes.POINTER(ctypes.c_int * (769*batch_size))
        self.lib.generate_labels.restype = ctypes.POINTER(ctypes.c_int * batch_size)
        
        self.batch_size = batch_size
        self.name = name

    def linecount(self):
        return ctypes.c_int.in_dll(self.lib, "linecount").value


    def ctypes_generate_features(self, index):
        return np.asarray(self.lib.generate_features(ctypes.c_int(index)).contents)
    def ctypes_generate_labels(self, index):
        return np.asarray(self.lib.generate_labels(ctypes.c_int(index)).contents)

    def __len__(self):
        return math.floor(self.linecount() / self.batch_size)

    def __getitem__(self, idx):
        x = self.ctypes_generate_features(idx).reshape(self.batch_size, 769)
        y = self.ctypes_generate_labels(idx)
        y = scaled_sigmoid(y)

        return np.array(x), np.array(y)


if __name__ == '__main__':
    l = DataLoader(32, 'generator', val=True)
    print(l[0])

    # for i in range(1000000):
    #     print(i)
    #     l[i]

    # g = l.__getitem__(3)
    # for i in range(32):
    #     print(g[0][i], g[1][i])
    #     print()