import { useStore } from '../store';

export default function ProgressPage({ navigate }) {
  const { user } = useStore();

  if (!user) {
    return (
      <div className="progress-page">
        <h1>学习进度</h1>
        <p>请先登录查看学习进度</p>
        <button onClick={() => navigate('#/login')} className="btn-primary">去登录</button>
      </div>
    );
  }

  return (
    <div className="progress-page">
      <h1>学习进度</h1>
      <div className="progress-summary">
        <div className="stat-card"><h3>{user.username}</h3><p>当前用户</p></div>
      </div>
    </div>
  );
}
