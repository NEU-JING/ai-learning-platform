import { useState, useEffect } from 'react';
import { useStore } from '../store';
import { api } from '../api';

export default function LabPage({ labId, navigate }) {
  const [lab, setLab] = useState(null);
  const [code, setCode] = useState('');
  const [result, setResult] = useState(null);
  const [running, setRunning] = useState(false);
  const { user } = useStore();

  useEffect(() => {
    api.labs.get(labId).then(setLab).catch(console.error);
  }, [labId]);

  const handleSubmit = async () => {
    if (!user) { navigate('#/login'); return; }
    setRunning(true);
    try {
      const res = await api.labs.submit(labId, code);
      setResult(res);
    } catch (e) {
      setResult({ success: false, error: e.message });
    } finally {
      setRunning(false);
    }
  };

  if (!lab) return <div className="loading">加载中...</div>;

  return (
    <div className="lab-page">
      <button className="btn-back" onClick={() => navigate('#/courses')}>← 返回课程</button>
      <h1>{lab.title}</h1>
      <p>{lab.description}</p>
      <div className="lab-editor">
        <textarea value={code} onChange={(e) => setCode(e.target.value)} placeholder="在此编写代码..." rows={15} />
        <button onClick={handleSubmit} disabled={running} className="btn-primary">
          {running ? '运行中...' : '提交运行'}
        </button>
      </div>
      {result && (
        <div className={`lab-result ${result.success ? 'success' : 'error'}`}>
          <h3>{result.success ? '✅ 通过' : '❌ 未通过'}</h3>
          {result.output && <pre>{result.output}</pre>}
          {result.error && <pre className="error-output">{result.error}</pre>}
        </div>
      )}
    </div>
  );
}
