import os  # noqa: E402
import sys  # noqa: E402

import numpy as np  # noqa: E402

# Add starter code directory to path
sys.path.insert(0, os.path.dirname(__file__))
import lab01_starter as student  # noqa: E402


def test_generate_data():
    """Data generation should produce correct shapes."""
    x, y = student.generate_data(n=50)
    assert x.shape == (50,), f"Expected x shape (50,), got {x.shape}"
    assert y.shape == (50,), f"Expected y shape (50,), got {y.shape}"


def test_add_intercept():
    """Intercept column should be all ones."""
    X = np.array([[1.0], [2.0], [3.0]])
    result = student.add_intercept(X)
    assert result.shape == (3, 2), f"Expected shape (3, 2), got {result.shape}"
    assert np.allclose(result[:, 0], 1.0), "Intercept column should be all ones"


def test_normal_equation():
    """Normal equation should recover true parameters (intercept≈5, slope≈3)."""
    x, y = student.generate_data(n=200, noise_std=1.0)
    X = student.add_intercept(x)
    w = student.normal_equation(X, y)

    assert w is not None, "normal_equation returned None — not implemented?"
    assert w.shape == (2,), f"Expected shape (2,), got {w.shape}"
    assert abs(w[0] - 5.0) < 1.0, f"Intercept {w[0]:.2f} too far from 5.0"
    assert abs(w[1] - 3.0) < 0.5, f"Slope {w[1]:.2f} too far from 3.0"


def test_gradient_descent():
    """Gradient descent should converge close to normal equation solution."""
    x, y = student.generate_data(n=200, noise_std=1.0)
    X = student.add_intercept(x)

    w_ne = student.normal_equation(X, y)
    w_gd = student.gradient_descent(X, y, lr=0.001, n_iters=10000)

    assert w_gd is not None, "gradient_descent returned None — not implemented?"
    assert w_gd.shape == (2,), f"Expected shape (2,), got {w_gd.shape}"
    assert abs(w_gd[0] - w_ne[0]) < 0.5, f"GD intercept {w_gd[0]:.2f} vs NE {w_ne[0]:.2f}"
    assert abs(w_gd[1] - w_ne[1]) < 0.5, f"GD slope {w_gd[1]:.2f} vs NE {w_ne[1]:.2f}"


def test_predict():
    """Predictions should have correct shape."""
    x, y = student.generate_data(n=50)
    X = student.add_intercept(x)
    w = student.normal_equation(X, y)
    y_pred = student.predict(X, w)

    assert y_pred.shape == (50,), f"Expected shape (50,), got {y_pred.shape}"


def test_r2_score():
    """R² of perfect predictions should be 1.0."""
    y_true = np.array([1.0, 2.0, 3.0, 4.0])
    y_pred = np.array([1.0, 2.0, 3.0, 4.0])
    r2 = student.r2_score(y_true, y_pred)
    assert abs(r2 - 1.0) < 1e-10, f"Perfect prediction R² should be 1.0, got {r2}"

    # R² of mean prediction should be 0.0
    y_mean = np.full_like(y_true, y_true.mean())
    r2_mean = student.r2_score(y_true, y_mean)
    assert abs(r2_mean) < 1e-10, f"Mean prediction R² should be 0.0, got {r2_mean}"


def test_r2_on_regression():
    """R² on actual regression should be positive."""
    x, y = student.generate_data(n=200, noise_std=1.0)
    X = student.add_intercept(x)
    w = student.normal_equation(X, y)
    y_pred = student.predict(X, w)
    r2 = student.r2_score(y, y_pred)

    assert r2 > 0.8, f"R² should be >0.8 for clean data, got {r2:.4f}"


if __name__ == "__main__":
    test_generate_data()
    test_add_intercept()
    test_normal_equation()
    test_gradient_descent()
    test_predict()
    test_r2_score()
    test_r2_on_regression()
    print("All tests passed!")
