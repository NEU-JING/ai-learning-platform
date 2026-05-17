import numpy as np


def generate_data(n=200, n_useful=20, n_noise=30, noise_std=1.0, seed=42):
    """Generate data with useful + noise features."""
    rng = np.random.RandomState(seed)
    n_features = n_useful + n_noise
    X = rng.randn(n, n_features)

    true_w = np.zeros(n_features)
    true_w[:n_useful] = rng.randn(n_useful)

    y = X @ true_w + rng.normal(0, noise_std, n)
    return X, y, true_w, n_useful


def add_intercept(X):
    """Add intercept column as the first column."""
    return np.column_stack([np.ones(X.shape[0]), X])


def mse_loss(X, y, w):
    """Compute MSE loss."""
    return np.mean((X @ w - y) ** 2)


def gradient_descent(X, y, lr=0.001, n_iters=5000):
    """Vanilla gradient descent without regularization.

    Args:
        X: Feature matrix with intercept column (n, d+1)
        y: Target vector (n,)
        lr: Learning rate
        n_iters: Number of iterations

    Returns:
        weights: (d+1,) array
    """
    # TODO: Implement gradient descent
    # Hint: grad = 2/n * X^T @ (X @ w - y)


def gradient_descent_l2(X, y, lr=0.001, n_iters=5000, alpha=0.1):
    """Gradient descent with L2 regularization (Ridge).

    Loss = MSE + alpha * ||w[1:]||^2  (bias excluded from regularization)

    Args:
        X: Feature matrix with intercept column (n, d+1)
        y: Target vector (n,)
        lr: Learning rate
        n_iters: Number of iterations
        alpha: Regularization strength

    Returns:
        weights: (d+1,) array
    """
    # TODO: Implement L2 regularized gradient descent
    # Hint: L2 gradient for w[1:] adds 2*alpha*w[1:]
    # Hint: w[0] (intercept) is NOT regularized


def gradient_descent_l1(X, y, lr=0.001, n_iters=5000, alpha=0.1):
    """Gradient descent with L1 regularization (Lasso approximation).

    Loss = MSE + alpha * ||w[1:]||_1  (bias excluded from regularization)

    Args:
        X: Feature matrix with intercept column (n, d+1)
        y: Target vector (n,)
        lr: Learning rate
        n_iters: Number of iterations
        alpha: Regularization strength

    Returns:
        weights: (d+1,) array
    """
    # TODO: Implement L1 regularized gradient descent
    # Hint: L1 subgradient for w[1:] adds alpha * sign(w[1:])
    # Hint: w[0] (intercept) is NOT regularized


def count_nonzero(weights, threshold=1e-4):
    """Count non-zero weights (excluding intercept)."""
    return np.sum(np.abs(weights[1:]) > threshold)


def main():
    """Run the full comparison pipeline."""
    X, y, true_w, n_useful = generate_data()
    X_with_intercept = add_intercept(X)

    # Split into train/test
    n_train = 150
    X_train, X_test = X_with_intercept[:n_train], X_with_intercept[n_train:]
    y_train, y_test = y[:n_train], y[n_train:]

    # Part 2: No regularization
    w_none = gradient_descent(X_train, y_train)

    # Part 3: L2 regularization
    w_l2 = gradient_descent_l2(X_train, y_train, alpha=0.1)

    # Part 4: L1 regularization
    w_l1 = gradient_descent_l1(X_train, y_train, alpha=0.1)

    # Part 5: Comparison
    for name, w in [("NoReg", w_none), ("L2", w_l2), ("L1", w_l1)]:
        train_mse = mse_loss(X_train, y_train, w)
        test_mse = mse_loss(X_test, y_test, w)
        nz = count_nonzero(w)
        print(f"{name:5s}: TrainMSE={train_mse:.4f}, TestMSE={test_mse:.4f}, NonZero={nz}/50")


if __name__ == "__main__":
    main()
