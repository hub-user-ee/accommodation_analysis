"""
This script trains a neural network model to predict rental prices using TensorFlow and Keras. It performs the following steps:
1. Loads and preprocesses the dataset.
2. Splits the data into training and testing sets.
3. Normalizes the feature data using StandardScaler.
4. Defines a function to build a Keras Sequential model with hyperparameter tuning.
5. Conducts a hyperparameter search using Keras Tuner to find the best model configuration.
6. Trains the best model found during the hyperparameter search.
7. Evaluates the trained model on the test data.
8. Displays predictions for 20 random examples from the test set.

The trained model and scaler are saved as .pkl files for future use.

Author: Elias Eschenauer
Version: 2024/06
"""

# --------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------
import joblib
import numpy as np
import pandas as pd
import tensorflow as tf
import keras_tuner as kt
import matplotlib.pyplot as plt
from keras.src.callbacks import EarlyStopping
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Dense, Dropout, Input

# --------------------------------------------------------------------
# Function definition
# --------------------------------------------------------------------
def load_and_prepare_data(file_path):
    """
    Load and prepare data for training and testing.

    Args:
        file_path (str): Path to the CSV file containing the dataset.

    Returns:
        X_train (np.array): Training features.
        X_test (np.array): Testing features.
        y_train (np.array): Training labels.
        y_test (np.array): Testing labels.
        scaler (StandardScaler): Fitted scaler for data normalization.
    """
    data = pd.read_csv(file_path)
    X = data.drop(columns=['price'])
    y = np.log1p(data['price'])

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    joblib.dump(scaler, 'scaler.pkl')

    return X_train, X_test, y_train, y_test, scaler


def build_model(hp):
    """
    Build a Keras Sequential model with hyperparameter tuning.

    Args:
        hp (kt.HyperParameters): Hyperparameters for tuning.

    Returns:
        model (tf.keras.Sequential): Compiled Keras model.
    """
    model = Sequential()
    model.add(Input(shape=(X_train.shape[1],)))
    model.add(Dense(units=hp.Int('units', min_value=32, max_value=512, step=32), activation='relu',
                    input_dim=X_train.shape[1]))
    model.add(Dropout(rate=hp.Float('dropout', min_value=0.0, max_value=0.5, step=0.1)))

    for i in range(hp.Int('num_layers', 1, 3)):
        model.add(Dense(units=hp.Int(f'units_{i}', min_value=32, max_value=512, step=32), activation='relu'))
        model.add(Dropout(rate=hp.Float(f'dropout_{i}', min_value=0.0, max_value=0.5, step=0.1)))

    model.add(Dense(units=1))
    model.compile(
        optimizer=tf.keras.optimizers.Adam(hp.Float('learning_rate', min_value=1e-4, max_value=1e-2, sampling='LOG')),
        loss='mean_squared_error')
    return model


def perform_hyperparameter_search(X_train, y_train):
    """
    Perform hyperparameter search using Keras Tuner.

    Args:
        X_train (np.array): Training features.
        y_train (np.array): Training labels.

    Returns:
        tuner (kt.RandomSearch): Keras Tuner with the best hyperparameters found.
    """
    tuner = kt.RandomSearch(build_model, objective='val_loss', max_trials=10, executions_per_trial=2,
                            directory='my_dir',
                            project_name='intro_to_kt')

    early_stopping = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)

    tuner.search(X_train, y_train, epochs=200, validation_split=0.2, callbacks=[early_stopping])

    return tuner


def train_best_model(tuner, X_train, y_train):
    """
    Train the best model found by the hyperparameter search.

    Args:
        tuner (kt.RandomSearch): Keras Tuner with the best hyperparameters found.
        X_train (np.array): Training features.
        y_train (np.array): Training labels.

    Returns:
        best_model (tf.keras.Sequential): Trained Keras model.
        history (tf.keras.callbacks.History): Training history of the model.
    """
    best_hps = tuner.get_best_hyperparameters(num_trials=1)[0]
    print(f"""
    Best Hyperparameters:
    - Units in the first layer: {best_hps.get('units')}
    - Dropout in the first layer: {best_hps.get('dropout')}
    - Learning rate: {best_hps.get('learning_rate')}
    """)

    best_model = tuner.hypermodel.build(best_hps)
    history = best_model.fit(X_train, y_train, epochs=200, validation_split=0.2,
                             callbacks=[EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)])

    return best_model, history


def evaluate_model(model, X_test, y_test):
    """
    Evaluate the trained model on the test set.

    Args:
        model (tf.keras.Sequential): Trained Keras model.
        X_test (np.array): Testing features.
        y_test (np.array): Testing labels.

    Returns:
        mse (float): Mean squared error on the test set.
        rmse (float): Root mean squared error on the test set.
    """
    # Make predictions
    y_pred_log = model.predict(X_test)

    # Transform predictions back to the original scale
    y_pred = np.expm1(y_pred_log)

    # Transform y_test back to the original scale
    y_test_orig = np.expm1(y_test)

    # Calculate MSE
    mse = np.mean((y_test_orig - y_pred.flatten()) ** 2)

    # Calculate RMSE
    rmse = np.sqrt(mse)

    print(f'Test MSE: {mse:.2f}, Test RMSE: {rmse:.2f}')

    return mse, rmse


def display_random_predictions(model, X_test, y_test):
    """
    Display predictions for 20 random examples from the test set.

    Args:
        model (tf.keras.Sequential): Trained Keras model.
        X_test (np.array): Testing features.
        y_test (np.array): Testing labels.
    """
    y_pred = model.predict(X_test)
    y_pred = np.expm1(y_pred)

    np.random.seed(42)
    random_indices = np.random.choice(len(y_test), size=20, replace=False)

    print("\nActual prices and predictions for 20 random examples:")
    for idx in random_indices:
        true_price = np.expm1(y_test.iloc[idx])
        predicted_price = y_pred[idx][0]
        print(f"Index {idx}: Actual Price = {true_price:.2f}, Predicted Price = {predicted_price:.2f}")


def plot_rmse(history):
    """
    Plot RMSE curves for training and validation based on the training history.

    Args:
        history (tf.keras.callbacks.History): Training history of the model.
    """
    train_rmse = np.sqrt(history.history['loss'])
    val_rmse = np.sqrt(history.history['val_loss'])
    epochs = range(1, len(train_rmse) + 1)

    plt.figure(figsize=(10, 6))
    plt.plot(epochs, train_rmse, 'b-', label='Training RMSE')
    plt.plot(epochs, val_rmse, 'r-', label='Validation RMSE')
    plt.title('Neural Network Learning Curve')
    plt.xlabel('Epochs')
    plt.ylabel('RMSE')
    plt.legend()
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    # Load and prepare data
    X_train, X_test, y_train, y_test, scaler = load_and_prepare_data('machine_learning_data_clean.csv')

    # Perform hyperparameter search
    tuner = perform_hyperparameter_search(X_train, y_train)

    # Train the best model
    best_model, history = train_best_model(tuner, X_train, y_train)

    # Save the best model
    joblib.dump(best_model, 'nn_model.pkl')

    # Evaluate the model
    mse, rmse = evaluate_model(best_model, X_test, y_test)

    # Display random predictions
    display_random_predictions(best_model, X_test, y_test)

    # Plot RMSE curve
    plot_rmse(history)
