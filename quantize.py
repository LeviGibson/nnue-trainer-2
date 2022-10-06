import math
import struct

import matplotlib.pyplot as plt
import tensorflow as tf
import Features
import numpy as np

def sigmoid(x):
    return 1/(1+math.pow(math.e, -x))

def load_params():
    weights, biases = [], []

    model = tf.keras.models.load_model("production/")
    params = model.get_weights()


    # divide first layer biases by 127 because the first layer is not divided as part of the activation function
    params[1] /= 127
    # Divide the first layer weights and biases by 2 because during training, the max value for the clipped_relu is 2, whereas during quantization it should be 1.
    # Also divide all biases by 2
    params[0] /= 4
    params[1] /= 4
    params[3] /= 4
    params[5] /= 4
    params[7] /= 4

    for p in params:
        if len(p.shape) == 2:
            # for i in p.flatten():
            #     if i < -1 or i > 1: print(i)
            p[p > 1] = 1
            p[p < -1] = -1
            weights.append((p * 127).astype(int))
        else:
            biases.append((p * 127 * 127).astype(int))

    weights[-1] *= 4
    biases[-1] *= 4

    return weights, biases


weights, biases = load_params()


def predict(fen):
    x = Features.get(fen)

    l1 = np.copy(biases[0])
    for n in range(len(x)):
        for n2 in range(len(l1)):
            l1[n2] += weights[0][n][n2] * x[n]
    l1[l1 < 0] = 0
    l1[l1 > 127] = 127

    l2 = np.copy(biases[1])
    for n in range(len(l1)):
        for n2 in range(len(l2)):
            l2[n2] += weights[1][n][n2] * l1[n]

    l2 //= 127
    l2[l2 < 0] = 0
    l2[l2 > 127] = 127


    l3 = np.copy(biases[2])

    for n in range(len(l2)):
        for n2 in range(len(l3)):
            l3[n2] += weights[2][n][n2] * l2[n]
    l3 //= 127
    l3[l3 < 0] = 0
    l3[l3 > 127] = 127

    l4 = (np.sum(l3 * weights[3].reshape((32,))) + biases[3][0]) / 127 / 127

    print(sigmoid(l4))


# predict("8/2k5/8/8/8/8/2K2PPP/8 w - - 0 1")
# predict("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")

# print(weights[1].flatten())

outfile = open("network.nnue", 'wb')
for i in weights[0].flatten():
    outfile.write(struct.pack('<h', i))

for i in weights[1].flatten():
    outfile.write(struct.pack('<b', i))

for i in weights[2].flatten():
    outfile.write(struct.pack('<b', i))

for i in weights[3].flatten():
    outfile.write(struct.pack('<h', i))

for i in biases[0]:
    outfile.write(struct.pack('<h', i))

for i in biases[1]:
    outfile.write(struct.pack('<i', i))

for i in biases[2]:
    outfile.write(struct.pack('<i', i))

for i in biases[3]:
    outfile.write(struct.pack('<i', i))
