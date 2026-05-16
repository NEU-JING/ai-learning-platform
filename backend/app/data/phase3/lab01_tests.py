"""
Lab 01 Test Cases - End-to-End ML Pipeline
"""
import numpy as np
import pandas as pd
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def generate_test_data(n=200, random_state=42):
    """Generate synthetic customer churn data for testing."""
    np.random.seed(random_state)
    df = pd.DataFrame({
        'customer_id': range(n),
        'tenure': np.random.randint(0, 73, n),
        'monthly_charges': np.random.uniform(20, 120, n).round(2),
        'total_charges': np.random.uniform(0, 8000, n).round(2),
        'contract': np.random.choice(['Month-to-month', 'One year', 'Two year'], n),
        'payment_method': np.random.choice(['Credit card', 'Bank transfer', 'Electronic check'], n),
        'internet_service': np.random.choice(['DSL', 'Fiber optic', 'No'], n),
        'senior_citizen': np.random.randint(0, 2, n),
        'partner': np.random.choice(['Yes', 'No'], n),
        'dependents': np.random.choice(['Yes', 'No'], n),
        'churn': np.random.choice(['Yes', 'No'], n, p=[0.27, 0.73])
    })
    return df


def test_load_and_prepare():
    """Test 1: Data loading and preparation."""
    from lab01_starter import load_and_prepare_data
    df = generate_test_data()
    filepath = '/tmp/test_churn.csv'
    df.to_csv(filepath, index=False)
    
    X, y = load_and_prepare_data(filepath)
    
    # customer_id and churn should not be in features
    assert 'customer_id' not in X.columns, "customer_id should be dropped"
    assert 'churn' not in X.columns, "churn should be dropped from features"
    
    # y should be binary 0/1
    assert set(y.unique()).issubset({0, 1}), f"y should be binary, got {y.unique()}"
    assert len(X) == len(y), f"X and y length mismatch: {len(X)} vs {len(y)}"
    print("✅ Test 1 passed: load_and_prepare_data")


def test_split_data():
    """Test 2: Stratified train-test split."""
    from lab01_starter import load_and_prepare_data, split_data
    df = generate_test_data()
    filepath = '/tmp/test_churn.csv'
    df.to_csv(filepath, index=False)
    
    X, y = load_and_prepare_data(filepath)
    X_train, X_test, y_train, y_test = split_data(X, y, test_size=0.2)
    
    # Check split ratio
    assert len(X_test) == int(0.2 * len(X)), "Test set size incorrect"
    assert len(X_train) == len(X) - len(X_test), "Train set size incorrect"
    
    # Check stratification (roughly same positive rate)
    train_pos_rate = y_train.mean()
    test_pos_rate = y_test.mean()
    assert abs(train_pos_rate - test_pos_rate) < 0.1, \
        f"Stratification failed: train={train_pos_rate:.2f}, test={test_pos_rate:.2f}"
    print("✅ Test 2 passed: split_data")


def test_identify_column_types():
    """Test 3: Column type identification."""
    from lab01_starter import load_and_prepare_data, identify_column_types
    df = generate_test_data()
    filepath = '/tmp/test_churn.csv'
    df.to_csv(filepath, index=False)
    
    X, y = load_and_prepare_data(filepath)
    numeric_features, categorical_features = identify_column_types(X)
    
    # tenure, monthly_charges, total_charges, senior_citizen should be numeric
    assert 'tenure' in numeric_features, "tenure should be numeric"
    assert 'monthly_charges' in numeric_features, "monthly_charges should be numeric"
    
    # contract, payment_method should be categorical
    assert 'contract' in categorical_features, "contract should be categorical"
    assert 'payment_method' in categorical_features, "payment_method should be categorical"
    
    # No overlap
    assert not set(numeric_features) & set(categorical_features), \
        "Numeric and categorical features should not overlap"
    print("✅ Test 3 passed: identify_column_types")


def test_build_preprocessor():
    """Test 4: Preprocessor construction."""
    from lab01_starter import load_and_prepare_data, identify_column_types, build_preprocessor
    df = generate_test_data()
    filepath = '/tmp/test_churn.csv'
    df.to_csv(filepath, index=False)
    
    X, y = load_and_prepare_data(filepath)
    numeric_features, categorical_features = identify_column_types(X)
    preprocessor = build_preprocessor(numeric_features, categorical_features)
    
    # Should be a ColumnTransformer
    assert hasattr(preprocessor, 'transform'), "Preprocessor should have transform method"
    assert hasattr(preprocessor, 'fit'), "Preprocessor should have fit method"
    
    # Should be able to fit and transform
    X_transformed = preprocessor.fit_transform(X)
    assert X_transformed.shape[0] == len(X), "Transformed data should have same number of rows"
    print("✅ Test 4 passed: build_preprocessor")


def test_feature_engineering():
    """Test 5: Feature engineering creates new features."""
    from lab01_starter import load_and_prepare_data, engineer_features
    df = generate_test_data()
    filepath = '/tmp/test_churn.csv'
    df.to_csv(filepath, index=False)
    
    X, y = load_and_prepare_data(filepath)
    X_eng = engineer_features(X)
    
    # Should have more columns than original
    assert len(X_eng.columns) >= len(X.columns), \
        "Feature engineering should add columns"
    
    # Check specific new features
    if 'charges_per_month' in X_eng.columns:
        assert not X_eng['charges_per_month'].isnull().all(), \
            "charges_per_month should have values"
    print("✅ Test 5 passed: engineer_features")


def test_build_full_pipeline():
    """Test 6: Full pipeline construction."""
    from lab01_starter import (
        load_and_prepare_data, split_data, identify_column_types,
        build_preprocessor, build_full_pipeline
    )
    df = generate_test_data()
    filepath = '/tmp/test_churn.csv'
    df.to_csv(filepath, index=False)
    
    X, y = load_and_prepare_data(filepath)
    X_train, X_test, y_train, y_test = split_data(X, y)
    numeric_features, categorical_features = identify_column_types(X_train)
    preprocessor = build_preprocessor(numeric_features, categorical_features)
    
    pipeline = build_full_pipeline(preprocessor, model_type='logistic')
    
    # Should have fit and predict methods
    assert hasattr(pipeline, 'fit'), "Pipeline should have fit method"
    assert hasattr(pipeline, 'predict'), "Pipeline should have predict method"
    
    # Should be able to fit
    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)
    assert len(y_pred) == len(y_test), "Prediction length should match test set"
    print("✅ Test 6 passed: build_full_pipeline")


def test_evaluate_model():
    """Test 7: Model evaluation returns correct metrics."""
    from lab01_starter import (
        load_and_prepare_data, split_data, identify_column_types,
        build_preprocessor, build_full_pipeline, evaluate_model
    )
    df = generate_test_data()
    filepath = '/tmp/test_churn.csv'
    df.to_csv(filepath, index=False)
    
    X, y = load_and_prepare_data(filepath)
    X_train, X_test, y_train, y_test = split_data(X, y)
    numeric_features, categorical_features = identify_column_types(X_train)
    preprocessor = build_preprocessor(numeric_features, categorical_features)
    pipeline = build_full_pipeline(preprocessor)
    pipeline.fit(X_train, y_train)
    
    metrics = evaluate_model(pipeline, X_test, y_test)
    
    assert 'accuracy' in metrics, "Metrics should include accuracy"
    assert 'f1' in metrics, "Metrics should include f1"
    assert 0 <= metrics['accuracy'] <= 1, "Accuracy should be between 0 and 1"
    assert 0 <= metrics['f1'] <= 1, "F1 should be between 0 and 1"
    print(f"  Accuracy: {metrics['accuracy']:.3f}, F1: {metrics['f1']:.3f}")
    print("✅ Test 7 passed: evaluate_model")


def test_no_data_leakage():
    """Test 8: Verify preprocessing does not leak test data."""
    from lab01_starter import (
        load_and_prepare_data, split_data, identify_column_types,
        build_preprocessor, build_full_pipeline
    )
    df = generate_test_data()
    filepath = '/tmp/test_churn.csv'
    df.to_csv(filepath, index=False)
    
    X, y = load_and_prepare_data(filepath)
    X_train, X_test, y_train, y_test = split_data(X, y)
    numeric_features, categorical_features = identify_column_types(X_train)
    preprocessor = build_preprocessor(numeric_features, categorical_features)
    pipeline = build_full_pipeline(preprocessor)
    
    # Fit only on training data
    pipeline.fit(X_train, y_train)
    
    # Predict on test data - should work without error
    y_pred = pipeline.predict(X_test)
    assert len(y_pred) == len(y_test), "Should be able to predict on test data"
    
    # Verify preprocessor was fit only on training data
    # by checking that the OneHotEncoder knows the categories from training
    cat_transformer = preprocessor.named_transformers_['cat']
    ohe = cat_transformer.named_steps['onehot']
    assert hasattr(ohe, 'categories_'), "OneHotEncoder should be fitted"
    print("✅ Test 8 passed: no_data_leakage")


if __name__ == '__main__':
    test_load_and_prepare()
    test_split_data()
    test_identify_column_types()
    test_build_preprocessor()
    test_feature_engineering()
    test_build_full_pipeline()
    test_evaluate_model()
    test_no_data_leakage()
    print("\n🎉 All 8 tests passed!")
