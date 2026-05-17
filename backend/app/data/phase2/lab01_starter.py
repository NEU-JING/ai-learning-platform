import numpy as np


def generate_data(n=100, noise_std=2.0, seed=42):
    """Generate synthetic data: y = 3x + 5 + noise"""
    rng = np.random.RandomState(seed)
    x = rng.uniform(0, 10, n)
    y = 3 * x + 5 + rng.normal(0, noise_std, n)
    return x, y


def add_intercept(X):
    """Add a column of ones for the intercept term."""
    return np.column_stack([np.ones(X.shape[0]), X])


def normal_equation(X, y):
    """Solve linear regression using the closed-form solution.

    Args:
        X: Feature matrix with intercept column (n, 2)
        y: Target vector (n,)

    Returns:
        weights: (2,) array of [intercept, slope]
    """
    # TODO: Implement normal equation w = (X^T X)^{-1} X^T y


def gradient_descent(X, y, lr=0.01, n_iters=1000):
    """Solve linear regression using batch gradient descent.

    Args:
        X: Feature matrix with intercept column (n, 2)
        y: Target vector (n,)
        lr: Learning rate
        n_iters: Number of iterations

    Returns:
        weights: (2,) array of [intercept, slope]
    """
    # TODO: Implement gradient descent
    # Hint: Initialize weights to zeros
    # Hint: Gradient = 2/n * X^T @ (X @ w - y)


def predict(X, weights):
    """Make predictions using learned weights."""
    return X @ weights


def r2_score(y_true, y_pred):
    """Calculate R-squared score.

    R^2 = 1 - SS_res / SS_tot
    """
    # TODO: Implement R² calculation


def main():
    """Run the full linear regression pipeline."""
    x, y = generate_data()
    X = add_intercept(x)

    # Part 2: Normal Equation
    w_ne = normal_equation(X, y)
    print(f"Normal Equation: intercept={w_ne[0]:.4f}, slope={w_ne[1]:.4f}")

    # Part 3: Gradient Descent
    w_gd = gradient_descent(X, y)
    print(f"Gradient Descent: intercept={w_gd[0]:.4f}, slope={w_gd[1]:.4f}")

    # Part 4: Evaluation
    y_pred_ne = predict(X, w_ne)
    y_pred_gd = predict(X, w_gd)

    r2_ne = r2_score(y, y_pred_ne)
    r2_gd = r2_score(y, y_pred_gd)

    print(f"R² (Normal Equation): {r2_ne:.4f}")
    print(f"R² (Gradient Descent): {r2_gd:.4f}")


if __name__ == "__main__":
    main()
