import React from 'react';
import { Icon } from './icons';
import { loadCourses, MOCK_COURSES } from './data';
import { useNavigate, useLocation } from 'react-router-dom';

/* Topbar / Navigation / Command palette */

const Topbar = ({ onOpenSearch, onOpenTweaks }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const tabs = [
    { id: "home",     label: "首页",   icon: "home" },
    { id: "courses",  label: "课程",   icon: "book" },
    { id: "progress", label: "进度",   icon: "trending" },
    { id: "discuss",  label: "讨论区", icon: "message" },
  ];

  const pathname = location.pathname;
  const active = pathname.startsWith('/courses') || pathname.startsWith('/chapter') || pathname.startsWith('/lab')
    ? "courses"
    : pathname === '/' || pathname === ''
      ? "home"
      : pathname.startsWith('/progress')
        ? "progress"
        : pathname.startsWith('/discuss')
          ? "discuss"
          : pathname.split('/').filter(Boolean)[0] || 'home';

  return (
    <header className="topbar">
      <div className="topbar-inner">
        <a className="brand" href="#" onClick={(e) => { e.preventDefault(); navigate('/'); }}>
          <span className="brand-mark">J</span>
          <span>JING</span>
          <span className="dim" style={{ fontWeight: 400, marginLeft: 2 }}>· 学习平台</span>
        </a>

        <nav className="nav" aria-label="主导航">
          {tabs.map(t => (
            <a
              key={t.id}
              href="#"
              className={active === t.id ? "active" : ""}
              onClick={(e) => {
                e.preventDefault();
                if (t.id === "home") navigate('/');
                else if (t.id === "courses") navigate('/courses');
                else if (t.id === "progress") navigate('/progress');
                else if (t.id === "discuss") navigate('/discuss');
              }}
            >{t.label}</a>
          ))}
        </nav>

        <div className="topbar-spacer" />

        <button className="search-trigger" onClick={onOpenSearch} aria-label="搜索">
          <Icon name="search" size={14} />
          <span>搜索课程、章节、实验…</span>
          <span className="kbd"><span>⌘</span><span>K</span></span>
        </button>

        <button className="icon-btn" title="通知"><Icon name="bell" size={16} /></button>
        <button className="icon-btn" title="设计参数" onClick={onOpenTweaks}><Icon name="settings" size={16} /></button>
        <div className="avatar" title="learner@jing.dev">LJ</div>
      </div>
    </header>
  );
};

const MobileNav = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const tabs = [
    { id: "home", label: "首页", icon: "home" },
    { id: "courses", label: "课程", icon: "book" },
    { id: "progress", label: "进度", icon: "trending" },
    { id: "discuss", label: "讨论", icon: "message" },
  ];

  const pathname = location.pathname;
  const active = pathname.startsWith('/courses') || pathname.startsWith('/chapter') || pathname.startsWith('/lab')
    ? "courses"
    : pathname === '/' || pathname === ''
      ? "home"
      : pathname.startsWith('/progress')
        ? "progress"
        : pathname.startsWith('/discuss')
          ? "discuss"
          : pathname.split('/').filter(Boolean)[0] || 'home';

  return (
    <nav className="mobile-nav" aria-label="底部导航">
      {tabs.map(t => (
        <a key={t.id} href="#" className={active === t.id ? "active" : ""} onClick={(e) => {
          e.preventDefault();
          if (t.id === "home") navigate('/');
          else if (t.id === "courses") navigate('/courses');
          else if (t.id === "progress") navigate('/progress');
          else if (t.id === "discuss") navigate('/discuss');
        }}>
          <Icon name={t.icon} size={18} />
          {t.label}
        </a>
      ))}
    </nav>
  );
};

const CommandPalette = ({ open, onClose }) => {
  const navigate = useNavigate();
  const [q, setQ] = React.useState("");
  const [courses, setCourses] = React.useState(MOCK_COURSES);
  const inputRef = React.useRef(null);
  React.useEffect(() => {
    loadCourses().then(setCourses);
  }, []);
  React.useEffect(() => {
    if (open) setTimeout(() => inputRef.current?.focus(), 30);
    const onKey = (e) => {
      if (e.key === "Escape" && open) onClose();
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        onClose(!open);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open]);

  if (!open) return null;

  // Build pseudo-results from data
  const ql = q.trim().toLowerCase();
  const courseHits = courses.filter(c => !ql || c.title.toLowerCase().includes(ql) || c.subtitle.toLowerCase().includes(ql)).slice(0, 4);
  const chapterHits = courses.flatMap(c => (c.chapters || []).map(ch => ({ ...ch, course: c })))
    .filter(ch => !ql || ch.title.toLowerCase().includes(ql))
    .slice(0, 4);

  return (
    <div onClick={onClose} style={{
      position: "fixed", inset: 0, zIndex: 200,
      background: "color-mix(in oklab, var(--bg) 60%, transparent)",
      backdropFilter: "blur(8px)", WebkitBackdropFilter: "blur(8px)",
      display: "flex", justifyContent: "center", paddingTop: "12vh",
    }}>
      <div
        onClick={(e) => e.stopPropagation()}
        style={{
          width: "min(640px, 92vw)",
          background: "var(--bg-1)",
          border: "1px solid var(--line-2)",
          borderRadius: 14,
          boxShadow: "0 24px 80px rgba(0,0,0,0.5)",
          overflow: "hidden",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 10, padding: "14px 16px", borderBottom: "1px solid var(--line)" }}>
          <Icon name="search" size={16} />
          <input
            ref={inputRef}
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="搜索课程、章节、实验，或输入 / 触发 AI 助手…"
            style={{
              flex: 1, background: "transparent", border: 0, outline: 0,
              color: "var(--fg)", fontSize: 14, height: 24,
            }}
          />
          <span className="kbd"><span>esc</span></span>
        </div>
        <div style={{ maxHeight: 420, overflowY: "auto", padding: 8 }}>
          {q.startsWith("/") ? (
            <div style={{ padding: 24, textAlign: "center" }}>
              <Icon name="sparkles" size={20} />
              <p className="muted" style={{ marginTop: 8, fontSize: 13 }}>AI 助手：解释概念、调试代码、推荐学习路径</p>
              <button className="btn btn-primary btn-sm" style={{ marginTop: 12 }}>
                <Icon name="send" size={12} />
                问 AI：{q.slice(1) || "如何理解逻辑回归"}
              </button>
            </div>
          ) : (
            <>
              <Group title="课程">
                {courseHits.map(c => (
                  <Row key={c.id} icon="book" title={c.title} sub={c.subtitle}
                       onClick={() => { onClose(); navigate('/courses/' + c.id); }} />
                ))}
              </Group>
              <Group title="章节 / 实验">
                {chapterHits.map(ch => (
                  <Row key={ch.id} icon={ch.type === "lab" ? "flask" : "fileText"}
                       title={ch.title}
                       sub={ch.course.title}
                       onClick={() => {
                         onClose();
                         if (ch.type === "lab") navigate('/lab/' + ch.id);
                         else navigate('/chapter/' + ch.id);
                       }} />
                ))}
              </Group>
              <Group title="操作">
                <Row icon="trending" title="查看我的进度" onClick={() => { onClose(); navigate('/progress'); }} />
                <Row icon="sparkles" title="问 AI 助手"  onClick={() => setQ("/")} />
              </Group>
            </>
          )}
        </div>
        <div style={{ display: "flex", gap: 16, padding: "10px 16px", borderTop: "1px solid var(--line)", fontSize: 11.5, color: "var(--fg-3)" }}>
          <span><span className="kbd"><span>↑↓</span></span> 选择</span>
          <span><span className="kbd"><span>↵</span></span> 打开</span>
          <span><span className="kbd"><span>/</span></span> AI 助手</span>
        </div>
      </div>
    </div>
  );
};

const Group = ({ title, children }) => {
  if (!React.Children.count(children)) return null;
  return (
    <div style={{ padding: "4px 0 8px" }}>
      <div style={{ fontSize: 11, fontWeight: 600, color: "var(--fg-3)", textTransform: "uppercase", letterSpacing: 0.04, padding: "6px 10px" }}>{title}</div>
      {children}
    </div>
  );
};

const Row = ({ icon, title, sub, onClick }) => (
  <button onClick={onClick} style={{
    display: "flex", alignItems: "center", gap: 12, width: "100%",
    padding: "8px 10px", borderRadius: 8, textAlign: "left",
    transition: "background .12s",
  }}
  onMouseEnter={(e) => e.currentTarget.style.background = "var(--surface-2)"}
  onMouseLeave={(e) => e.currentTarget.style.background = "transparent"}>
    <span style={{ color: "var(--fg-2)" }}><Icon name={icon} size={15} /></span>
    <span style={{ flex: 1, minWidth: 0 }}>
      <div style={{ fontSize: 13.5, color: "var(--fg)" }}>{title}</div>
      {sub && <div style={{ fontSize: 12, color: "var(--fg-3)", marginTop: 1 }}>{sub}</div>}
    </span>
    <Icon name="arrowRight" size={13} style={{ color: "var(--fg-4)" }} />
  </button>
);

export { Topbar, MobileNav, CommandPalette };
