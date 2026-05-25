/* Lab screen — Code editor + test runner + AI hint sidebar */
import React, { useState, useEffect } from 'react';
import { Icon } from '../icons';
import { loadLab, loadCourses, CURRENT, LEVEL_MAP, CATEGORY_MAP } from '../data';
import { useNavigate, useParams } from 'react-router-dom';

const ScreenLab = () => {
  const navigate = useNavigate();
  const { id } = useParams();
  const [lab, setLab] = useState(null);
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [results, setResults] = useState([]);
  const [code, setCode] = useState('');
  const [tab, setTab] = useState("output");
  const [running, setRunning] = useState(false);
  const [aiOpen, setAiOpen] = useState(false);
  
  useEffect(() => {
    setLoading(true);
    Promise.all([
      loadLab(id),
      loadCourses(),
    ]).then(([labData, coursesData]) => {
      if (labData) {
        setLab(labData);
        const testCases = labData.test_cases || labData.tests || [];
        setResults(testCases);
        setCode(labData.starter_code || labData.starter || '');
      }
      setCourses(coursesData || []);
      setLoading(false);
    });
  }, [id]);
  const [output, setOutput] = React.useState(
`>>> 加载数据集 creditcard.csv
shape = (284807, 31)
正类样本: 492 (0.17%)
负类样本: 284,315 (99.83%)
>>> 切分训练 / 测试集 (stratify=y)
X_train: (227845, 30)  X_test: (56962, 30)
>>> 训练 LogisticRegression(max_iter=1000)
[ConvergenceWarning] lbfgs failed to converge. 建议增加迭代次数或缩放特征。
>>> 评估
              precision    recall  f1-score   support
           0       1.00      1.00      1.00     56863
           1       0.64      0.87      0.74        99
`
  );

  const passed = results.filter(r => r.status === "pass").length;
  const failed = results.filter(r => r.status === "fail").length;
  const total = results.length;

  const runSimulation = () => {
    setRunning(true);
    setResults(results.map(r => ({ ...r, status: "pending" })));
    setOutput("⏳ 沙箱启动中…\n");
    setTab("tests");

    const stages = [
      () => setOutput(o => o + ">>> 安装依赖 pandas scikit-learn imbalanced-learn…\n"),
      () => setOutput(o => o + ">>> 加载数据集 creditcard.csv\n"),
      () => setResults(prev => prev.map((r, i) => i === 0 ? { ...r, status: "pass" } : r)),
      () => setResults(prev => prev.map((r, i) => i === 1 ? { ...r, status: "pass" } : r)),
      () => setOutput(o => o + ">>> 训练模型 (耗时 2.8s)…\n"),
      () => setResults(prev => prev.map((r, i) => i === 2 ? { ...r, status: "pass" } : r)),
      () => setResults(prev => prev.map((r, i) => i === 3 ? { ...r, status: "pass" } : r)),
      () => setResults(prev => prev.map((r, i) => i === 4 ? { ...r, status: "fail" } : r)),
      () => setResults(prev => prev.map((r, i) => i === 5 ? { ...r, status: "pass" } : r)),
      () => { setRunning(false); setOutput(o => o + ">>> 完成。5/6 通过，1 失败。\n"); },
    ];
    stages.forEach((s, i) => setTimeout(s, 350 * (i + 1)));
  };

  return (
    <div className="screen">
      {/* Top sub-bar */}
      <div style={{
        position: "sticky", top: 56, zIndex: 40,
        background: "color-mix(in oklab, var(--bg) 92%, transparent)",
        backdropFilter: "blur(12px)",
        borderBottom: "1px solid var(--line)",
      }}>
        <div className="container hstack" style={{ height: 48, gap: 12 }}>
          <nav className="crumb" style={{ flex: 1, minWidth: 0 }}>
            <a href="#" onClick={(e) => { e.preventDefault(); navigate('/courses'); }}>课程</a>
            <Icon name="chevronRight" size={11} className="sep" />
            <a href="#" onClick={(e) => { e.preventDefault(); navigate('/courses/3'); }}>{lab.course_title}</a>
            <Icon name="chevronRight" size={11} className="sep" />
            <span className="current">{lab.title}</span>
          </nav>
          <span className="tag tag-brand"><Icon name="flask" size={11} /> 实验</span>
          <button className="btn btn-ghost btn-sm" onClick={() => setAiOpen(true)}>
            <Icon name="sparkles" size={12} /> AI 助手
          </button>
        </div>
      </div>

      {/* Main lab workspace */}
      <div className="container" style={{ padding: "20px 24px 80px" }}>
        <LabHeader lab={lab} passed={passed} total={total} running={running} />

        <div style={{
          marginTop: 18,
          display: "grid",
          gridTemplateColumns: "320px minmax(0, 1fr)",
          gap: 16,
          minHeight: 620,
        }}>
          <LabBriefPanel lab={lab} />

          <div style={{
            display: "grid",
            gridTemplateRows: "minmax(380px, 1fr) 280px",
            gap: 16,
          }}>
            <CodeEditor
              code={code}
              onChange={setCode}
              onRun={runSimulation}
              running={running}
            />
            <ResultPanel
              tab={tab}
              setTab={setTab}
              results={results}
              output={output}
              passed={passed}
              failed={failed}
              total={total}
              running={running}
            />
          </div>
        </div>
      </div>

      {aiOpen && <AIAssistant onClose={() => setAiOpen(false)} />}
    </div>
  );
};

const LabHeader = ({ lab, passed, total, running }) => {
  const allPassed = passed === total;
  return (
    <div className="hstack" style={{ justifyContent: "space-between", flexWrap: "wrap", gap: 12 }}>
      <div>
        <div className="dim mono" style={{ fontSize: 11.5, letterSpacing: 0.04 }}>LAB · {lab.difficulty.toUpperCase()}</div>
        <h1 className="h-1" style={{ marginTop: 4 }}>{lab.title}</h1>
        <div className="hstack dim" style={{ gap: 16, fontSize: 13, marginTop: 6 }}>
          <span className="hstack" style={{ gap: 5 }}><Icon name="clock" size={12} /> 约 {lab.duration} 分钟</span>
          <span className="hstack" style={{ gap: 5 }}><Icon name="terminal" size={12} /> Python 3.11 · Docker 沙箱</span>
          <span className="hstack" style={{ gap: 5 }}><Icon name="check" size={12} /> {total} 项测试</span>
        </div>
      </div>
      <div className="hstack" style={{ gap: 8 }}>
        <span className="tag" style={{ height: 28, fontSize: 12, padding: "0 10px" }}>
          {running ? <><span className="dot" style={{ background: "var(--warn)", boxShadow: "0 0 0 3px rgba(251,191,36,0.18)" }} /> 运行中</> :
           allPassed ? <><Icon name="checkCircle" size={12} style={{ color: "var(--ok)" }}/> 全部通过</> :
           <><Icon name="circle" size={12} style={{ color: "var(--fg-3)" }}/> {passed}/{total} 通过</>}
        </span>
        <button className="btn btn-secondary"><Icon name="refresh" size={12} /> 重置</button>
        <button className="btn btn-secondary"><Icon name="send" size={12} /> 提交评测</button>
      </div>
    </div>
  );
};

const LabBriefPanel = ({ lab }) => (
  <aside className="card" style={{ padding: 18, alignSelf: "start" }}>
    <div className="h-3" style={{ marginBottom: 10 }}>任务说明</div>
    <p className="muted" style={{ fontSize: 13, lineHeight: 1.65 }}>{lab.description}</p>

    <div className="divider" style={{ margin: "16px 0" }} />

    <div className="h-3" style={{ marginBottom: 10 }}>评测要求</div>
    <ul className="vstack" style={{ gap: 6, listStyle: "none", fontSize: 12.5 }}>
      <li className="hstack"><span className="dot dot-brand" /><span style={{ marginLeft: 8 }}>Recall ≥ 0.85</span></li>
      <li className="hstack"><span className="dot dot-brand" /><span style={{ marginLeft: 8 }}>Precision ≥ 0.70</span></li>
      <li className="hstack"><span className="dot dot-brand" /><span style={{ marginLeft: 8 }}>使用 stratified split 保持类别比例</span></li>
      <li className="hstack"><span className="dot dot-brand" /><span style={{ marginLeft: 8 }}>避免数据泄露（scaler 在 split 后 fit）</span></li>
    </ul>

    <div className="divider" style={{ margin: "16px 0" }} />

    <details>
      <summary style={{
        cursor: "pointer", display: "flex", alignItems: "center", gap: 6,
        fontSize: 13, fontWeight: 500, color: "var(--warn)",
        listStyle: "none",
      }}>
        <Icon name="zap" size={13} />
        <span>提示（{lab.hints.length}）</span>
      </summary>
      <ul className="vstack" style={{ gap: 8, marginTop: 12, listStyle: "none", fontSize: 12.5, color: "var(--fg-2)", paddingLeft: 0 }}>
        {lab.hints.map((h, i) => (
          <li key={i} className="hstack" style={{ alignItems: "flex-start", gap: 8 }}>
            <span className="dim mono num" style={{ fontSize: 11 }}>{String(i + 1).padStart(2, "0")}</span>
            <span style={{ lineHeight: 1.55 }}>{h}</span>
          </li>
        ))}
      </ul>
    </details>
  </aside>
);

const CodeEditor = ({ code, onChange, onRun, running }) => {
  const lines = code.split("\n");
  return (
    <div className="card" style={{ display: "flex", flexDirection: "column", overflow: "hidden", background: "var(--code-bg)" }}>
      <div className="hstack" style={{
        padding: "8px 12px", borderBottom: "1px solid var(--line)",
        background: "var(--surface)", gap: 8,
      }}>
        <span className="dot" style={{ background: "#ff5f57", boxShadow: "none" }} />
        <span className="dot" style={{ background: "#febc2e", boxShadow: "none" }} />
        <span className="dot" style={{ background: "#28c840", boxShadow: "none" }} />
        <span className="mono dim" style={{ fontSize: 11.5, marginLeft: 6 }}>solution.py</span>
        <span className="tag" style={{ height: 20, fontSize: 10.5, padding: "0 6px" }}>
          <Icon name="python" size={10} /> Python 3.11
        </span>
        <span className="spacer" />
        <button className="btn btn-ghost btn-sm" style={{ height: 24, padding: "0 8px" }}>
          <Icon name="refresh" size={11} />
        </button>
        <button className="btn btn-ghost btn-sm" style={{ height: 24, padding: "0 8px" }}>
          <Icon name="copy" size={11} />
        </button>
        <button
          className="btn btn-primary btn-sm"
          style={{ height: 24, padding: "0 10px" }}
          onClick={onRun}
          disabled={running}
        >
          {running ? <><Icon name="pause" size={10} /> 运行中</> : <><Icon name="play" size={10} /> 运行</>}
        </button>
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "40px 1fr", flex: 1, overflow: "hidden" }}>
        <div className="mono" style={{
          padding: "12px 8px", textAlign: "right",
          color: "var(--fg-4)", fontSize: 12, lineHeight: 1.65,
          borderRight: "1px solid var(--line)",
          background: "var(--code-bg)",
          userSelect: "none",
        }}>
          {lines.map((_, i) => <div key={i}>{i + 1}</div>)}
        </div>
        <textarea
          value={code}
          onChange={(e) => onChange(e.target.value)}
          spellCheck="false"
          className="mono"
          style={{
            border: 0, outline: 0, resize: "none",
            padding: 12, fontSize: 12.5, lineHeight: 1.65,
            background: "var(--code-bg)", color: "var(--fg)",
            width: "100%", height: "100%",
          }}
        />
      </div>
    </div>
  );
};

const ResultPanel = ({ tab, setTab, results, output, passed, failed, total, running }) => (
  <div className="card" style={{ display: "flex", flexDirection: "column", overflow: "hidden" }}>
    <div className="hstack" style={{ borderBottom: "1px solid var(--line)", background: "var(--surface)" }}>
      {[
        { id: "tests",   label: "测试结果", count: `${passed}/${total}`, tone: failed ? "warn" : "ok" },
        { id: "output",  label: "运行输出", count: null },
        { id: "console", label: "终端",   count: null },
      ].map(t => (
        <button
          key={t.id}
          onClick={() => setTab(t.id)}
          style={{
            padding: "10px 16px",
            fontSize: 12.5, fontWeight: 500,
            color: tab === t.id ? "var(--fg)" : "var(--fg-3)",
            borderBottom: `2px solid ${tab === t.id ? "var(--brand)" : "transparent"}`,
            marginBottom: -1,
            display: "flex", alignItems: "center", gap: 6,
          }}
        >
          {t.label}
          {t.count && (
            <span className={`tag tag-${t.tone}`} style={{ height: 18, fontSize: 10.5, padding: "0 6px" }}>{t.count}</span>
          )}
        </button>
      ))}
      <span className="spacer" />
      {running && <span className="dim hstack" style={{ gap: 6, fontSize: 11.5, paddingRight: 12 }}>
        <span className="dot" style={{ background: "var(--warn)", boxShadow: "0 0 0 3px rgba(251,191,36,0.18)" }} />
        实时评测中
      </span>}
    </div>

    <div style={{ flex: 1, overflowY: "auto" }}>
      {tab === "tests" && <TestsList results={results} />}
      {tab === "output" && (
        <pre className="mono" style={{
          margin: 0, padding: 16, fontSize: 12, lineHeight: 1.65,
          color: "var(--fg-2)", whiteSpace: "pre-wrap",
        }}>{output}</pre>
      )}
      {tab === "console" && (
        <div className="mono" style={{ padding: 16, fontSize: 12 }}>
          <div className="dim">$ python -m pytest solution.py -v</div>
          <div className="dim" style={{ marginTop: 4 }}>$ docker exec sandbox python -c "import sklearn; print(sklearn.__version__)"</div>
          <div style={{ marginTop: 4 }}>1.4.0</div>
        </div>
      )}
    </div>
  </div>
);

const TestsList = ({ results }) => (
  <ul className="vstack" style={{ gap: 2, listStyle: "none", padding: 8 }}>
    {results.map((r, i) => (
      <li key={i}>
        <div style={{
          display: "grid",
          gridTemplateColumns: "20px minmax(0, 1fr) 80px",
          gap: 12,
          alignItems: "center",
          padding: "10px 12px",
          background: r.status === "fail" ? "rgba(248,113,113,0.05)" : "transparent",
          border: `1px solid ${r.status === "fail" ? "rgba(248,113,113,0.18)" : "transparent"}`,
          borderRadius: 6,
        }}>
          <span style={{ display: "grid", placeItems: "center" }}>
            {r.status === "pass"    && <Icon name="checkCircle" size={14} style={{ color: "var(--ok)" }} />}
            {r.status === "fail"    && <Icon name="x" size={14} style={{ color: "var(--err)" }} />}
            {r.status === "pending" && <Icon name="circleDashed" size={14} style={{ color: "var(--fg-3)" }} />}
          </span>
          <div style={{ minWidth: 0 }}>
            <div className="mono" style={{ fontSize: 12.5, color: "var(--fg)" }}>{r.name}</div>
            <div className="dim" style={{ fontSize: 11.5, marginTop: 2 }}>{r.desc}</div>
            {r.error && (
              <div className="mono" style={{
                marginTop: 6, padding: 8,
                background: "rgba(248,113,113,0.08)",
                border: "1px solid rgba(248,113,113,0.2)",
                borderRadius: 5,
                fontSize: 11.5, color: "var(--err)",
              }}>{r.error}</div>
            )}
          </div>
          <span className="dim num" style={{ fontSize: 11.5, textAlign: "right" }}>
            {r.status === "pass" || r.status === "fail" ? `${r.time}ms` : "—"}
          </span>
        </div>
      </li>
    ))}
  </ul>
);

const AIAssistant = ({ onClose }) => (
  <div onClick={onClose} style={{
    position: "fixed", inset: 0, zIndex: 90,
    background: "rgba(0,0,0,0.5)", display: "flex", justifyContent: "flex-end",
  }}>
    <aside onClick={(e) => e.stopPropagation()} style={{
      width: "min(420px, 92vw)", height: "100vh",
      background: "var(--bg-1)",
      borderLeft: "1px solid var(--line)",
      display: "flex", flexDirection: "column",
    }}>
      <div className="hstack" style={{ padding: "16px 18px", borderBottom: "1px solid var(--line)" }}>
        <span className="hstack" style={{ gap: 8 }}>
          <span style={{ width: 28, height: 28, borderRadius: 8, background: "var(--brand-soft)", display: "grid", placeItems: "center", color: "var(--brand)" }}>
            <Icon name="sparkles" size={14} />
          </span>
          <span>
            <div className="h-3">AI 助手</div>
            <div className="dim" style={{ fontSize: 11.5, marginTop: 1 }}>Claude · 实时上下文感知</div>
          </span>
        </span>
        <span className="spacer" />
        <button className="icon-btn" onClick={onClose}><Icon name="x" size={14} /></button>
      </div>

      <div style={{ flex: 1, overflowY: "auto", padding: "16px 18px" }}>
        <div className="vstack" style={{ gap: 12 }}>
          <div style={{
            padding: 12, borderRadius: 10, background: "var(--surface-2)",
            border: "1px solid var(--line)", fontSize: 13, lineHeight: 1.65,
          }}>
            看到你在做<span style={{ color: "var(--brand)" }}>《信用卡欺诈检测》</span>，第 5 项测试 <code className="mono" style={{ background: "var(--code-bg)", padding: "1px 6px", borderRadius: 4, fontSize: 12 }}>test_precision_threshold</code> 失败了。Precision = 0.642，差 0.058 才到 0.70。
          </div>
          <div style={{
            padding: 12, borderRadius: 10, background: "var(--surface-2)",
            border: "1px solid var(--line)", fontSize: 13, lineHeight: 1.65,
          }}>
            <div style={{ fontWeight: 500, marginBottom: 6 }}>三个改进方向（从简单到复杂）：</div>
            <ol style={{ paddingLeft: 18, color: "var(--fg-2)" }}>
              <li style={{ marginBottom: 4 }}>提高决策阈值：<code className="mono" style={{ fontSize: 12 }}>predict_proba</code> 后用 0.6 而非 0.5</li>
              <li style={{ marginBottom: 4 }}>用 <code className="mono" style={{ fontSize: 12 }}>StandardScaler</code> 先标准化特征</li>
              <li>换 <code className="mono" style={{ fontSize: 12 }}>class_weight='balanced'</code> + 网格搜 C</li>
            </ol>
            <div className="hstack" style={{ marginTop: 10, gap: 6 }}>
              <button className="btn btn-secondary btn-sm">展示代码</button>
              <button className="btn btn-ghost btn-sm">解释为什么</button>
            </div>
          </div>
        </div>
      </div>

      <div style={{ padding: 14, borderTop: "1px solid var(--line)" }}>
        <div className="hstack" style={{ gap: 6, padding: "6px 10px 6px 12px",
          background: "var(--surface)", border: "1px solid var(--line)",
          borderRadius: 10 }}>
          <input
            placeholder="问点什么…"
            style={{ flex: 1, background: "transparent", border: 0, outline: 0,
              color: "var(--fg)", fontSize: 13, height: 28 }}
          />
          <button className="icon-btn" style={{ color: "var(--brand)" }}>
            <Icon name="send" size={14} />
          </button>
        </div>
        <div className="dim" style={{ fontSize: 11, marginTop: 6, textAlign: "center" }}>
          AI 看得到你的代码和测试结果 · 不会替你完成实验
        </div>
      </div>
    </aside>
  </div>
);

export default ScreenLab;
