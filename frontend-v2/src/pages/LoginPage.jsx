import { useState } from 'react';
import { useStore } from '../store';

export default function LoginPage({ navigate }) {
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { login, register } = useStore();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      if (isRegister) {
        await register(email, username, password);
      } else {
        await login(email, password);
      }
      navigate('#/courses');
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="login-page">
      <h1>{isRegister ? '注册' : '登录'}</h1>
      <form onSubmit={handleSubmit}>
        <input type="email" placeholder="邮箱" value={email} onChange={(e) => setEmail(e.target.value)} required />
        {isRegister && <input type="text" placeholder="用户名" value={username} onChange={(e) => setUsername(e.target.value)} required />}
        <input type="password" placeholder="密码" value={password} onChange={(e) => setPassword(e.target.value)} required />
        {error && <p className="error">{error}</p>}
        <button type="submit" className="btn-primary">{isRegister ? '注册' : '登录'}</button>
      </form>
      <p onClick={() => { setIsRegister(!isRegister); setError(''); }} className="toggle-auth">
        {isRegister ? '已有账号？去登录' : '没有账号？去注册'}
      </p>
    </div>
  );
}
