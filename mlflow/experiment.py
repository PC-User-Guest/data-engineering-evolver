import os
import pandas as pd
import mlflow
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split


def run_experiment(data_path: str):
    # simple regression on aggregated data
    df = pd.read_parquet(data_path)

    X = df[["revenue"]].values
    y = df[["revenue"]].values  # dummy target

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    with mlflow.start_run():
        model = LinearRegression()
        model.fit(X_train, y_train)
        score = model.score(X_test, y_test)

        mlflow.log_param("model", "LinearRegression")
        mlflow.log_metric("r2", score)
        mlflow.sklearn.log_model(model, "model")

        print(f"Logged model with r2={score}")


if __name__ == "__main__":
    data_path = os.environ.get("MLFLOW_DATA", "data/output_parquet")
    run_experiment(data_path)
