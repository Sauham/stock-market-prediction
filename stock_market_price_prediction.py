# -*- coding: utf-8 -*-
"""Stock market price prediction.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1MNchalnSZ9OZDiRW_hXj0tqIB3-wCwDC
"""

!pip install yfinance
!pip install statsmodels

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import mean_squared_error, mean_absolute_error

# List of stock tickers
tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']

# Download historical data
data = yf.download(tickers, start="2020-01-01", end="2023-01-01", group_by='ticker')

# Check for missing values
print(data.isnull().sum())

# Forward fill or drop missing values
data = data.ffill().dropna()

# Ensure the data is indexed by date
data.index = pd.to_datetime(data.index)

data.to_csv('cleaned_stock_data.csv')

for ticker in tickers:
    plt.figure(figsize=(10, 5))
    plt.plot(data[ticker]['Close'], label=ticker)
    plt.title(f'{ticker} Closing Prices')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.show()

from statsmodels.tsa.seasonal import seasonal_decompose

# Decompose time series for one stock
decomposition = seasonal_decompose(data['AAPL']['Close'], period=30)
decomposition.plot()
plt.show()

# Create lagged variables
for lag in range(1, 6):
    data['AAPL'][f'Close_Lag_{lag}'] = data['AAPL']['Close'].shift(lag)

# Calculate rolling statistics
data['AAPL']['Rolling_Mean_7'] = data['AAPL']['Close'].rolling(window=7).mean()
data['AAPL']['Rolling_Std_7'] = data['AAPL']['Close'].rolling(window=7).std()

# Compute percentage changes
data['AAPL']['Daily_Return'] = data['AAPL']['Close'].pct_change()

# Drop rows with NaN values (created by lagging and rolling operations)
data['AAPL'] = data['AAPL'].dropna()

for lag in range(1, 6):
    data['AAPL'][f'Close_Lag_{lag}'] = data['AAPL']['Close'].shift(lag)

data['AAPL']['Rolling_Mean_7'] = data['AAPL']['Close'].rolling(window=7).mean()
data['AAPL']['Rolling_Std_7'] = data['AAPL']['Close'].rolling(window=7).std()

data['AAPL']['Daily_Return'] = data['AAPL']['Close'].pct_change()

# Plot ACF and PACF
plot_acf(data['AAPL']['Close'].dropna())
plot_pacf(data['AAPL']['Close'].dropna())
plt.show()

# Fit ARIMA model
model = ARIMA(data['AAPL']['Close'], order=(5, 1, 0))
results = model.fit()
print(results.summary())

# Forecast future prices
forecast = results.forecast(steps=30)
print(forecast)

print(data['AAPL'].columns)

print(data.columns)

# Extract data for AAPL
aapl_data = data['AAPL'].copy()
print(aapl_data.columns)

# Create lagged variables
for lag in range(1, 6):
    aapl_data[f'Close_Lag_{lag}'] = aapl_data['Close'].shift(lag)

# Calculate rolling statistics
aapl_data['Rolling_Mean_7'] = aapl_data['Close'].rolling(window=7).mean()
aapl_data['Rolling_Std_7'] = aapl_data['Close'].rolling(window=7).std()

# Compute percentage changes
aapl_data['Daily_Return'] = aapl_data['Close'].pct_change()

# Drop rows with NaN values (created by lagging and rolling operations)
aapl_data = aapl_data.dropna()

# Verify the new columns
print(aapl_data.columns)

# Prepare features and target
X = aapl_data[['Close_Lag_1', 'Close_Lag_2', 'Rolling_Mean_7', 'Daily_Return']]
y = aapl_data['Close'].shift(-1)  # Shift target variable to predict the next day's closing price

# Drop rows with NaN values in X
X = X.dropna()

# Align y with the remaining rows of X
y = y.loc[X.index]

# Check shapes
print(X.shape, y.shape)  # Should be the same

print(X.isnull().sum())  # Check for NaN in features
print(y.isnull().sum())  # Check for NaN in target

y = y.dropna()
X = X.loc[y.index]

print(X.isnull().sum())
print(y.isnull().sum())

# Grid search for hyperparameter tuning
param_grid = {
    'n_estimators': [100, 200],
    'learning_rate': [0.01, 0.1],
    'max_depth': [3, 5]
}
gb = GradientBoostingRegressor()
grid_search = GridSearchCV(gb, param_grid, cv=3)
grid_search.fit(X, y)
print(grid_search.best_params_)

# Train the final model with the best hyperparameters
final_model = GradientBoostingRegressor(
    learning_rate=0.1,
    max_depth=5,
    n_estimators=200
)

# Fit the model on the entire dataset
final_model.fit(X, y)

from sklearn.model_selection import train_test_split

# Split the data into training and testing sets (80% train, 20% test)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the model on the training set
final_model.fit(X_train, y_train)

# Predict on the test set
y_pred = final_model.predict(X_test)

!pip install --upgrade scikit-learn

from sklearn.metrics import mean_squared_error

# Calculate MSE
mse = mean_squared_error(y_test, y_pred)

import numpy as np

# Calculate RMSE
rmse = np.sqrt(mse)

from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import numpy as np

# Calculate evaluation metrics
mse = mean_squared_error(y_test, y_pred)  # Calculate MSE
rmse = np.sqrt(mse)  # Calculate RMSE
mae = mean_absolute_error(y_test, y_pred)  # Calculate MAE
r2 = r2_score(y_test, y_pred)  # Calculate R²

print(f"RMSE: {rmse}")
print(f"MAE: {mae}")
print(f"R²: {r2}")

# Plot actual vs predicted values
plt.figure(figsize=(10, 6))
plt.plot(y_test.values, label="Actual")
plt.plot(y_pred, label="Predicted")
plt.title("Actual vs Predicted Stock Prices")
plt.xlabel("Time")
plt.ylabel("Price")
plt.legend()
plt.show()

# Plot feature importances
importances = final_model.feature_importances_
plt.figure(figsize=(10, 6))
plt.bar(X.columns, importances)
plt.title("Feature Importances")
plt.xlabel("Features")
plt.ylabel("Importance")
plt.show()

#

# Save the model
import joblib  # Import joblib for saving the model

# Save the model to a file
joblib.dump(final_model, "gradient_boosting_stock_model.pkl")

# Load the model from the file
loaded_model = joblib.load("gradient_boosting_stock_model.pkl")

# Use the loaded model to make predictions
predictions = loaded_model.predict(X_test)

