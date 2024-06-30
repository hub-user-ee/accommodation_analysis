"""
Machine Learning model with hyperparameter optimization and training using XGBoost.

Authors: Elias Eschenauer, Tamara Weilharter
Version: 2024/06
"""

# --------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------
import xgboost as xgb
import pandas as pd
from sklearn.metrics import mean_squared_error
from hyperopt import hp, fmin, tpe, Trials, STATUS_OK


# --------------------------------------------------------------------
# Function definition
# --------------------------------------------------------------------

def find_hyperparams(train, test):
    """
    Finds the best hyperparameters for XGBoost using Bayesian optimization.

    Parameters:
        train (tuple): Training data (features, target).
        test (tuple): Validation data (features, target).

    Returns:
        dict: Best hyperparameters.
    """
    # Define hyperparameter space with probability distributions
    space = {
        'gamma': hp.uniform('gamma', 0.001, 0.004),
        'reg_alpha': hp.uniform('reg_alpha', 0.5, 2),
        'reg_lambda': hp.uniform('reg_lambda', 0.1, 0.5),
        'max_depth': hp.quniform("max_depth", 10, 20, 1),
        'n_estimators': hp.quniform('n_estimators', 400, 550, 1),
        'colsample_bytree': hp.uniform('colsample_bytree', 0.1, 0.4),
        'min_child_weight': hp.uniform('min_child_weight', 0.1, 0.4),
        'learning_rate': hp.uniform('learning_rate', 0.001, 0.1),
        'early_stopping_rounds': hp.quniform('early_stopping_rounds', 5, 20, 1)
    }

    def objective(space):
        """
        Objective function to minimize during hyperparameter optimization.

        Parameters:
            space (dict): Hyperparameter values to evaluate.

        Returns:
            dict: Loss and status.
        """
        # Set up XGBoost Regressor with given hyperparameters
        xgb_reg = xgb.XGBRegressor(
            n_estimators=int(space['n_estimators']),
            max_depth=int(space['max_depth']),
            gamma=space['gamma'],
            reg_alpha=space['reg_alpha'],
            min_child_weight=space['min_child_weight'],
            colsample_bytree=space['colsample_bytree'],
            reg_lambda=space['reg_lambda'],
            early_stopping_rounds=int(space['early_stopping_rounds']),
            n_jobs=-1,
            learning_rate=space['learning_rate'],
            tree_method='hist'  # Use CPU
        )

        # Define evaluation dataset
        evaluation = [(train[0], train[1]), (test[0], test[1])]

        # Fit model to training data
        xgb_reg.fit(train[0], train[1], eval_set=evaluation, verbose=False)

        # Make predictions and calculate RMSE
        pred = xgb_reg.predict(test[0])
        rmse = mean_squared_error(test[1], pred, squared=False)

        return {'loss': rmse, 'status': STATUS_OK}

    # Start Bayesian Hyperparameter Optimization with TPE Algorithm
    trials = Trials()
    hyperparams = fmin(fn=objective, space=space, algo=tpe.suggest, max_evals=200, trials=trials)

    # Retrieve best performing hyperparameters
    best_hyperparams = {
        'max_depth': int(hyperparams['max_depth']),
        'reg_alpha': hyperparams['reg_alpha'],
        'gamma': hyperparams['gamma'],
        'seed': 0,
        'reg_lambda': hyperparams['reg_lambda'],
        'n_estimators': int(hyperparams['n_estimators']),
        'learning_rate': hyperparams['learning_rate'],
        'colsample_bytree': hyperparams['colsample_bytree'],
        'min_child_weight': hyperparams['min_child_weight'],
        'early_stopping_rounds': int(hyperparams['early_stopping_rounds']),
    }

    return best_hyperparams


def xgboost(train, test, space):
    """
    Builds and evaluates an XGBoost model.

    Parameters:
        train (tuple): Training data (features, target).
        test (tuple): Test data (features, target).
        space (dict): Hyperparameters for the model.

    Returns:
        tuple: Model, RMSE, feature importance (gain), feature importance (weight), predictions, evaluation results.
    """
    # Set up final XGBoost Regressor with optimized hyperparameters
    xgb_reg = xgb.XGBRegressor(
        n_estimators=space['n_estimators'],
        max_depth=space['max_depth'],
        gamma=space['gamma'],
        reg_alpha=space['reg_alpha'],
        min_child_weight=space['min_child_weight'],
        colsample_bytree=space['colsample_bytree'],
        reg_lambda=space['reg_lambda'],
        early_stopping_rounds=space['early_stopping_rounds'],
        n_jobs=-1,
        learning_rate=space['learning_rate'],
        tree_method='hist'  # Use CPU
    )

    # Define evaluation dataset
    evaluation = [(train[0], train[1]), (test[0], test[1])]

    # Fit model to training data
    model = xgb_reg.fit(train[0], train[1], eval_set=evaluation, verbose=False)

    # Make predictions on test data and calculate RMSE
    pred = xgb_reg.predict(test[0])
    rmse = mean_squared_error(test[1], pred, squared=False)

    # Retrieve feature importance scores
    gain_score = xgb_reg.get_booster().get_score(importance_type='gain')
    weight_score = xgb_reg.get_booster().get_score(importance_type='weight')

    # Create DataFrames for feature importance
    data_gain = pd.DataFrame(list(gain_score.items()), columns=['Feature', 'Score']).sort_values(by='Score', ascending=False)
    data_weight = pd.DataFrame(list(weight_score.items()), columns=['Feature', 'Score']).sort_values(by='Score', ascending=False)

    # Retrieve evaluation results
    eval_results = xgb_reg.evals_result()

    return model, rmse, data_gain, data_weight, pred, eval_results
