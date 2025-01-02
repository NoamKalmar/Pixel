import tensorflow as tf
import keras
from keras import layers
import numpy as np
import pandas as pd

MODEL_PATH = "emotion_recognition_model.keras"
INPUT_SHAPE = (1404)


# mean = X_train.mean().astype(np.float64) # 0.020804420971837947
# std = X_train.std().astype(np.float64) # 0.058424480229290865

def standardize(x):
    return (x - 0.020804420971837947) / 0.058424480229290865


def get_model(input_shape):
    model = keras.Sequential([
        keras.Input(shape=(input_shape,)),
        # layers.Lambda(standardize),
        layers.Flatten(),
        layers.Dense(256, activation="relu"),
        layers.Dense(128, activation="relu"),
        layers.Dense(3, activation="softmax")
    ])
    model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])
    return model

def train_and_save(model_path, input_shape):

    learning_rate = 0.0002
    epochs = 30
    batch_size = 32

    DATASET_PATH = "face_data.csv"

    train = pd.read_csv(DATASET_PATH)
    X_train = (train.iloc[:,1:].values).astype("float64")
    y_train = train.iloc[:,0].values.astype("int32")
    y_train = keras.utils.to_categorical(y_train)

    model = get_model(input_shape)
    model.optimizer.lr = learning_rate

    model.fit(X_train, y_train, batch_size=batch_size, epochs=epochs, validation_split=0.1)
    model.save(model_path)

def predict_emotion(model, landmarks):
    seed = 43
    np.random.seed(seed)

    prediction = model.predict(np.array([landmarks]))
    predicted_emotion = np.argmax(prediction)
    probability = prediction[0][predicted_emotion]
    return predicted_emotion, probability

if __name__ == "__main__":
    train_and_save(MODEL_PATH, INPUT_SHAPE)