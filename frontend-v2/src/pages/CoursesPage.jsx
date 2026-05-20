/* Courses listing screen — grid + filters */
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Icon } from '../icons';
import { loadCourses, CATEGORY_MAP, LEVEL_MAP } from '../data';
import { CourseCard } from './HomePage';

const ScreenCourses = () => {
  const navigate = useNavigate();
  const [level, setLevel] = useState("all");
  const [category, setCategory] = useState("all");
  const [view, setView] = useState("grid");
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    setLoading(true);
    loadCourses().then(data => {
      setCourses(data || []);
      setLoading(false);
    });
  }, []);

  const filtered = courses.filter(c =>
    (level === "all" || c.level === level) &&
    (category === "all" || c.category === category)
  );

  return (
    <div className="screen container" style={{ paddingTop: 32, paddingBottom: 80 }}>
      <div style={{ marginBottom: 28 }}>
        <h1 className="h-1">课程</h1>
        <p className="muted" style={{ marginTop: 6, fontSize: 14 }}>6 个阶段，60 章节，43 个实验。按你的进度循序渐进。</p>
      </div>

      {/* Filter bar */}
      <div className="hstack" style={{ gap: 8, marginBottom: 24, flexWrap: "wrap" }}>
        <FilterGroup
          label="难度"
          value={level}
          onChange={setLevel}
          options={[
            { id: "all", label: "全部" },
            { id: "beginner", label: "入门" },
            { id: "intermediate", label: "进阶" },
            { id: "advanced", label: "高级" },
            { id: "expert", label: "专家" },
          ]}
        />
        <FilterGroup
          label="方向"
          value={category}
          onChange={setCategory}
          options={[
            { id: "all", label: "全部" },
            ...Object.entries(CATEGORY_MAP).map(([id, label]) => ({ id, label })),
          ]}
        />
        <div className="spacer" />
        <div className="hstack" style={{ gap: 2, padding: 2, background: "var(--surface)", border: "1px solid var(--line)", borderRadius: 8 }}>
          <button
            className="icon-btn"
            style={{ background: view === "grid" ? "var(--surface-2)" : "transparent", color: view === "grid" ? "var(--fg)" : "var(--fg-3)" }}
            onClick={() => setView("grid")}
            title="网格视图"
          ><Icon name="grid" size={15} /></button>
          <button
            className="icon-btn"
            style={{ background: view === "list" ? "var(--surface-2)" : "transparent", color: view === "list" ? "var(--fg)" : "var(--fg-3)" }}
            onClick={() => setView("list")}
            title="列表视图"
          ><Icon name="list" size={15} /></button>
        </div>
      </div>

      {/* Results */}
      <div className="dim" style={{ fontSize: 12.5, marginBottom: 12 }}>
        共 {filtered.length} 门课程
      </div>

      {view === "grid" ? (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))", gap: 16 }}>
          {filtered.map(c => (
            <CourseCard key={c.id} course={c} onOpen={() => navigate('/courses/' + c.id)} />
          ))}
        </div>
      ) : (
        <div className="card" style={{ overflow: "hidden" }}>
          {filtered.map((c, i) => (
            <CourseRow
              key={c.id}
              course={c}
              isLast={i === filtered.length - 1}
              onOpen={() => navigate('/courses/' + c.id)}
            />
          ))}
        </div>
      )}
    </div>
  );
};

const FilterGroup = ({ label, value, onChange, options }) => (
  <div className="hstack" style={{ gap: 2, padding: 3, background: "var(--surface)", border: "1px solid var(--line)", borderRadius: 8 }}>
    <span className="dim" style={{ fontSize: 11.5, padding: "0 8px 0 6px", borderRight: "1px solid var(--line)", height: 22, lineHeight: "22px" }}>{label}</span>
    {options.map(o => (
      <button
        key={o.id}
        onClick={() => onChange(o.id)}
        style={{
          padding: "4px 10px",
          fontSize: 12.5,
          fontWeight: 500,
          color: value === o.id ? "var(--fg)" : "var(--fg-3)",
          background: value === o.id ? "var(--surface-2)" : "transparent",
          borderRadius: 5,
          transition: "background .15s, color .15s",
        }}
      >{o.label}</button>
    ))}
  </div>
);

const CourseRow = ({ course, isLast, onOpen }) => {
  const lvl = LEVEL_MAP[course.level];
  const pct = Math.round(course.chapters_done / course.chapters_total * 100);
  return (
    <button
      onClick={onOpen}
      style={{
        display: "grid",
        gridTemplateColumns: "44px 60px minmax(0, 1fr) 140px 200px 24px",
        gap: 16,
        alignItems: "center",
        width: "100%",
        padding: "14px 18px",
        textAlign: "left",
        borderBottom: isLast ? "none" : "1px solid var(--line)",
        cursor: "pointer",
        transition: "background .15s",
      }}
      onMouseEnter={(e) => e.currentTarget.style.background = "var(--surface-2)"}
      onMouseLeave={(e) => e.currentTarget.style.background = "transparent"}
    >
      <span style={{
        width: 36, height: 36, borderRadius: 8,
        background: "var(--surface-2)", border: "1px solid var(--line)",
        display: "grid", placeItems: "center", color: "var(--brand)",
      }}>
        <Icon name={course.icon} size={16} />
      </span>
      <span className="mono dim" style={{ fontSize: 11, letterSpacing: 0.04 }}>P{course.phase}</span>
      <span style={{ minWidth: 0 }}>
        <div className="h-3">{course.title}</div>
        <div className="dim" style={{ fontSize: 12, marginTop: 2, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
          {course.description}
        </div>
      </span>
      <span className="hstack dim" style={{ gap: 12, fontSize: 12 }}>
        <span><Icon name="fileText" size={11} /> {course.chapters_total}</span>
        <span><Icon name="flask" size={11} /> {course.lab_total}</span>
        <span><Icon name="clock" size={11} /> {course.duration_hours}h</span>
      </span>
      <span style={{ minWidth: 0 }}>
        <div className="hstack" style={{ justifyContent: "space-between", marginBottom: 4 }}>
          <span style={{ color: lvl.color, fontSize: 11.5, fontWeight: 500 }}>{lvl.text}</span>
          <span className="dim num" style={{ fontSize: 11.5 }}>{pct}%</span>
        </div>
        <div className="prog"><i style={{ width: `${pct}%` }} /></div>
      </span>
      <Icon name="chevronRight" size={14} style={{ color: "var(--fg-4)" }} />
    </button>
  );
};

export default ScreenCourses;
