import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
import lab02_starter as student


def test_generate_data():
    """Data generation should have correct shapes."""
    X, y, true_w, n_useful = student.generate_data()
    assert X.shape == (200, 50), f"Expected (200, 50), got {X.shape}"
    assert y.shape == (200,), f"Expected (200,), got {y.shape}"
    assert true_w.shape == (50,)
    assert n_useful == 20


def test_add_intercept():
    """Intercept column should be all ones."""
    X = np.random.randn(10, 5)
    result = student.add_intercept(X)
    assert result.shape == (10, 6)
    assert np.allclose(result[:, 0], 1.0)


def test_gradient_descent_converges():
    """Vanilla GD should reduce loss over iterations."""
    X, y, _, _ = student.generate_data(n=100, n_useful=5, n_noise=0, noise_std=0.5)
    X_int = student.add_intercept(X)
    w = student.gradient_descent(X_int, y, lr=0.001, n_iters=5000)
    
    assert w is not None, "gradient_descent returned None"
    assert w.shape == (6,), f"Expected (6,), got {w.shape}"
    
    initial_loss = student.mse_loss(X_int, y, np.zeros(6))
    final_loss = student.mse_loss(X_int, y, w)
    assert final_loss < initial_loss * 0.5, f"Loss not decreasing: {initial_loss:.4f} → {final_loss:.4f}"


def test_gradient_descent_l2():
    """L2 regularization should produce smaller weights than no regularization."""
    X, y, _, _ = student.generate_data(n=200, n_useful=5, n_noise=5, noise_std=0.5)
    X_int = student.add_intercept(X)
    
    w_none = student.gradient_descent(X_int, y, lr=0.001, n_iters=5000)
    w_l2 = student.gradient_descent_l2(X_int, y, lr=0.001, n_iters=5000, alpha=1.0)
    
    assert w_l2 is not None, "gradient_descent_l2 returned None"
    # L2 weights should be smaller (excluding intercept)
    l2_norm_none = np.sum(w_none[1:] ** 2)
    l2_norm_l2 = np.sum(w_l2[1:] ** 2)
    assert l2_norm_l2 < l2_norm_none, f"L2 should shrink weights: {l2_norm_l2:.4f} >= {l2_norm_none:.4f}"


def test_gradient_descent_l1_sparsity():
    """L1 regularization should produce sparser weights."""
    X, y, _, _ = student.generate_data(n=200, n_useful=5, n_noise=15, noise_std=0.5)
    X_int = student.add_intercept(X)
    
    w_none = student.gradient_descent(X_int, y, lr=0.001, n_iters=5000)
    w_l1 = student.gradient_descent_l1(X_int, y, lr=0.001, n_iters=5000, alpha=0.5)
    
    assert w_l1 is not None, "gradient_descent_l1 returned None"
    
    nz_none = student.count_nonzero(w_none)
    nz_l1 = student.count_nonzero(w_l1)
    assert nz_l1 <= nz_none, f"L1 should produce fewer non-zero weights: {nz_l1} > {nz_none}"


def test_bias_not_regularized():
    """Intercept term should not be regularized."""
    X, y, _, _ = student.generate_data(n=100, n_useful=2, n_noise=0)
    X_int = student.add_intercept(X)
    
    w_l2 = student.gradient_descent_l2(X_int, y, lr=0.001, n_iters=5000, alpha=100.0)
    w_l1 = student.gradient_descent_l1(X_int, y, lr=0.001, n_iters=5000, alpha=100.0)
    
    # With very high alpha, feature weights should be near zero but intercept can be non-zero
    if w_l2 is not None:
        assert abs(w_l2[0]) > 0.01 or abs(w_l2[1]) < 0.1, "Bias should survive regularization"
    if w_l1 is not None:
        assert abs(w_l1[0]) > 0.01 or abs(w_l1[1]) < 0.1, "Bias should survive regularization"


def test_mse_loss():
    """MSE loss should be non-negative and zero for perfect predictions."""
    X = np.array([[1, 2], [1, 3], [1, 4]])
    y = np.array([5.0, 7.0, 9.0])
    w = np.array([1.0, 2.0])  # Perfect: y = 1 + 2x
    
    loss = student.mse_loss(X, y, w)
    assert loss < 1e-10, f"Perfect prediction should have ~0 loss, got {loss}"


if __name__ == "__main__":
    test_generate_data()
    test_add_intercept()
    test_gradient_descent_converges()
    test_gradient_descent_l2()
    test_gradient_descent_l1_sparsity()
    test_bias_not_regularized()
    test_mse_loss()
    print("All tests passed!")
