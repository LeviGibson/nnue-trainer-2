import tensorflow.keras as keras
import numpy as np
import math
import CsvProcessor, Features

class DataLoader(keras.utils.Sequence):

    def __init__(self, batch_size, name, filename="chessData.csv"):
        self.lines = []
        self.labels = []
        infile = open(filename, 'r')
        infile.readline()
        for i, line in enumerate(infile):
            l = CsvProcessor.process_line(line)
            self.lines.append(l)
            self.labels.append(l[1])
        self.labels = np.array(self.labels)
        
        self.batch_size = batch_size
        self.name = name

    def __len__(self):
        return math.floor(len(self.lines) / self.batch_size)

    def __getitem__(self, idx):
        x = []
        y = []
            
        for i in range(self.batch_size):
            index = i+(idx*self.batch_size)
            line = (self.lines[index])
            x.append(Features.get(line[0]))
            y.append(line[1])

        return np.array(x), np.array(y)


if __name__ == '__main__':
    l = DataLoader(32, 'generator')
    g = l.__getitem__(3)
    for i in range(32):
        print(g[0][i], g[1][i])
        print()