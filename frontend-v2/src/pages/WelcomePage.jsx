/* Welcome page — unauthenticated landing with CTA and phase preview */
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Icon } from '../icons';
import { loadCourses, loadPlatformStats } from '../data';

const WelcomePage = () => {
  const navigate = useNavigate();
  const [courses, setCourses] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    setLoading(true);
    Promise.all([
      loadCourses(),
      loadPlatformStats(),
    ]).then(([coursesData, statsData]) => {
      setCourses(coursesData || []);
      setStats(statsData);
      setLoading(false);
    });
  }, []);

  return (
    <div className="screen" style={{ paddingBottom: 80 }}>
      {/* Hero */}
      <section style={{
        borderBottom: "1px solid var(--line)",
        background: "radial-gradient(ellipse 60% 50% at 50% 0%, var(--brand-soft), transparent 70%)",
        textAlign: "center",
      }}>
        <div className="container" style={{ padding: "80px 24px 56px" }}>
          <div className="tag tag-brand" style={{ marginBottom: 24 }}>
            <Icon name="sparkles" size={11} />
            <span>v4.0 · 6 阶段系统化 AI 学习</span>
          </div>
          <h1 className="h-display" style={{ maxWidth: 640, margin: "0 auto" }}>
            AI 学习平台
          </h1>
          <p style={{ fontSize: 15.5, color: "var(--fg-2)", maxWidth: 520, margin: "20px auto 0", lineHeight: 1.65 }}>
            60 章 · 43 个实验 · 浏览器内沙箱 · 真测试用例评测。<br />
            从 Python 入门到把模型部署上生产，一条路径走完。
          </p>
          <div className="hstack" style={{ marginTop: 28, justifyContent: "center", gap: 10 }}>
            <button className="btn btn-primary btn-lg" onClick={() => navigate('/register')}>
              开始学习 <Icon name="arrowRight" size={14} />
            </button>
            <button className="btn btn-secondary btn-lg" onClick={() => navigate('/login')}>
              已有账号？登录
            </button>
          </div>

          {/* Stats row */}
          <div style={{
            display: "grid", gridTemplateColumns: "repeat(3, 1fr)",
            maxWidth: 540, margin: "48px auto 0", gap: 0,
            border: "1px solid var(--line)", borderRadius: 12,
            background: "var(--surface)",
          }}>
            {[
              { n: stats?.total_chapters ? String(stats.total_chapters) : '—', l: "章节" },
              { n: stats?.total_labs ? String(stats.total_labs) : '—', l: "实验" },
              { n: stats?.total_students ? String(stats.total_students) : '—', l: "在学学员" },
            ].map((s, i) => (
              <div key={i} style={{
                padding: "20px 16px", textAlign: "center",
                borderRight: i < 2 ? "1px solid var(--line)" : "none",
              }}>
                <div className="num" style={{ fontSize: 22, fontWeight: 600, letterSpacing: "-0.02em" }}>{s.n}</div>
                <div style={{ fontSize: 12, color: "var(--fg-3)", marginTop: 2 }}>{s.l}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Phase overview */}
      <section className="container" style={{ paddingTop: 56 }}>
        <h2 style={{ textAlign: "center", marginBottom: 32 }}>学习路径</h2>
        {loading ? (
          <div style={{ textAlign: 'center', padding: '40px', color: 'var(--fg-3)' }}>加载中…</div>
        ) : courses.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '40px', color: 'var(--fg-3)' }}>暂无课程数据</div>
        ) : (
          <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 12 }}>
            {courses.map((c) => (
              <div key={c.id} className="card" style={{
                padding: 20, textAlign: "center",
                display: "flex", flexDirection: "column", gap: 8,
              }}>
                <div className="mono dim" style={{ fontSize: 11, letterSpacing: 0.04 }}>PHASE {c.phase}</div>
                <span style={{
                  width: 40, height: 40, borderRadius: 10, margin: "0 auto",
                  background: "var(--surface-2)", border: "1px solid var(--line)",
                  display: "grid", placeItems: "center", color: "var(--brand)",
                }}>
                  <Icon name={c.icon} size={20} />
                </span>
                <div className="h-3">{c.title}</div>
                <div className="dim" style={{ fontSize: 11.5 }}>
                  {c.chapters_total} 章 · {c.lab_total} 实验 · {c.duration_hours}h
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
};

export default WelcomePage;
