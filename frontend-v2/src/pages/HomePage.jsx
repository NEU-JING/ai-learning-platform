import { useStore } from '../store';

export default function HomePage({ navigate }) {
  const { courses } = useStore();
  const phases = courses.slice(0, 6);

  return (
    <div className="home-page">
      <section className="hero">
        <h1>AI 全栈工程师养成计划</h1>
        <p>从 Python 基础到大模型工程，6 阶段系统化学习</p>
        <button onClick={() => navigate('#/courses')} className="btn-primary">开始学习</button>
      </section>
      <section className="phases-grid">
        {phases.map((phase, i) => (
          <div key={phase.id} className="phase-card" onClick={() => navigate(`#/courses/${phase.id}`)}>
            <div className="phase-number">Phase {i + 1}</div>
            <h3>{phase.title}</h3>
            <p>{phase.description?.slice(0, 80)}...</p>
          </div>
        ))}
      </section>
    </div>
  );
}
