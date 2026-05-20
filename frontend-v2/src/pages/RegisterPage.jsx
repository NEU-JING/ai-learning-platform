/* Register page — production-ready user registration */
import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Icon } from '../icons';
import { registerUser, loginUser } from '../data';

const RegisterPage = ({ onLogin }) => {
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: '', username: '', password: '', confirmPassword: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
    setError('');
  };

  const validate = () => {
    if (!form.email || !form.username || !form.password) {
      return '请填写所有必填项';
    }
    if (form.password !== form.confirmPassword) {
      return '两次输入的密码不一致';
    }
    if (form.password.length < 8) {
      return '密码长度至少8位';
    }
    if (!/[A-Za-z]/.test(form.password) || !/\d/.test(form.password)) {
      return '密码必须同时包含字母和数字';
    }
    if (form.username.length < 3) {
      return '用户名长度至少3位';
    }
    return null;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const validationError = validate();
    if (validationError) {
      setError(validationError);
      return;
    }

    setLoading(true);
    setError('');

    try {
      // 1. 注册
      await registerUser({
        email: form.email,
        username: form.username,
        password: form.password,
      });

      // 2. 自动登录
      const loginRes = await loginUser({
        email: form.email,
        password: form.password,
      });

      // 3. 更新状态并跳转
      onLogin?.({ isLoggedIn: true, user: loginRes.user });
      navigate('/');
    } catch (err) {
      setError(err.message || '注册失败，请稍后重试');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="screen" style={{ display: 'flex', minHeight: '100vh' }}>
      {/* Left: branding */}
      <div style={{
        flex: 1,
        display: 'none',
        background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
        color: 'white',
        padding: 48,
        flexDirection: 'column',
        justifyContent: 'center',
      }} className="hide-mobile">
        <h1 style={{ fontSize: 40, fontWeight: 700, marginBottom: 16 }}>AILP</h1>
        <p style={{ fontSize: 18, opacity: 0.9, maxWidth: 360 }}>
          系统化 AI 学习平台<br />
          60 章 · 43 实验 · 从 Python 到生产部署
        </p>
      </div>

      {/* Right: form */}
      <div style={{
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        padding: 24,
      }}>
        <div style={{ width: '100%', maxWidth: 400 }}>
          <div style={{ textAlign: 'center', marginBottom: 32 }}>
            <h2 style={{ fontSize: 24, fontWeight: 600 }}>创建账号</h2>
            <p style={{ color: 'var(--fg-2)', marginTop: 8 }}>开始你的 AI 学习之旅</p>
          </div>

          {error && (
            <div style={{
              background: 'rgba(251, 113, 133, 0.1)',
              border: '1px solid rgba(251, 113, 133, 0.3)',
              color: '#fb7185',
              padding: '12px 16px',
              borderRadius: 8,
              marginBottom: 16,
              fontSize: 14,
            }}>
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            <div>
              <label style={{ display: 'block', fontSize: 14, marginBottom: 6, color: 'var(--fg-2)' }}>
                邮箱 <span style={{ color: '#fb7185' }}>*</span>
              </label>
              <input
                type="email"
                name="email"
                value={form.email}
                onChange={handleChange}
                placeholder="your@email.com"
                required
                style={{
                  width: '100%',
                  padding: '12px 16px',
                  border: '1px solid var(--line)',
                  borderRadius: 8,
                  background: 'var(--surface)',
                  color: 'var(--fg)',
                  fontSize: 15,
                }}
              />
            </div>

            <div>
              <label style={{ display: 'block', fontSize: 14, marginBottom: 6, color: 'var(--fg-2)' }}>
                用户名 <span style={{ color: '#fb7185' }}>*</span>
              </label>
              <input
                type="text"
                name="username"
                value={form.username}
                onChange={handleChange}
                placeholder="3-20位，支持中文"
                required
                style={{
                  width: '100%',
                  padding: '12px 16px',
                  border: '1px solid var(--line)',
                  borderRadius: 8,
                  background: 'var(--surface)',
                  color: 'var(--fg)',
                  fontSize: 15,
                }}
              />
            </div>

            <div>
              <label style={{ display: 'block', fontSize: 14, marginBottom: 6, color: 'var(--fg-2)' }}>
                密码 <span style={{ color: '#fb7185' }}>*</span>
              </label>
              <input
                type="password"
                name="password"
                value={form.password}
                onChange={handleChange}
                placeholder="至少8位，包含字母和数字"
                required
                style={{
                  width: '100%',
                  padding: '12px 16px',
                  border: '1px solid var(--line)',
                  borderRadius: 8,
                  background: 'var(--surface)',
                  color: 'var(--fg)',
                  fontSize: 15,
                }}
              />
            </div>

            <div>
              <label style={{ display: 'block', fontSize: 14, marginBottom: 6, color: 'var(--fg-2)' }}>
                确认密码 <span style={{ color: '#fb7185' }}>*</span>
              </label>
              <input
                type="password"
                name="confirmPassword"
                value={form.confirmPassword}
                onChange={handleChange}
                placeholder="再次输入密码"
                required
                style={{
                  width: '100%',
                  padding: '12px 16px',
                  border: '1px solid var(--line)',
                  borderRadius: 8,
                  background: 'var(--surface)',
                  color: 'var(--fg)',
                  fontSize: 15,
                }}
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              style={{
                width: '100%',
                padding: '14px 24px',
                background: loading ? 'var(--surface-3)' : 'var(--brand)',
                color: 'white',
                border: 'none',
                borderRadius: 8,
                fontSize: 15,
                fontWeight: 500,
                cursor: loading ? 'not-allowed' : 'pointer',
                marginTop: 8,
              }}
            >
              {loading ? '注册中...' : '创建账号'}
            </button>
          </form>

          <div style={{ textAlign: 'center', marginTop: 24, color: 'var(--fg-2)', fontSize: 14 }}>
            已有账号？<Link to="/login" style={{ color: 'var(--brand)', textDecoration: 'none' }}>立即登录</Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;
