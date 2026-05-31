/* Skill Radar Page - 10-dimension skill visualization */
import React, { useState, useEffect } from 'react';
import { Icon } from '../icons';
import { useNavigate } from 'react-router-dom';

const RadarPage = () => {
  const navigate = useNavigate();
  const [radarData, setRadarData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchRadarData();
  }, []);

  const fetchRadarData = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('ailp_token');
      const res = await fetch('/api/v1/radar', {
        headers: token ? { 'Authorization': `Bearer ${token}` } : {}
      });
      if (!res.ok) throw new Error(`API ${res.status}`);
      const data = await res.json();
      setRadarData(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('ailp_token');
      const res = await fetch('/api/v1/skills/refresh', {
        method: 'POST',
        headers: token ? { 'Authorization': `Bearer ${token}` } : {}
      });
      if (!res.ok) throw new Error('刷新失败');
      await fetchRadarData();
    } catch (e) {
      setError(e.message);
    }
  };

  if (loading) {
    return (
      <div className="screen container" style={{ paddingTop: 80 }}>
        <div style={{ textAlign: 'center', padding: 60 }}>
          <div className="skeleton" style={{ width: 300, height: 300, margin: '0 auto', borderRadius: '50%' }} />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="screen container" style={{ paddingTop: 80, textAlign: 'center' }}>
        <Icon name="alert" size={48} style={{ color: 'var(--error)', marginBottom: 16 }} />
        <p>加载失败: {error}</p>
        <button className="btn btn-primary" onClick={fetchRadarData} style={{ marginTop: 16 }}>重试</button>
      </div>
    );
  }

  const dimensions = radarData?.dimensions || [];
  const overallScore = radarData?.overall_score || 0;

  // Simple bar chart representation (radar chart can be added later with a library)
  return (
    <div className="screen container" style={{ paddingTop: 24, paddingBottom: 60 }}>
      <div style={{ maxWidth: 800, margin: '0 auto' }}>
        {/* Header */}
        <div style={{ marginBottom: 32 }}>
          <div className="section-h" style={{ marginBottom: 16 }}>
            <div>
              <h1>技能雷达</h1>
              <p className="muted" style={{ marginTop: 4 }}>10维能力评估，发现你的技能缺口</p>
            </div>
            <button className="btn btn-secondary" onClick={handleRefresh}>
              <Icon name="refresh" size={14} /> 刷新数据
            </button>
          </div>
        </div>

        {/* Overall Score */}
        <div style={{
          background: 'var(--surface)',
          border: '1px solid var(--line)',
          borderRadius: 12,
          padding: 24,
          marginBottom: 24,
          textAlign: 'center'
        }}>
          <div style={{ fontSize: 48, fontWeight: 700, color: 'var(--brand)' }}>
            {overallScore.toFixed(1)}
          </div>
          <div style={{ fontSize: 14, color: 'var(--fg-2)', marginTop: 4 }}>综合评分</div>
        </div>

        {/* Dimensions */}
        <div style={{
          background: 'var(--surface)',
          border: '1px solid var(--line)',
          borderRadius: 12,
          padding: 24
        }}>
          <h3 style={{ marginBottom: 16 }}>技能维度</h3>
          {dimensions.length === 0 ? (
            <p className="muted">暂无技能数据，开始学习课程来获取评分</p>
          ) : (
            <div style={{ display: 'grid', gap: 16 }}>
              {dimensions.map((dim, idx) => (
                <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                      <span style={{ fontSize: 14 }}>{dim.name}</span>
                      <span style={{ fontSize: 14, fontWeight: 500 }}>{dim.score.toFixed(1)}</span>
                    </div>
                    <div style={{
                      height: 8,
                      background: 'var(--bg)',
                      borderRadius: 4,
                      overflow: 'hidden'
                    }}>
                      <div style={{
                        width: `${dim.score}%`,
                        height: '100%',
                        background: 'var(--brand)',
                        borderRadius: 4,
                        transition: 'width 0.3s ease'
                      }} />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Tips */}
        <div style={{
          background: 'color-mix(in oklab, var(--brand) 8%, transparent)',
          border: '1px solid color-mix(in oklab, var(--brand) 20%, transparent)',
          borderRadius: 12,
          padding: 16,
          marginTop: 24
        }}>
          <div style={{ display: 'flex', gap: 12, alignItems: 'flex-start' }}>
            <Icon name="info" size={16} style={{ color: 'var(--brand)', marginTop: 2 }} />
            <div>
              <p style={{ fontSize: 14 }}>技能分数基于你的学习进度、实验完成情况和测试成绩自动计算。完成更多课程来提升你的技能评分。</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RadarPage;
