/* Home screen — Hero, learning path, continue learning, featured courses */
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Icon } from '../icons';
import { loadCourses, loadPlatformStats, CURRENT, LEVEL_MAP, CATEGORY_MAP } from '../data';

const ScreenHome = ({ tweaks }) => {
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
  
  const current = courses.find(c => c.id === CURRENT.course_id);
  const currentChapter = current?.chapters?.find(ch => ch.id === CURRENT.chapter_id);
  const overallProgress = courses.length > 0
    ? Math.round(courses.reduce((sum, c) => sum + (c.chapters_done || 0), 0) / courses.reduce((sum, c) => sum + (c.chapters_total || 1), 0) * 100)
    : 0;
  const totalStudents = courses.reduce((s, c) => s + (c.students || 0), 0);

  return (
    <div className="screen">
      <Hero progress={overallProgress} layout={tweaks?.hero_layout} totalStudents={totalStudents} />

      <section className="container" style={{ paddingTop: 32 }}>
        <ContinueCard course={current} chapter={currentChapter} />
      </section>

      <section className="container" style={{ paddingTop: 56 }}>
        <div className="section-h">
          <div>
            <h2>学习路径</h2>
            <div className="meta" style={{ marginTop: 2 }}>6 阶段，从工程师到 AI 团队 Leader · 整体进度 {overallProgress}%</div>
          </div>
          <button className="btn btn-ghost btn-sm" onClick={() => navigate('/courses')}>
            查看全部 <Icon name="arrowRight" size={12} />
          </button>
        </div>
        <LearningPath courses={courses} />
      </section>

      <section className="container" style={{ paddingTop: 56, paddingBottom: 80 }}>
        <div className="section-h">
          <div>
            <h2>推荐课程</h2>
            <div className="meta" style={{ marginTop: 2 }}>基于你在 Phase 1 / 2 的进度</div>
          </div>
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))", gap: 16 }}>
          {courses.slice(2, 6).map(c => (
            <CourseCard key={c.id} course={c} onOpen={() => navigate('/courses/' + c.id)} />
          ))}
        </div>
      </section>
    </div>
  );
};

const Hero = ({ progress, layout, totalStudents }) => {
  const navigate = useNavigate();
  if (layout === "split") {
    return (
      <section style={{
        borderBottom: "1px solid var(--line)",
        background: "linear-gradient(180deg, color-mix(in oklab, var(--brand) 4%, transparent), transparent 70%)",
      }}>
        <div className="container" style={{ display: "grid", gridTemplateColumns: "1.2fr 1fr", gap: 56, padding: "64px 24px 56px", alignItems: "center" }}>
          <div>
            <div className="tag tag-brand" style={{ marginBottom: 18 }}>
              <Icon name="sparkles" size={11} />
              <span>v4.0 · 上线 LLM 应用开发</span>
            </div>
            <h1 className="h-display">
              系统地学 AI，<br />
              <span style={{ color: "var(--fg-3)" }}>而不是收藏教程。</span>
            </h1>
            <p style={{ fontSize: 15, color: "var(--fg-2)", marginTop: 18, maxWidth: 480, lineHeight: 1.65 }}>
              60 章 · 43 个实验 · 浏览器内沙箱 · 真测试用例评测。从 Python 入门到把模型部署上生产，一条路径走完。
            </p>
            <div className="hstack" style={{ marginTop: 24, gap: 10 }}>
              <button className="btn btn-primary btn-lg" onClick={() => navigate('/courses')}>
                继续学习 <Icon name="arrowRight" size={14} />
              </button>
              <button className="btn btn-secondary btn-lg" onClick={() => navigate('/progress')}>
                查看进度
              </button>
            </div>
          </div>
          <HeroVisual />
        </div>
      </section>
    );
  }
  return (
    <section style={{
      borderBottom: "1px solid var(--line)",
      position: "relative",
      overflow: "hidden",
      background: "radial-gradient(ellipse 60% 50% at 50% 0%, var(--brand-soft), transparent 70%)",
    }}>
      <div className="container" style={{ padding: "80px 24px 56px", textAlign: "center" }}>
        <div className="tag tag-brand" style={{ marginBottom: 24 }}>
          <Icon name="sparkles" size={11} />
          <span>v4.0 · 上线 LLM 应用开发</span>
        </div>
        <h1 className="h-display" style={{ maxWidth: 720, margin: "0 auto" }}>
          系统地学 AI，<span style={{ color: "var(--fg-3)" }}>而不是收藏教程。</span>
        </h1>
        <p style={{ fontSize: 15.5, color: "var(--fg-2)", maxWidth: 560, margin: "20px auto 0", lineHeight: 1.65 }}>
          60 章 · 43 个实验 · 浏览器内沙箱 · 真测试用例评测。<br />
          从 Python 入门到把模型部署上生产，一条路径走完。
        </p>
        <div className="hstack" style={{ marginTop: 28, justifyContent: "center", gap: 10 }}>
          <button className="btn btn-primary btn-lg" onClick={() => navigate('/courses')}>
            继续学习 <Icon name="arrowRight" size={14} />
          </button>
          <button className="btn btn-secondary btn-lg" onClick={() => navigate('/progress')}>
            查看进度
          </button>
        </div>
        <HeroStats totalStudents={totalStudents} />
      </div>
    </section>
  );
};

const HeroStats = ({ totalStudents }) => {
  const fmtStudents = totalStudents >= 1000
    ? (totalStudents / 1000).toFixed(totalStudents >= 10000 ? 1 : 0) + 'k'
    : totalStudents.toLocaleString();
  return (
  <div style={{
    display: "grid", gridTemplateColumns: "repeat(4, 1fr)",
    maxWidth: 720, margin: "48px auto 0", gap: 0,
    border: "1px solid var(--line)", borderRadius: 12,
    background: "var(--surface)",
  }}>
    {[
      { n: stats?.total_chapters ? String(stats.total_chapters) : '—', l: "章节" },
      { n: stats?.total_labs ? String(stats.total_labs) : '—', l: "实验" },
      { n: stats?.total_phases ? String(stats.total_phases) : '6', l: "学习阶段" },
      { n: fmtStudents, l: "在学学员" },
    ].map((s, i) => (
      <div key={i} style={{
        padding: "20px 16px", textAlign: "center",
        borderRight: i < 3 ? "1px solid var(--line)" : "none",
      }}>
        <div className="num" style={{ fontSize: 22, fontWeight: 600, letterSpacing: "-0.02em" }}>{s.n}</div>
        <div style={{ fontSize: 12, color: "var(--fg-3)", marginTop: 2 }}>{s.l}</div>
      </div>
    ))}
  </div>
  );
};

const HeroVisual = () => (
  <div style={{
    position: "relative",
    height: 360,
    border: "1px solid var(--line)",
    borderRadius: 14,
    background: "var(--surface)",
    overflow: "hidden",
    boxShadow: "0 20px 60px rgba(0,0,0,0.3)",
  }}>
    {/* Mini code editor */}
    <div style={{ borderBottom: "1px solid var(--line)", padding: "10px 14px", display: "flex", alignItems: "center", gap: 8 }}>
      <span className="dot" style={{ background: "#ff5f57" }} />
      <span className="dot" style={{ background: "#febc2e" }} />
      <span className="dot" style={{ background: "#28c840" }} />
      <span className="mono dim" style={{ fontSize: 11.5, marginLeft: 8 }}>lab_logistic_regression.py</span>
      <span className="spacer" />
      <span className="tag tag-ok" style={{ height: 20, fontSize: 10.5 }}>
        <Icon name="check" size={10} />6/6 通过
      </span>
    </div>
    <pre className="mono" style={{ margin: 0, padding: 16, fontSize: 12, lineHeight: 1.7, color: "var(--fg-2)", overflow: "hidden" }}>
{`import numpy as np
from sklearn.linear_model import LogisticRegression

def train(X, y):
    model = LogisticRegression(`}<span style={{ color: "var(--brand)" }}>{`max_iter=1000`}</span>{`)\n    model.fit(X, y)\n    return model\n\n# 评测点：Recall ≥ 0.85\ny_pred = model.predict(X_test)\nrecall = `}<span style={{ color: "var(--ok)" }}>0.87</span>{`  # ✓\nprecision = `}<span style={{ color: "var(--warn)" }}>0.71</span>{`  # ✓\n\n# 决策边界可视化…`}</pre>
  </div>
);

const ContinueCard = ({ course, chapter }) => {
  const navigate = useNavigate();
  if (!course || !chapter) return null;
  const courseProgress = Math.round(course.chapters_done / course.chapters_total * 100);
  return (
    <div className="card" style={{
      padding: 24, display: "grid",
      gridTemplateColumns: "1fr auto", gap: 24, alignItems: "center",
      borderColor: "var(--brand-soft-2)",
      background: "linear-gradient(135deg, var(--brand-soft), transparent 60%), var(--surface)",
    }}>
      <div style={{ minWidth: 0 }}>
        <div className="hstack" style={{ gap: 10, color: "var(--brand)", fontSize: 12, fontWeight: 500 }}>
          <Icon name="play" size={12} />
          <span>继续学习 · {CURRENT.resumed_at}</span>
        </div>
        <h2 className="h-1" style={{ marginTop: 8 }}>{chapter.title}</h2>
        <div className="hstack dim" style={{ gap: 14, marginTop: 6, fontSize: 13 }}>
          <span>{course.title}</span>
          <span>·</span>
          <span>第 {chapter.num} 章 / 共 {course.chapters_total} 章</span>
          <span>·</span>
          <span className="hstack" style={{ gap: 4 }}><Icon name="clock" size={12} />{chapter.duration} 分钟</span>
        </div>
        <div style={{ marginTop: 16, maxWidth: 520 }}>
          <div className="hstack dim" style={{ justifyContent: "space-between", fontSize: 12, marginBottom: 6 }}>
            <span>课程进度</span>
            <span className="num">{course.chapters_done} / {course.chapters_total}</span>
          </div>
          <div className="prog prog-lg" role="progressbar" aria-valuenow={courseProgress} aria-valuemin={0} aria-valuemax={100}>
            <i style={{ width: `${courseProgress}%` }} />
          </div>
        </div>
      </div>
      <div className="vstack" style={{ gap: 8 }}>
        <button className="btn btn-primary btn-lg" onClick={() => navigate('/chapter/' + chapter.id)}>
          <Icon name="play" size={13} /> 继续阅读
        </button>
        <button className="btn btn-ghost btn-sm" onClick={() => navigate('/courses/' + course.id)}>
          查看大纲
        </button>
      </div>
    </div>
  );
};

const LearningPath = ({ courses }) => {
  const navigate = useNavigate();
  return (
    <div style={{ display: "grid", gridTemplateColumns: "repeat(6, 1fr)", gap: 12 }}>
      {courses.map((c, i) => {
        const pct = Math.round(c.chapters_done / c.chapters_total * 100);
        const state = c.chapters_done === c.chapters_total ? "done"
                   : c.chapters_done > 0 ? "active"
                   : "locked";
        return (
          <button
            key={c.id}
            onClick={() => navigate('/courses/' + c.id)}
            className="card card-hover"
            style={{
              padding: 16, textAlign: "left", cursor: "pointer",
              borderColor: state === "active" ? "var(--brand-soft-2)" : "var(--line)",
              background: state === "active" ? "var(--surface-2)" : "var(--surface)",
              minHeight: 168,
              display: "flex", flexDirection: "column", justifyContent: "space-between",
            }}
          >
            <div>
              <div className="hstack" style={{ justifyContent: "space-between" }}>
                <span className="mono dim" style={{ fontSize: 11, letterSpacing: 0.04 }}>PHASE {c.phase}</span>
                {state === "done" && <Icon name="checkCircle" size={14} style={{ color: "var(--ok)" }} />}
                {state === "active" && <span className="dot dot-brand" />}
                {state === "locked" && <Icon name="circleDashed" size={14} style={{ color: "var(--fg-4)" }} />}
              </div>
              <div className="h-3" style={{ marginTop: 10, color: state === "locked" ? "var(--fg-3)" : "var(--fg)" }}>
                {c.title}
              </div>
              <div className="dim" style={{ fontSize: 11.5, marginTop: 4 }}>
                {c.chapters_total} 章 · {c.lab_total} 实验
              </div>
            </div>
            <div>
              <div className="prog" style={{ marginTop: 12 }}>
                <i style={{ width: `${pct}%` }} />
              </div>
              <div className="dim num" style={{ fontSize: 11, marginTop: 6 }}>{pct}%</div>
            </div>
          </button>
        );
      })}
    </div>
  );
};

const CourseCard = ({ course, onOpen }) => {
  const lvl = LEVEL_MAP[course.level];
  const pct = Math.round(course.chapters_done / course.chapters_total * 100);
  return (
    <button
      onClick={onOpen}
      className="card card-hover"
      style={{
        padding: 20, textAlign: "left", cursor: "pointer",
        display: "flex", flexDirection: "column", gap: 14, minHeight: 220,
      }}
    >
      <div className="hstack" style={{ justifyContent: "space-between" }}>
        <span style={{
          width: 36, height: 36, borderRadius: 9,
          background: "var(--surface-2)", border: "1px solid var(--line)",
          display: "grid", placeItems: "center", color: "var(--brand)",
        }}>
          <Icon name={course.icon} size={18} />
        </span>
        <span className="tag" style={{ color: lvl.color, borderColor: "var(--line)", background: "transparent" }}>
          <span className="dot" style={{ background: lvl.color, boxShadow: "none" }} />
          {lvl.text}
        </span>
      </div>
      <div>
        <div className="mono dim" style={{ fontSize: 11, letterSpacing: 0.04 }}>PHASE {course.phase}</div>
        <div className="h-2" style={{ marginTop: 4 }}>{course.title}</div>
        <p className="muted" style={{ fontSize: 13, marginTop: 6, lineHeight: 1.55,
          display: "-webkit-box", WebkitLineClamp: 2, WebkitBoxOrient: "vertical", overflow: "hidden" }}>
          {course.description}
        </p>
      </div>
      <div className="spacer" />
      <div className="hstack dim" style={{ fontSize: 12, gap: 14, justifyContent: "space-between" }}>
        <span className="hstack" style={{ gap: 4 }}><Icon name="fileText" size={12} />{course.chapters_total} 章</span>
        <span className="hstack" style={{ gap: 4 }}><Icon name="flask" size={12} />{course.lab_total} 实验</span>
        <span className="hstack" style={{ gap: 4 }}><Icon name="clock" size={12} />{course.duration_hours}h</span>
      </div>
    </button>
  );
};

export default ScreenHome;
export { CourseCard };
