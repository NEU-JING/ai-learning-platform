import React from 'react';
import { Icon } from './icons';
import { loadCourses } from './data';
import { useNavigate, useLocation } from 'react-router-dom';

/* Topbar / Navigation / Command palette */

const Topbar = ({ onOpenSearch, onOpenTweaks, auth = {} }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const isLoggedIn = auth.isLoggedIn || false;
  const user = auth.user || null;
  const tabs = [
    { id: "home",     label: "首页",   icon: "home" },
    { id: "courses",  label: "课程",   icon: "book" },
    { id: "progress", label: "进度",   icon: "trending" },

  ];

  const pathname = location.pathname;
  const active = pathname.startsWith('/courses') || pathname.startsWith('/chapter') || pathname.startsWith('/lab')
    ? "courses"
    : pathname === '/' || pathname === ''
      ? "home"
      : pathname.startsWith('/progress')
        ? "progress"
      : pathname.split('/').filter(Boolean)[0] || 'home';

  return (
    <header className="topbar">
      <div className="topbar-inner">
        <a className="brand" href="#" onClick={(e) => { e.preventDefault(); navigate('/'); }} title="AI Learning Platform">
          {/* SVG Logo: AI神经元图标 + 品牌名 */}
          <svg width="28" height="28" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg" style={{ marginRight: 10, flexShrink: 0 }}>
            <rect width="28" height="28" rx="6" fill="url(#logo-gradient)"/>
            <circle cx="14" cy="14" r="3" fill="white"/>
            <circle cx="14" cy="7" r="2" fill="white" opacity="0.9"/>
            <circle cx="14" cy="21" r="2" fill="white" opacity="0.9"/>
            <circle cx="7" cy="14" r="2" fill="white" opacity="0.7"/>
            <circle cx="21" cy="14" r="2" fill="white" opacity="0.7"/>
            <circle cx="8.5" cy="8.5" r="1.5" fill="white" opacity="0.5"/>
            <circle cx="19.5" cy="8.5" r="1.5" fill="white" opacity="0.5"/>
            <circle cx="8.5" cy="19.5" r="1.5" fill="white" opacity="0.5"/>
            <circle cx="19.5" cy="19.5" r="1.5" fill="white" opacity="0.5"/>
            <line x1="14" y1="11" x2="14" y2="7" stroke="white" strokeWidth="1.5" opacity="0.8"/>
            <line x1="14" y1="17" x2="14" y2="21" stroke="white" strokeWidth="1.5" opacity="0.8"/>
            <line x1="11" y1="14" x2="7" y2="14" stroke="white" strokeWidth="1.5" opacity="0.6"/>
            <line x1="17" y1="14" x2="21" y2="14" stroke="white" strokeWidth="1.5" opacity="0.6"/>
            <defs>
              <linearGradient id="logo-gradient" x1="0" y1="0" x2="28" y2="28" gradientUnits="userSpaceOnUse">
                <stop stopColor="#6366f1"/>
                <stop offset="1" stopColor="#8b5cf6"/>
              </linearGradient>
            </defs>
          </svg>
          <span style={{ fontWeight: 700, fontSize: 16, letterSpacing: '-0.02em' }}>AILP</span>
          <span className="dim" style={{ fontWeight: 400, marginLeft: 6, fontSize: 13 }}>AI学习平台</span>
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
        {isLoggedIn ? (
          <div className="avatar" title={user?.email || 'learner'}>{user?.name ? user.name.slice(0, 2).toUpperCase() : (user?.email || '??').slice(0, 2).toUpperCase()}</div>
        ) : (
          <div className="hstack" style={{ gap: 8 }}>
            <button className="btn btn-ghost btn-sm" onClick={() => navigate('/login')}>登录</button>
            <button className="btn btn-primary btn-sm" onClick={() => navigate('/register')}>注册</button>
          </div>
        )}
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

  ];

  const pathname = location.pathname;
  const active = pathname.startsWith('/courses') || pathname.startsWith('/chapter') || pathname.startsWith('/lab')
    ? "courses"
    : pathname === '/' || pathname === ''
      ? "home"
      : pathname.startsWith('/progress')
        ? "progress"
      : pathname.split('/').filter(Boolean)[0] || 'home';

  return (
    <nav className="mobile-nav" aria-label="底部导航">
      {tabs.map(t => (
        <a key={t.id} href="#" className={active === t.id ? "active" : ""} onClick={(e) => {
          e.preventDefault();
          if (t.id === "home") navigate('/');
          else if (t.id === "courses") navigate('/courses');
          else if (t.id === "progress") navigate('/progress');
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
  const [courses, setCourses] = React.useState([]);
  const inputRef = React.useRef(null);
  React.useEffect(() => {
    loadCourses().then(data => setCourses(data || []));
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
