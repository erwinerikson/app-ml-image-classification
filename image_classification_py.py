# -*- coding: utf-8 -*-
"""Untitled4.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1yCSn5_yc4E4jajnA9TNGGmMY_wLcjS1S
"""

import os
import zipfile
import tensorflow as tf
import matplotlib.pyplot as plt
import pathlib

local_zip = '/content/drive/MyDrive/Animal-10.zip'
zip_ref = zipfile.ZipFile(local_zip, 'r')
zip_ref.extractall('/content')
zip_ref.close()

os.listdir()

dir_path = '/content/raw-img'
os.listdir(dir_path)

train_generator= tf.keras.preprocessing.image_dataset_from_directory(
    dir_path,
    validation_split=0.2,
    image_size=(224,224),
    seed=100,
    batch_size=32,
    subset="training",
)
val_generator= tf.keras.preprocessing.image_dataset_from_directory(
    dir_path,
    validation_split=0.2,
    image_size=(224,224),
    seed=200,
    batch_size=32,
    subset="validation",
)

model = tf.keras.models.Sequential([
    tf.keras.layers.Conv2D(32, kernel_size = 3, activation='relu', input_shape=(224, 224, 3)),
    tf.keras.layers.MaxPooling2D(2,2),
    tf.keras.layers.BatchNormalization(),
    tf.keras.layers.Conv2D(32, kernel_size = 3, activation='relu'),
    tf.keras.layers.MaxPooling2D(2,2),
    tf.keras.layers.BatchNormalization(),
    tf.keras.layers.Conv2D(64, kernel_size = 5, padding='same', activation='relu'),
    tf.keras.layers.MaxPooling2D(2,2),
    tf.keras.layers.BatchNormalization(),
    tf.keras.layers.Dropout(0.4),
    tf.keras.layers.Conv2D(128, kernel_size = 5, padding='same', activation='relu'),
    tf.keras.layers.MaxPooling2D(2,2),
    tf.keras.layers.BatchNormalization(),
    tf.keras.layers.Dropout(0.4),
    tf.keras.layers.Conv2D(256, kernel_size = 4, activation='relu'),
    tf.keras.layers.MaxPooling2D(2,2),
    tf.keras.layers.BatchNormalization(),
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dropout(0.4),
    tf.keras.layers.Dense(10, activation='softmax')
])

model.summary()

optimizer = tf.optimizers.Adam(learning_rate=1e-3, amsgrad=True, use_ema=True)
model.compile(loss='sparse_categorical_crossentropy',
		optimizer=optimizer,
		metrics=['accuracy'])

class ModelCallback(tf.keras.callbacks.Callback):
    def on_epoch_end(self, epoch, logs={}):
        if logs.get('accuracy') > 0.93 and logs.get('val_accuracy') > 0.93:
            self.model.stop_training = True

history = model.fit(
    train_generator,
    epochs=200,
    validation_data=val_generator,
    verbose=2,
    callbacks=ModelCallback())

plt.figure(figsize=(15,5))
plt.subplot(1,2,1)
plt.plot(history.history['loss'],label='Train_Loss')
plt.plot(history.history['val_loss'],label='Validation_Loss')
plt.title('Model Loss',fontsize=20)
plt.ylabel('Loss')
plt.xlabel('Epoch')
plt.legend()
plt.subplot(1,2,2)
plt.plot(history.history['accuracy'],label='Train_Accuracy')
plt.plot(history.history['val_accuracy'],label='Validation_Accuracy')
plt.title('Model Accuracy',fontsize=20)
plt.ylabel('Accuracy')
plt.xlabel('Epoch')
plt.legend()

export_dir = 'saved_model/'
tf.saved_model.save(model, export_dir)

converter = tf.lite.TFLiteConverter.from_saved_model(export_dir)
tflite_model = converter.convert()

tflite_model_file = pathlib.Path('vegs.tflite')
tflite_model_file.write_bytes(tflite_model)

os.listdir()