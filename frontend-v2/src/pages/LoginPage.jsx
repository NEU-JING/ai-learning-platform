/* Login page — production-ready user authentication */
import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Icon } from '../icons';
import { loginUser } from '../data';

const LoginPage = ({ onLogin }) => {
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.email || !form.password) {
      setError('请填写邮箱和密码');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const res = await loginUser({
        email: form.email,
        password: form.password,
      });

      onLogin?.({ isLoggedIn: true, user: res.user });
      navigate('/');
    } catch (err) {
      setError(err.message || '登录失败，请检查邮箱和密码');
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
            <h2 style={{ fontSize: 24, fontWeight: 600 }}>欢迎回来</h2>
            <p style={{ color: 'var(--fg-2)', marginTop: 8 }}>登录以继续你的学习进度</p>
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
                邮箱
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
                密码
              </label>
              <input
                type="password"
                name="password"
                value={form.password}
                onChange={handleChange}
                placeholder="输入密码"
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
              {loading ? '登录中...' : '登录'}
            </button>
          </form>

          <div style={{ textAlign: 'center', marginTop: 24, color: 'var(--fg-2)', fontSize: 14 }}>
            还没有账号？<Link to="/register" style={{ color: 'var(--brand)', textDecoration: 'none' }}>立即注册</Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
