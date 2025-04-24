import tensorflow as tf
import keras
from keras import layers
import numpy as np
import pandas as pd

MODEL_PATH = "emotion_recognition_model.keras"
DATASET_PATH = "face_data.csv"
INPUT_SHAPE = (1404)


# mean = X_train.mean().astype(np.float64) # 0.020804420971837947
# std = X_train.std().astype(np.float64) # 0.058424480229290865

def standardize(x) -> float:
    return (x - 0.020804420971837947) / 0.058424480229290865


def get_model(input_shape) -> keras.Sequential:
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

def train_model(
        model, dataset_path: str, input_shape: tuple, learning_rate: float = 0.0002, epochs: int = 30, batch_size: int = 32
) -> None:
    train = pd.read_csv(dataset_path),
    X_train = (train.iloc[:,1:].values).astype("float64")
    y_train = train.iloc[:,0].values.astype("int32")
    y_train = keras.utils.to_categorical(y_train)

    model = get_model(input_shape)
    model.optimizer.lr = learning_rate

    model.fit(X_train, y_train, batch_size=batch_size, epochs=epochs, validation_split=0.1)
    return model

def predict_emotion(model, landmarks, random_seed: int = 13) -> int:
    np.random.seed(random_seed)

    prediction = model.predict(np.array([landmarks]))
    predicted_emotion = np.argmax(prediction)
    probability = prediction[0][predicted_emotion]
    return predicted_emotion, probability

def load_model() -> keras.Sequential:
    model = keras.saving.load_model(MODEL_PATH)
    return model

def main() -> None:
    model = get_model()
    model = train_model(model, DATASET_PATH, INPUT_SHAPE)
    model.save(MODEL_PATH)

if __name__ == "__main__":
    main()