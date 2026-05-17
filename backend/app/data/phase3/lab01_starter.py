"""
Lab 01 - End-to-End ML Pipeline: From CSV to Prediction
Customer Churn Prediction for a Telecom Company

Complete the TODO sections to build a full ML pipeline.
Target: F1 score >= 0.60
"""

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


def load_and_prepare_data(filepath="customer_churn.csv"):
    """
    Load CSV data and perform initial preparation.

    Returns:
        X: Feature DataFrame
        y: Target Series (0/1 encoded)
    """
    # TODO: Load data from CSV
    df = pd.read_csv(filepath)

    # TODO: Encode target variable (Yes->1, No->0)
    y = (df["churn"] == "Yes").astype(int)

    # TODO: Drop non-feature columns (customer_id, churn)
    drop_cols = ["customer_id", "churn"]
    X = df.drop(columns=drop_cols, errors="ignore")

    # TODO: Fix total_charges (may have whitespace strings)
    if "total_charges" in X.columns:
        X["total_charges"] = pd.to_numeric(X["total_charges"], errors="coerce")

    return X, y


def split_data(X, y, test_size=0.2, random_state=42):
    """
    Split data into train and test sets with stratification.

    Returns:
        X_train, X_test, y_train, y_test
    """
    # TODO: Implement stratified train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    return X_train, X_test, y_train, y_test


def identify_column_types(X):
    """
    Identify numeric and categorical columns.

    Returns:
        numeric_features: list of numeric column names
        categorical_features: list of categorical column names
    """
    # TODO: Identify numeric and categorical columns
    numeric_features = X.select_dtypes(include=[np.number]).columns.tolist()
    categorical_features = X.select_dtypes(include=["object", "category"]).columns.tolist()
    return numeric_features, categorical_features


def build_preprocessor(numeric_features, categorical_features):
    """
    Build a ColumnTransformer for preprocessing.

    Numeric pipeline: impute median + standard scale
    Categorical pipeline: impute most_frequent + one-hot encode

    Returns:
        preprocessor: ColumnTransformer
    """
    # TODO: Build numeric transformer pipeline
    numeric_transformer = Pipeline(
        [("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())]
    )

    # TODO: Build categorical transformer pipeline
    categorical_transformer = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]
    )

    # TODO: Combine into ColumnTransformer
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, numeric_features),
            ("cat", categorical_transformer, categorical_features),
        ]
    )

    return preprocessor


def engineer_features(X):
    """
    Create new features from existing ones.

    Returns:
        X: DataFrame with new features
    """
    X = X.copy()

    # TODO: Create feature: charges_per_month (total_charges / tenure)
    # Handle division by zero (tenure=0)
    if "total_charges" in X.columns and "tenure" in X.columns:
        X["charges_per_month"] = np.where(
            X["tenure"] > 0,
            X["total_charges"] / X["tenure"],
            X["monthly_charges"] if "monthly_charges" in X.columns else 0,
        )

    # TODO: Create feature: tenure_group (binned tenure)
    if "tenure" in X.columns:
        X["tenure_group"] = pd.cut(
            X["tenure"],
            bins=[0, 12, 24, 48, 72, float("inf")],
            labels=["0-12", "12-24", "24-48", "48-72", "72+"],
        )

    return X


def build_full_pipeline(preprocessor, model_type="logistic"):
    """
    Build complete pipeline: preprocessing + model.

    Args:
        preprocessor: ColumnTransformer
        model_type: 'logistic' or 'random_forest'

    Returns:
        pipeline: full sklearn Pipeline
    """
    # TODO: Select model based on model_type
    if model_type == "logistic":
        model = LogisticRegression(max_iter=1000, random_state=42, class_weight="balanced")
    else:
        model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced")

    # TODO: Build full pipeline
    pipeline = Pipeline([("preprocessor", preprocessor), ("classifier", model)])

    return pipeline


def evaluate_model(pipeline, X_test, y_test):
    """
    Evaluate model and return metrics.

    Returns:
        dict with accuracy, f1_score, and classification_report
    """
    # TODO: Make predictions
    y_pred = pipeline.predict(X_test)

    # TODO: Calculate metrics
    metrics = {
        "accuracy": accuracy_score(y_test, y_pred),
        "f1": f1_score(y_test, y_pred),
        "report": classification_report(y_test, y_pred),
    }

    return metrics


def run_pipeline(filepath="customer_churn.csv"):
    """
    Run the complete ML pipeline end-to-end.

    Returns:
        pipeline: trained pipeline
        metrics: evaluation metrics dict
    """
    # Step 1: Load and prepare data
    X, y = load_and_prepare_data(filepath)

    # Step 2: Feature engineering
    X = engineer_features(X)

    # Step 3: Split data
    X_train, X_test, y_train, y_test = split_data(X, y)

    # Step 4: Identify column types
    numeric_features, categorical_features = identify_column_types(X_train)

    # Step 5: Build preprocessor
    preprocessor = build_preprocessor(numeric_features, categorical_features)

    # Step 6: Build and train pipeline
    pipeline = build_full_pipeline(preprocessor, model_type="logistic")
    pipeline.fit(X_train, y_train)

    # Step 7: Evaluate
    metrics = evaluate_model(pipeline, X_test, y_test)

    return pipeline, metrics


if __name__ == "__main__":
    # Generate sample data for testing
    np.random.seed(42)
    n = 500
    df = pd.DataFrame(
        {
            "customer_id": range(n),
            "tenure": np.random.randint(0, 73, n),
            "monthly_charges": np.random.uniform(20, 120, n).round(2),
            "total_charges": np.random.uniform(0, 8000, n).round(2),
            "contract": np.random.choice(["Month-to-month", "One year", "Two year"], n),
            "payment_method": np.random.choice(
                ["Credit card", "Bank transfer", "Electronic check"], n
            ),
            "internet_service": np.random.choice(["DSL", "Fiber optic", "No"], n),
            "senior_citizen": np.random.randint(0, 2, n),
            "partner": np.random.choice(["Yes", "No"], n),
            "dependents": np.random.choice(["Yes", "No"], n),
            "churn": np.random.choice(["Yes", "No"], n, p=[0.27, 0.73]),
        }
    )
    df.to_csv("customer_churn.csv", index=False)

    pipeline, metrics = run_pipeline()
    print(f"Accuracy: {metrics['accuracy']:.3f}")
    print(f"F1 Score: {metrics['f1']:.3f}")
    print(metrics["report"])
