/* Chapter reading screen — Breadcrumb + sticky progress + TOC + content + prev/next */
import React, { useState, useEffect } from 'react';
import { Icon } from '../icons';
import { loadChapter, loadCourses, CURRENT, MOCK_CHAPTER, MOCK_COURSES, PROGRESS_STATS, LEVEL_MAP, CATEGORY_MAP } from '../data';
import { useNavigate, useParams } from 'react-router-dom';

const ScreenChapter = () => {
  const navigate = useNavigate();
  const { id } = useParams();
  const [chapter, setChapter] = useState(MOCK_CHAPTER);
  const [courses, setCourses] = useState(MOCK_COURSES);
  useEffect(() => {
    loadChapter(id).then(ch => { if (ch) setChapter(ch); });
    loadCourses().then(setCourses);
  }, [id]);
  const course = courses.find(c => c.id === chapter.course_id) || courses[2];
  const chapterList = course.chapters || [];
  const currentIdx = chapterList.findIndex(c => c.id === chapter.id);
  const prev = currentIdx > 0 ? chapterList[currentIdx - 1] : null;
  const next = currentIdx >= 0 && currentIdx < chapterList.length - 1 ? chapterList[currentIdx + 1] : null;
  const pct = chapterList.length ? Math.round((currentIdx + 1) / chapterList.length * 100) : 0;

  const [activeSection, setActiveSection] = React.useState("s1");
  const [drawerOpen, setDrawerOpen] = React.useState(false);

  return (
    <div className="screen">
      {/* Sticky breadcrumb / progress bar */}
      <div style={{
        position: "sticky", top: 56, zIndex: 40,
        background: "color-mix(in oklab, var(--bg) 92%, transparent)",
        backdropFilter: "blur(12px)",
        borderBottom: "1px solid var(--line)",
      }}>
        <div className="container hstack" style={{ height: 48, gap: 14 }}>
          {/* Breadcrumb */}
          <nav className="crumb" style={{ flex: 1, minWidth: 0 }}>
            <a href="#" onClick={(e) => { e.preventDefault(); navigate('/courses'); }}>课程</a>
            <Icon name="chevronRight" size={11} className="sep" />
            <a href="#" onClick={(e) => { e.preventDefault(); navigate('/courses/' + course.id); }} style={{
              overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", maxWidth: 220,
            }}>{course.title}</a>
            <Icon name="chevronRight" size={11} className="sep" />
            <span className="current" style={{
              overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap",
            }}>第 {chapter.num} 章 · {chapter.title}</span>
          </nav>

          {/* Position indicator + nav */}
          <span className="dim num" style={{ fontSize: 12, whiteSpace: "nowrap" }}>
            {currentIdx + 1} / {chapterList.length}
          </span>
          <div className="hstack" style={{ gap: 2 }}>
            <button
              className="btn btn-ghost btn-sm"
              aria-disabled={!prev}
              disabled={!prev}
              onClick={() => prev && navigate('/chapter/' + prev.id)}
              title={prev ? `上一章：${prev.title}` : "已是第一章"}
              style={{ padding: 0, width: 32, height: 28 }}
            ><Icon name="chevronLeft" size={14} /></button>
            <button
              className="btn btn-ghost btn-sm"
              aria-disabled={!next}
              disabled={!next}
              onClick={() => next && navigate('/chapter/' + next.id)}
              title={next ? `下一章：${next.title}` : "已是最后一章"}
              style={{ padding: 0, width: 32, height: 28 }}
            ><Icon name="chevronRight" size={14} /></button>
          </div>

          {/* Mobile drawer */}
          <button
            className="btn btn-ghost btn-sm"
            onClick={() => setDrawerOpen(true)}
            title="章节目录"
            style={{ padding: 0, width: 32, height: 28 }}
          ><Icon name="list" size={14} /></button>
        </div>
        {/* Reading progress (course-level) */}
        <div className="prog" style={{ height: 2, borderRadius: 0, background: "transparent" }}>
          <i style={{ width: `${pct}%` }} />
        </div>
      </div>

      <div className="container layout-2col-left">
        {/* Left rail: TOC */}
        <aside className="sidebar">
          <div className="sidebar-sticky">
            <ChapterSidebar
              course={course}
              chapters={chapterList}
              currentId={chapter.id}
              toc={chapter.toc}
              activeSection={activeSection}
              setActiveSection={setActiveSection}
              onNavigate={(screen, opts) => {
                if (screen === "lab") navigate('/lab/' + opts.id);
                else if (screen === "chapter") navigate('/chapter/' + opts.id);
              }}
            />
          </div>
        </aside>

        {/* Main content */}
        <main style={{ paddingTop: 8 }}>
          <ChapterHeader chapter={chapter} />
          <article className="md-body" style={{ marginTop: 24 }}>
            {chapter.blocks.map((b, i) => <Block key={i} block={b} />)}
          </article>

          {/* Lab entry / chapter complete actions */}
          <div className="card" style={{
            marginTop: 36, padding: 18,
            display: "grid", gridTemplateColumns: "1fr auto", gap: 16, alignItems: "center",
            background: "linear-gradient(135deg, var(--brand-soft), transparent 70%), var(--surface)",
            borderColor: "var(--brand-soft-2)",
          }}>
            <div>
              <div className="h-3" style={{ color: "var(--brand)", marginBottom: 4 }}>动手实验 · 学以致用</div>
              <div className="muted" style={{ fontSize: 13 }}>
                完成《信用卡欺诈检测》实验巩固本章知识。Recall ≥ 0.85，Precision ≥ 0.70。
              </div>
            </div>
            <button className="btn btn-primary" onClick={() => navigate('/lab/35')}>
              <Icon name="flask" size={13} /> 进入实验
            </button>
          </div>

          {/* Prev / Next cards */}
          <div style={{ marginTop: 32, display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
            <NavCard chapter={prev} dir="prev" onClick={() => prev && navigate('/chapter/' + prev.id)} />
            <NavCard chapter={next} dir="next" onClick={() => next && navigate('/chapter/' + next.id)} />
          </div>

          {/* Feedback strip */}
          <div className="hstack" style={{ marginTop: 36, padding: "12px 16px", border: "1px solid var(--line)", borderRadius: 10, background: "var(--surface)", justifyContent: "space-between" }}>
            <span className="dim" style={{ fontSize: 13 }}>本章对你有帮助吗？</span>
            <div className="hstack" style={{ gap: 6 }}>
              <button className="btn btn-ghost btn-sm"><Icon name="check" size={12} /> 有帮助</button>
              <button className="btn btn-ghost btn-sm"><Icon name="x" size={12} /> 需改进</button>
              <button className="btn btn-ghost btn-sm"><Icon name="message" size={12} /> 提问</button>
            </div>
          </div>
        </main>
      </div>

      {/* Mobile TOC drawer */}
      {drawerOpen && (
        <MobileDrawer onClose={() => setDrawerOpen(false)}>
          <ChapterSidebar
            course={course}
            chapters={chapterList}
            currentId={chapter.id}
            toc={chapter.toc}
            activeSection={activeSection}
            setActiveSection={(id) => { setActiveSection(id); setDrawerOpen(false); }}
            onNavigate={(screen, opts) => {
              setDrawerOpen(false);
              if (screen === "lab") navigate('/lab/' + opts.id);
              else if (screen === "chapter") navigate('/chapter/' + opts.id);
            }}
          />
        </MobileDrawer>
      )}

      <ChapterMarkdownStyle />
    </div>
  );
};

const ChapterHeader = ({ chapter }) => (
  <header style={{ paddingTop: 24, paddingBottom: 8 }}>
    <div className="dim mono" style={{ fontSize: 11.5, letterSpacing: 0.04 }}>
      CHAPTER {String(chapter.num).padStart(2, "0")}
    </div>
    <h1 className="h-display" style={{ fontSize: 30, marginTop: 8 }}>{chapter.title}</h1>
    <div className="hstack dim" style={{ gap: 16, fontSize: 13, marginTop: 14 }}>
      <span className="hstack" style={{ gap: 5 }}><Icon name="clock" size={12} /> 约 {chapter.duration} 分钟</span>
      <span className="hstack" style={{ gap: 5 }}><Icon name="fileText" size={12} /> 阅读章节</span>
      <span className="hstack" style={{ gap: 5 }}><Icon name="users" size={12} /> 8,920 已学完</span>
    </div>
  </header>
);

const Block = ({ block }) => {
  if (block.type === "h2")
    return <h2 className="md-h2">{block.text}</h2>;
  if (block.type === "h3")
    return <h3 className="md-h3">{block.text}</h3>;
  if (block.type === "p")
    return <p className="md-p">{block.text}</p>;
  if (block.type === "list")
    return (
      <ul className="md-list">
        {block.items.map((it, i) => <li key={i}>{it}</li>)}
      </ul>
    );
  if (block.type === "code")
    return (
      <div className="md-code">
        <div className="md-code-bar">
          <span className="mono dim" style={{ fontSize: 11 }}>{block.lang}</span>
          <span className="spacer" />
          <button className="btn btn-ghost btn-sm" style={{ height: 22, padding: "0 8px" }}>
            <Icon name="copy" size={11} /> 复制
          </button>
        </div>
        <pre className="mono"><code>{block.code}</code></pre>
      </div>
    );
  if (block.type === "callout") {
    const colors = {
      info: { bg: "var(--brand-soft)", brd: "var(--brand-soft-2)", fg: "var(--brand)" },
      warn: { bg: "rgba(251,191,36,0.08)", brd: "rgba(251,191,36,0.20)", fg: "var(--warn)" },
      ok:   { bg: "rgba(74,222,128,0.08)", brd: "rgba(74,222,128,0.20)", fg: "var(--ok)" },
    }[block.tone || "info"];
    return (
      <aside style={{
        margin: "20px 0",
        padding: "14px 18px",
        background: colors.bg,
        border: `1px solid ${colors.brd}`,
        borderRadius: 10,
        borderLeft: `3px solid ${colors.fg}`,
      }}>
        <div className="hstack" style={{ gap: 8, color: colors.fg, fontWeight: 600, fontSize: 13, marginBottom: 4 }}>
          <Icon name={block.tone === "warn" ? "zap" : "sparkles"} size={13} />
          {block.title}
        </div>
        <div style={{ fontSize: 14, color: "var(--fg)", lineHeight: 1.65 }}>{block.text}</div>
      </aside>
    );
  }
  return null;
};

const ChapterSidebar = ({ course, chapters, currentId, toc, activeSection, setActiveSection, onNavigate }) => {
  const [tab, setTab] = React.useState("toc"); // toc | chapters
  return (
    <div>
      {/* Tab switch */}
      <div className="hstack" style={{ gap: 2, padding: 2, background: "var(--surface)", border: "1px solid var(--line)", borderRadius: 6, marginBottom: 14 }}>
        {[
          { id: "toc", label: "本章目录" },
          { id: "chapters", label: "课程章节" },
        ].map(t => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            style={{
              flex: 1,
              padding: "5px 8px",
              fontSize: 12,
              color: tab === t.id ? "var(--fg)" : "var(--fg-3)",
              background: tab === t.id ? "var(--surface-2)" : "transparent",
              borderRadius: 4,
              fontWeight: 500,
            }}
          >{t.label}</button>
        ))}
      </div>

      {tab === "toc" ? (
        <nav aria-label="本章目录">
          <ul className="vstack" style={{ gap: 1, listStyle: "none" }}>
            {toc.map(item => (
              <li key={item.id}>
                <a
                  href={`#${item.id}`}
                  onClick={(e) => { e.preventDefault(); setActiveSection(item.id); }}
                  style={{
                    display: "block",
                    padding: "6px 10px 6px 12px",
                    fontSize: 12.5,
                    color: activeSection === item.id ? "var(--brand)" : "var(--fg-3)",
                    background: activeSection === item.id ? "var(--brand-soft)" : "transparent",
                    borderLeft: `2px solid ${activeSection === item.id ? "var(--brand)" : "transparent"}`,
                    borderRadius: 0,
                    marginLeft: -2,
                    paddingLeft: item.level === 3 ? 24 : 12,
                    transition: "color .15s, background .15s",
                    fontWeight: activeSection === item.id ? 500 : 400,
                  }}
                >{item.text}</a>
              </li>
            ))}
          </ul>
        </nav>
      ) : (
        <nav aria-label="课程章节" className="vstack" style={{ gap: 1 }}>
          {chapters.map(ch => {
            const isCurrent = ch.id === currentId;
            const isLab = ch.type === "lab";
            return (
              <a
                key={ch.id}
                href="#"
                onClick={(e) => { e.preventDefault(); onNavigate(isLab ? "lab" : "chapter", { id: ch.id }); }}
                style={{
                  display: "grid",
                  gridTemplateColumns: "16px 18px minmax(0, 1fr)",
                  gap: 8,
                  alignItems: "center",
                  padding: "6px 10px",
                  fontSize: 12.5,
                  color: isCurrent ? "var(--fg)" : ch.status === "completed" ? "var(--fg-3)" : "var(--fg-2)",
                  background: isCurrent ? "var(--surface-2)" : "transparent",
                  borderRadius: 5,
                  fontWeight: isCurrent ? 500 : 400,
                  transition: "color .15s, background .15s",
                }}
              >
                <span style={{ display: "grid", placeItems: "center",
                  color: ch.status === "completed" ? "var(--ok)" : "var(--fg-4)" }}>
                  {ch.status === "completed"
                    ? <Icon name="check" size={11} />
                    : isCurrent ? <Icon name="play" size={10} style={{ color: "var(--brand)" }} /> : null}
                </span>
                <span className="dim num" style={{ fontSize: 11, textAlign: "center" }}>
                  {isLab ? <Icon name="flask" size={11} style={{ color: "var(--brand)" }} /> : ch.num}
                </span>
                <span style={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                  {ch.title}
                </span>
              </a>
            );
          })}
        </nav>
      )}
    </div>
  );
};

const NavCard = ({ chapter, dir, onClick }) => {
  if (!chapter) {
    return <div style={{ visibility: "hidden" }} aria-hidden="true" />;
  }
  return (
    <button
      onClick={onClick}
      className="card card-hover"
      style={{
        padding: 14, cursor: "pointer",
        textAlign: dir === "next" ? "right" : "left",
      }}
    >
      <div className="hstack dim" style={{
        gap: 4, fontSize: 11.5,
        justifyContent: dir === "next" ? "flex-end" : "flex-start",
      }}>
        {dir === "prev" ? <Icon name="arrowLeft" size={11} /> : null}
        <span>{dir === "prev" ? "上一章" : "下一章"}</span>
        {dir === "next" ? <Icon name="arrowRight" size={11} /> : null}
      </div>
      <div className="h-3" style={{ marginTop: 4, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
        {chapter.title}
      </div>
    </button>
  );
};

const MobileDrawer = ({ children, onClose }) => (
  <div onClick={onClose} style={{
    position: "fixed", inset: 0, zIndex: 80,
    background: "rgba(0,0,0,0.5)",
    display: "flex", justifyContent: "flex-start",
  }}>
    <div onClick={(e) => e.stopPropagation()} style={{
      width: "min(320px, 88vw)", height: "100vh",
      background: "var(--bg-1)", padding: 20, overflowY: "auto",
      borderRight: "1px solid var(--line)",
    }}>
      <div className="hstack" style={{ justifyContent: "space-between", marginBottom: 14 }}>
        <span className="h-3">章节</span>
        <button className="icon-btn" onClick={onClose}><Icon name="x" size={14} /></button>
      </div>
      {children}
    </div>
  </div>
);

const ChapterMarkdownStyle = () => (
  <style>{`
    .md-body { font-size: 15px; line-height: 1.78; color: var(--fg); max-width: 720px; }
    .md-body .md-p { margin: 0 0 18px; color: var(--fg-2); }
    .md-body .md-h2 {
      font-size: 20px; font-weight: 600; letter-spacing: -0.01em;
      margin: 40px 0 14px;
      color: var(--fg);
      padding-top: 8px;
    }
    .md-body .md-h3 { font-size: 16px; font-weight: 600; margin: 28px 0 10px; }
    .md-body .md-list { margin: 0 0 18px 22px; color: var(--fg-2); }
    .md-body .md-list li { margin-bottom: 6px; }
    .md-body .md-code {
      margin: 22px 0;
      background: var(--code-bg);
      border: 1px solid var(--line);
      border-radius: 10px;
      overflow: hidden;
    }
    .md-body .md-code-bar {
      display: flex; align-items: center;
      padding: 8px 12px;
      border-bottom: 1px solid var(--line);
      background: var(--surface);
    }
    .md-body .md-code pre {
      margin: 0; padding: 16px 18px;
      font-size: 12.5px; line-height: 1.65;
      color: var(--fg);
      overflow-x: auto;
    }
    .md-body code { font-family: 'JetBrains Mono', ui-monospace, monospace; }
  `}</style>
);

export default ScreenChapter;
