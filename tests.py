import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense
from tensorflow.keras.callbacks import EarlyStopping
from Loader import DataLoader
import matplotlib.pyplot as plt
import numpy as np
import datetime

BATCH_SIZE = 128

# x_train = None
# x_val = None
x_train = DataLoader(BATCH_SIZE, 'training_generator')
x_val = DataLoader(BATCH_SIZE, 'training_generator', val=True)

lossHistory = []
valHistory = []

class NnueCallbacks(tf.keras.callbacks.Callback):
  def on_batch_end(self, batch, logs=None):
    lossHistory[-1].append(logs['loss'])
    if batch and batch % 15000 == 0:

      pred = self.model.predict(x_val)
      loss = (pred.flatten() - x_val.labels.flatten()[0:len(x_val)*BATCH_SIZE]) ** 2
      loss = np.sum(loss) / len(loss)
      valHistory[-1].append(loss)

      for i in lossHistory:
        plt.plot(i[20:], linewidth=0.5)
        plt.savefig("loss.png", dpi=400)
      plt.clf()

      for i in valHistory:
        plt.plot(i, linewidth=0.5)
        plt.savefig("val.png", dpi=400)
      
      plt.clf()

log_dir = "logs/fit/" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir=log_dir, histogram_freq=1)

from keras import backend as K
def clipped_relu(x):
    return K.relu(x, max_value=4)

model = Sequential()
model.add(Dense(128, input_shape=(769,), activation=clipped_relu))
model.add(Dense(32, activation=clipped_relu))
model.add(Dense(32, activation=clipped_relu))
model.add(Dense(1, activation='sigmoid'))

model.compile(loss='mse', optimizer='adam', metrics=['mae'])

lossHistory.append([])
valHistory.append([])
model.fit(x_train, validation_data=x_val, epochs=100, callbacks=[NnueCallbacks(), EarlyStopping(patience=1)])

#Epoch 2/2
#10906/10906 [==============================] - 225s 21ms/step - loss: 0.0243 - mae: 0.0866
