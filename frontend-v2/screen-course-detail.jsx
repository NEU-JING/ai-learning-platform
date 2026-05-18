/* Course detail — UX FIX: chapter list is primary; right rail = metadata, not duplicate TOC */

const ScreenCourseDetail = ({ params, onNavigate }) => {
  const course = COURSES.find(c => c.id === Number(params?.id)) || COURSES[0];
  const lvl = LEVEL_MAP[course.level];
  const pct = Math.round(course.chapters_done / course.chapters_total * 100);
  const totalMinutes = (course.chapters || []).reduce((s, c) => s + (c.duration || 0), 0);
  const nextChapter = (course.chapters || []).find(c => c.status === "in_progress")
                  || (course.chapters || []).find(c => c.status === "not_started")
                  || (course.chapters || [])[0];

  return (
    <div className="screen container" style={{ paddingTop: 20 }}>
      {/* Breadcrumb */}
      <nav className="crumb" aria-label="路径">
        <a href="#" onClick={(e) => { e.preventDefault(); onNavigate("courses"); }}>课程</a>
        <Icon name="chevronRight" size={12} className="sep" />
        <span className="current">{course.title}</span>
      </nav>

      {/* Header */}
      <header style={{ padding: "20px 0 32px", borderBottom: "1px solid var(--line)" }}>
        <div className="hstack" style={{ gap: 12, marginBottom: 14 }}>
          <span className="mono dim" style={{ fontSize: 11.5, letterSpacing: 0.04 }}>PHASE {course.phase}</span>
          <span className="tag" style={{ color: lvl.color, background: "transparent" }}>
            <span className="dot" style={{ background: lvl.color, boxShadow: "none" }} />
            {lvl.text}
          </span>
          <span className="tag">{CATEGORY_MAP[course.category]}</span>
        </div>
        <h1 className="h-display" style={{ fontSize: 32 }}>{course.title}</h1>
        <p className="muted" style={{ fontSize: 15, marginTop: 12, maxWidth: 720, lineHeight: 1.65 }}>
          {course.description}
        </p>
        <div className="hstack dim" style={{ gap: 20, fontSize: 13, marginTop: 18 }}>
          <span className="hstack" style={{ gap: 5 }}><Icon name="fileText" size={13} /> {course.chapters_total} 章节</span>
          <span className="hstack" style={{ gap: 5 }}><Icon name="flask" size={13} /> {course.lab_total} 实验</span>
          <span className="hstack" style={{ gap: 5 }}><Icon name="clock" size={13} /> 约 {course.duration_hours} 小时 · {totalMinutes} 分钟内容</span>
          <span className="hstack" style={{ gap: 5 }}><Icon name="users" size={13} /> {course.students.toLocaleString()} 在学</span>
          <span className="hstack" style={{ gap: 5 }}><Icon name="award" size={13} /> {course.rating}</span>
        </div>
      </header>

      {/* Two-col layout: left = chapter list (primary), right = sidecar */}
      <div className="layout-2col">
        <main>
          <ChapterListPanel
            course={course}
            onOpenChapter={(ch) => onNavigate(ch.type === "lab" ? "lab" : "chapter", { id: ch.id })}
          />
        </main>

        <aside className="sidebar">
          <div className="sidebar-sticky vstack" style={{ gap: 16 }}>
            <CourseProgressCard course={course} pct={pct} nextChapter={nextChapter} onContinue={() => nextChapter && onNavigate(nextChapter.type === "lab" ? "lab" : "chapter", { id: nextChapter.id })} />
            <CourseFactsCard course={course} totalMinutes={totalMinutes} />
            <CourseInstructorCard />
          </div>
        </aside>
      </div>
    </div>
  );
};

const ChapterListPanel = ({ course, onOpenChapter }) => {
  const [filter, setFilter] = React.useState("all"); // all | unread | lab
  const chapters = course.chapters || [];

  const visible = chapters.filter(ch =>
    filter === "all" ? true
    : filter === "unread" ? ch.status !== "completed"
    : filter === "lab" ? ch.type === "lab"
    : true
  );

  return (
    <div>
      <div className="hstack" style={{ marginBottom: 16, gap: 8, justifyContent: "space-between" }}>
        <h2 className="h-2">章节大纲</h2>
        <div className="hstack" style={{ gap: 2, padding: 2, background: "var(--surface)", border: "1px solid var(--line)", borderRadius: 6 }}>
          {[
            { id: "all", label: "全部", n: chapters.length },
            { id: "unread", label: "未完成", n: chapters.filter(c => c.status !== "completed").length },
            { id: "lab", label: "实验", n: chapters.filter(c => c.type === "lab").length },
          ].map(t => (
            <button
              key={t.id}
              onClick={() => setFilter(t.id)}
              style={{
                padding: "3px 10px", fontSize: 12,
                color: filter === t.id ? "var(--fg)" : "var(--fg-3)",
                background: filter === t.id ? "var(--surface-2)" : "transparent",
                borderRadius: 4,
              }}
            >{t.label} <span className="num dim">({t.n})</span></button>
          ))}
        </div>
      </div>

      {chapters.length === 0 ? (
        <EmptyChapters />
      ) : (
        <ol className="vstack" style={{ gap: 4, listStyle: "none" }}>
          {visible.map((ch) => (
            <ChapterItem key={ch.id} chapter={ch} onOpen={() => onOpenChapter(ch)} />
          ))}
        </ol>
      )}
    </div>
  );
};

const ChapterItem = ({ chapter, onOpen }) => {
  const isLab = chapter.type === "lab";
  const status = chapter.status;
  return (
    <li>
      <button
        onClick={onOpen}
        style={{
          width: "100%",
          display: "grid",
          gridTemplateColumns: "auto 36px minmax(0,1fr) auto auto",
          gap: 14,
          alignItems: "center",
          padding: "12px 16px 12px 13px",
          background: "var(--surface)",
          border: "1px solid var(--line)",
          borderLeft: isLab ? "3px solid var(--brand)" : "1px solid var(--line)",
          borderRadius: "var(--radius)",
          textAlign: "left",
          transition: "background .15s, border-color .15s",
          cursor: "pointer",
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.background = "var(--surface-2)";
          e.currentTarget.style.borderColor = "var(--line-2)";
          if (isLab) e.currentTarget.style.borderLeftColor = "var(--brand)";
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.background = "var(--surface)";
          e.currentTarget.style.borderColor = "var(--line)";
          if (isLab) e.currentTarget.style.borderLeftColor = "var(--brand)";
        }}
      >
        {/* Status indicator */}
        <span style={{ width: 18, display: "grid", placeItems: "center", color:
          status === "completed" ? "var(--ok)" :
          status === "in_progress" ? "var(--brand)" :
          "var(--fg-4)" }}>
          {status === "completed" ? <Icon name="checkCircle" size={16} />
            : status === "in_progress" ? <Icon name="play" size={13} />
            : <Icon name="circle" size={15} />}
        </span>

        {/* Chapter number / lab icon */}
        <span style={{
          width: 30, height: 30, borderRadius: 7,
          background: isLab ? "var(--brand-soft)" : "var(--surface-2)",
          border: "1px solid var(--line)",
          color: isLab ? "var(--brand)" : "var(--fg-2)",
          display: "grid", placeItems: "center",
          fontSize: 12.5, fontWeight: 600,
          fontVariantNumeric: "tabular-nums",
        }}>
          {isLab ? <Icon name="flask" size={14} /> : chapter.num}
        </span>

        {/* Title */}
        <span style={{ minWidth: 0 }}>
          <div style={{
            fontSize: 14, fontWeight: 500,
            color: status === "completed" ? "var(--fg-2)" : "var(--fg)",
            display: "flex", alignItems: "center", gap: 8,
          }}>
            <span style={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{chapter.title}</span>
            {isLab && <span className="tag tag-brand" style={{ height: 18, padding: "0 6px", fontSize: 10.5, fontWeight: 600 }}>LAB</span>}
          </div>
          <div className="dim" style={{ fontSize: 12, marginTop: 2 }}>
            {isLab ? "实验课 · 提交评测" : "阅读章节"}
          </div>
        </span>

        {/* Duration */}
        <span className="dim hstack" style={{ gap: 4, fontSize: 12 }}>
          <Icon name="clock" size={11} />
          <span className="num">{chapter.duration}m</span>
        </span>

        {/* Chevron */}
        <span style={{ color: "var(--fg-4)" }}><Icon name="chevronRight" size={14} /></span>
      </button>
    </li>
  );
};

const CourseProgressCard = ({ course, pct, nextChapter, onContinue }) => (
  <div className="card" style={{ padding: 18 }}>
    <div className="hstack" style={{ justifyContent: "space-between", marginBottom: 12 }}>
      <span className="h-3">课程进度</span>
      <span className="mono num" style={{ fontSize: 13, color: "var(--brand)" }}>{pct}%</span>
    </div>
    <div className="prog prog-xl" role="progressbar" aria-valuenow={pct} aria-valuemin={0} aria-valuemax={100}>
      <i style={{ width: `${pct}%` }} />
    </div>
    <div className="hstack dim" style={{ marginTop: 10, fontSize: 12, justifyContent: "space-between" }}>
      <span>{course.chapters_done} 已完成</span>
      <span>{course.chapters_total - course.chapters_done} 剩余</span>
    </div>
    {nextChapter && (
      <>
        <div className="divider" style={{ margin: "16px 0" }} />
        <div className="dim" style={{ fontSize: 11.5, marginBottom: 4 }}>下一章</div>
        <div className="h-3" style={{ marginBottom: 12 }}>{nextChapter.title}</div>
        <button className="btn btn-primary" style={{ width: "100%" }} onClick={onContinue}>
          <Icon name="play" size={12} />
          {pct === 0 ? "开始学习" : pct === 100 ? "复习课程" : "继续学习"}
        </button>
      </>
    )}
    <button className="btn btn-ghost btn-sm" style={{ width: "100%", marginTop: 6 }}>
      <Icon name="bookmark" size={12} /> 收藏课程
    </button>
  </div>
);

const CourseFactsCard = ({ course, totalMinutes }) => (
  <div className="card" style={{ padding: 18 }}>
    <div className="h-3" style={{ marginBottom: 14 }}>课程信息</div>
    <dl className="vstack" style={{ gap: 10 }}>
      <Fact label="阶段" value={`Phase ${course.phase}`} />
      <Fact label="方向" value={CATEGORY_MAP[course.category]} />
      <Fact label="时长" value={`${course.duration_hours} 小时`} />
      <Fact label="章节" value={`${course.chapters_total} 个`} />
      <Fact label="实验" value={`${course.lab_total} 个`} />
      <Fact label="评分" value={`${course.rating} / 5.0`} />
      <Fact label="在学" value={`${course.students.toLocaleString()} 人`} />
    </dl>
  </div>
);

const Fact = ({ label, value }) => (
  <div className="hstack" style={{ justifyContent: "space-between", fontSize: 12.5 }}>
    <dt className="dim">{label}</dt>
    <dd style={{ color: "var(--fg)", fontVariantNumeric: "tabular-nums" }}>{value}</dd>
  </div>
);

const CourseInstructorCard = () => (
  <div className="card" style={{ padding: 18 }}>
    <div className="h-3" style={{ marginBottom: 12 }}>教研团队</div>
    <div className="hstack" style={{ gap: 10 }}>
      <div className="avatar" style={{ width: 36, height: 36, fontSize: 13 }}>HM</div>
      <div style={{ minWidth: 0 }}>
        <div style={{ fontSize: 13, fontWeight: 500 }}>Hermes 团队</div>
        <div className="dim" style={{ fontSize: 11.5, marginTop: 1 }}>资深 AI 工程师 · 5 年 Anthropic Claude 应用经验</div>
      </div>
    </div>
  </div>
);

const EmptyChapters = () => (
  <div className="card" style={{ padding: "60px 20px", textAlign: "center" }}>
    <div style={{ color: "var(--fg-4)", marginBottom: 12 }}>
      <Icon name="layers" size={28} />
    </div>
    <div className="h-3">课程内容编写中</div>
    <p className="dim" style={{ fontSize: 13, marginTop: 6 }}>
      本阶段的章节正在录制和审核中。<br />
      关注更新通知，第一时间收到上线消息。
    </p>
    <button className="btn btn-secondary btn-sm" style={{ marginTop: 16 }}>
      <Icon name="bell" size={12} /> 关注上线通知
    </button>
  </div>
);

Object.assign(window, { ScreenCourseDetail });
