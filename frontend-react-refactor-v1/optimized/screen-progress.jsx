/* Progress dashboard — stats, weekly activity, course breakdown, recent activity */

const ScreenProgress = ({ onNavigate }) => {
  const s = PROGRESS_STATS;
  const maxWeekly = Math.max(...s.weekly);
  const totalHours = (s.total_minutes / 60).toFixed(1);

  return (
    <div className="screen container" style={{ paddingTop: 32, paddingBottom: 80 }}>
      <header style={{ marginBottom: 28 }}>
        <h1 className="h-1">学习进度</h1>
        <p className="muted" style={{ marginTop: 6, fontSize: 14 }}>
          坚持学习 {s.streak_days} 天 · 累计 {totalHours} 小时 · 完成 {s.chapters_completed} 章 / {s.labs_completed} 实验
        </p>
      </header>

      {/* Stats row */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12, marginBottom: 24 }}>
        <StatCard icon="flame"    label="连续天数" value={s.streak_days}      unit="天"  tone="warn" />
        <StatCard icon="clock"    label="学习时长" value={totalHours}         unit="h"   tone="brand" />
        <StatCard icon="fileText" label="完成章节" value={s.chapters_completed} unit={`/60`} tone="ok" />
        <StatCard icon="flask"    label="完成实验" value={s.labs_completed}     unit={`/43`} tone="brand" />
      </div>

      {/* Activity chart + path overview */}
      <div style={{ display: "grid", gridTemplateColumns: "1.4fr 1fr", gap: 16, marginBottom: 24 }}>
        <ActivityChart weekly={s.weekly} maxWeekly={maxWeekly} />
        <PathOverview onNavigate={onNavigate} />
      </div>

      {/* Two-col: course progress + recent activity */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
        <CourseProgressList onNavigate={onNavigate} />
        <RecentActivity items={s.recent} />
      </div>
    </div>
  );
};

const StatCard = ({ icon, label, value, unit, tone }) => {
  const colors = {
    brand: "var(--brand)",
    ok:    "var(--ok)",
    warn:  "var(--warn)",
    err:   "var(--err)",
  };
  return (
    <div className="card" style={{ padding: 18 }}>
      <div className="hstack" style={{ justifyContent: "space-between" }}>
        <span className="dim" style={{ fontSize: 12 }}>{label}</span>
        <span style={{ color: colors[tone] }}><Icon name={icon} size={14} /></span>
      </div>
      <div className="hstack" style={{ alignItems: "baseline", gap: 4, marginTop: 8 }}>
        <span className="num" style={{ fontSize: 28, fontWeight: 600, letterSpacing: "-0.02em", color: "var(--fg)" }}>{value}</span>
        <span className="dim" style={{ fontSize: 13 }}>{unit}</span>
      </div>
    </div>
  );
};

const ActivityChart = ({ weekly, maxWeekly }) => {
  const days = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"];
  return (
    <div className="card" style={{ padding: 20 }}>
      <div className="hstack" style={{ justifyContent: "space-between" }}>
        <span className="h-3">本周活跃度</span>
        <div className="hstack dim" style={{ gap: 14, fontSize: 12 }}>
          <span className="hstack" style={{ gap: 4 }}>
            <span style={{ width: 8, height: 8, borderRadius: 2, background: "var(--brand)" }} />
            学习时长
          </span>
          <span>累计 {weekly.reduce((a, b) => a + b, 0)} 分钟</span>
        </div>
      </div>
      <div style={{
        marginTop: 24,
        display: "grid",
        gridTemplateColumns: "repeat(7, 1fr)",
        gap: 8,
        height: 160,
        alignItems: "end",
      }}>
        {weekly.map((m, i) => {
          const h = (m / maxWeekly) * 100;
          const isToday = i === 4; // pretend Friday is today
          return (
            <div key={i} style={{ display: "flex", flexDirection: "column", alignItems: "center", height: "100%", justifyContent: "flex-end" }}>
              <span className="dim num" style={{ fontSize: 10.5, marginBottom: 6 }}>{m}m</span>
              <div style={{
                width: "100%",
                height: `${h}%`,
                background: isToday ? "var(--brand)" : "var(--brand-soft-2)",
                borderRadius: 4,
                transition: "height .5s ease",
                position: "relative",
              }}>
                {isToday && (
                  <span style={{
                    position: "absolute", top: -6, left: "50%", transform: "translateX(-50%)",
                    width: 4, height: 4, borderRadius: "50%", background: "var(--brand)",
                    boxShadow: "0 0 0 3px var(--brand-soft)",
                  }} />
                )}
              </div>
              <span className="dim" style={{ fontSize: 11, marginTop: 8, color: isToday ? "var(--fg)" : "var(--fg-3)" }}>{days[i]}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
};

const PathOverview = ({ onNavigate }) => {
  const done = COURSES.reduce((s, c) => s + c.chapters_done, 0);
  const total = COURSES.reduce((s, c) => s + c.chapters_total, 0);
  const pct = Math.round(done / total * 100);
  return (
    <div className="card" style={{ padding: 20, display: "flex", flexDirection: "column" }}>
      <div className="hstack" style={{ justifyContent: "space-between" }}>
        <span className="h-3">总进度</span>
        <span className="mono num" style={{ fontSize: 13, color: "var(--brand)" }}>{pct}%</span>
      </div>

      {/* Circular progress */}
      <div style={{ flex: 1, display: "grid", placeItems: "center", padding: "20px 0" }}>
        <div style={{ position: "relative", width: 160, height: 160 }}>
          <svg width="160" height="160" viewBox="0 0 160 160" style={{ transform: "rotate(-90deg)" }}>
            <circle cx="80" cy="80" r="68" fill="none" stroke="var(--surface-3)" strokeWidth="10" />
            <circle
              cx="80" cy="80" r="68"
              fill="none"
              stroke="var(--brand)"
              strokeWidth="10"
              strokeLinecap="round"
              strokeDasharray={`${(pct / 100) * 2 * Math.PI * 68} ${2 * Math.PI * 68}`}
              style={{ transition: "stroke-dasharray .8s ease" }}
            />
          </svg>
          <div style={{
            position: "absolute", inset: 0,
            display: "flex", flexDirection: "column",
            alignItems: "center", justifyContent: "center",
          }}>
            <span className="num" style={{ fontSize: 32, fontWeight: 600, letterSpacing: "-0.02em" }}>{done}</span>
            <span className="dim" style={{ fontSize: 12, marginTop: 2 }}>/ {total} 章节</span>
          </div>
        </div>
      </div>
      <button className="btn btn-secondary btn-sm" style={{ width: "100%" }} onClick={() => onNavigate("courses")}>
        继续下一章 <Icon name="arrowRight" size={11} />
      </button>
    </div>
  );
};

const CourseProgressList = ({ onNavigate }) => (
  <div className="card" style={{ padding: 20 }}>
    <div className="hstack" style={{ justifyContent: "space-between", marginBottom: 14 }}>
      <span className="h-3">课程进度</span>
      <span className="dim" style={{ fontSize: 11.5 }}>按阶段</span>
    </div>
    <ul className="vstack" style={{ gap: 10, listStyle: "none" }}>
      {COURSES.map(c => {
        const pct = Math.round(c.chapters_done / c.chapters_total * 100);
        return (
          <li key={c.id}>
            <button
              onClick={() => onNavigate("course", { id: c.id })}
              style={{
                width: "100%", textAlign: "left",
                padding: "10px 4px",
                display: "grid",
                gridTemplateColumns: "28px minmax(0, 1fr) 60px 60px",
                gap: 12, alignItems: "center",
                borderRadius: 6, transition: "background .15s",
              }}
              onMouseEnter={(e) => e.currentTarget.style.background = "var(--surface-2)"}
              onMouseLeave={(e) => e.currentTarget.style.background = "transparent"}
            >
              <span style={{
                width: 26, height: 26, borderRadius: 6,
                background: "var(--surface-2)", border: "1px solid var(--line)",
                display: "grid", placeItems: "center", color: "var(--brand)",
              }}>
                <Icon name={c.icon} size={13} />
              </span>
              <span style={{ minWidth: 0 }}>
                <div style={{ fontSize: 13, fontWeight: 500, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                  {c.title}
                </div>
                <div className="dim" style={{ fontSize: 11.5, marginTop: 2 }}>
                  Phase {c.phase} · {c.chapters_done}/{c.chapters_total} 章
                </div>
              </span>
              <span className="prog">
                <i style={{ width: `${pct}%` }} />
              </span>
              <span className="num dim" style={{ fontSize: 12, textAlign: "right" }}>{pct}%</span>
            </button>
          </li>
        );
      })}
    </ul>
  </div>
);

const RecentActivity = ({ items }) => (
  <div className="card" style={{ padding: 20 }}>
    <div className="hstack" style={{ justifyContent: "space-between", marginBottom: 14 }}>
      <span className="h-3">最近活动</span>
      <button className="btn btn-ghost btn-sm">查看全部</button>
    </div>
    <ul className="vstack" style={{ gap: 0, listStyle: "none" }}>
      {items.map((it, i) => {
        const isLab = it.kind === "lab";
        return (
          <li key={i} style={{
            display: "grid",
            gridTemplateColumns: "28px minmax(0,1fr) auto",
            gap: 12, alignItems: "center",
            padding: "12px 4px",
            borderBottom: i < items.length - 1 ? "1px solid var(--line)" : "none",
          }}>
            <span style={{
              width: 26, height: 26, borderRadius: 6,
              background: isLab ? "var(--brand-soft)" : "var(--surface-2)",
              border: "1px solid var(--line)",
              display: "grid", placeItems: "center",
              color: isLab ? "var(--brand)" : "var(--fg-2)",
            }}>
              <Icon name={isLab ? "flask" : "fileText"} size={13} />
            </span>
            <span style={{ minWidth: 0 }}>
              <div style={{ fontSize: 13, fontWeight: 500, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                {it.title}
              </div>
              <div className="dim" style={{ fontSize: 11.5, marginTop: 2 }}>
                {it.course} · {it.when}
              </div>
            </span>
            {it.score !== undefined ? (
              <span className="tag tag-ok" style={{ height: 22 }}>
                <Icon name="award" size={11} /> {it.score}
              </span>
            ) : (
              <span className="tag" style={{ height: 22, color: it.progress === 100 ? "var(--ok)" : "var(--brand)" }}>
                {it.progress === 100
                  ? <><Icon name="check" size={11} /> 完成</>
                  : <><Icon name="play" size={10} /> {it.progress}%</>}
              </span>
            )}
          </li>
        );
      })}
    </ul>
  </div>
);

Object.assign(window, { ScreenProgress });
