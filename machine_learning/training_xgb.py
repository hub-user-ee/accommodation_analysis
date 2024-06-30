"""
Training Machine Learning Model with XGBoost.

Authors: Elias Eschenauer, Tamara Weilharter
Version: 2024/06
"""

# --------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------
import joblib
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from machine_learning.model_xgb import find_hyperparams, xgboost


# --------------------------------------------------------------------
# Function definition
# --------------------------------------------------------------------

def train_and_evaluate_model(save_model=True):
    # Load data
    data = pd.read_csv('machine_learning_data_clean.csv')

    # Split data into features and labels
    features = data.drop('price', axis=1)
    labels = data['price']

    # Split data into training and test sets
    features_train, features_test, labels_train, labels_test = train_test_split(features, labels, test_size=0.2, random_state=42)

    train_data = (features_train, labels_train)     # 80%
    test_data = (features_test, labels_test)        # 20%

    # Find best hyperparameters
    space = find_hyperparams(train_data, test_data)

    # Create and evaluate model
    model_final, rmse, data_gain, data_weight, pred, results = xgboost(train_data, test_data, space)

    # Print results
    print(f'Root Mean Squared Error: {rmse}')
    print(f'Feature Importance (Gain):\n{data_gain}')
    print(f'Feature Importance (Weight):\n{data_weight}\n')

    # Print first 20 predictions and corresponding test data
    for i in range(20):
        print(f"Prediction: {pred[i]}, Test data: {test_data[1].iloc[i]}")

    # Define x_axis length
    x_axis = range(len(results['validation_0']['rmse']))

    # Plot the learning curve
    plt.figure(figsize=(12, 6))
    plt.plot(x_axis, results['validation_0']['rmse'], label='Train')
    plt.plot(x_axis, results['validation_1']['rmse'], label='Test')
    plt.xlabel('Epochs')
    plt.ylabel('RMSE')
    plt.title('XGBoost Learning Curve')
    plt.legend()
    plt.grid(True)
    plt.show()

    # Save the trained model to a file
    if save_model:
        try:
            joblib.dump(model_final, 'xgboost_model.pkl')
            print("Trained model saved successfully.")
        except Exception as e:
            print(f"Error saving model: {str(e)}")

    return model_final


if __name__ == "__main__":
    model_final = train_and_evaluate_model()
