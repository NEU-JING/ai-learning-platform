import { useEffect } from 'react';
import { useStore } from '../store';

export default function CourseDetailPage({ courseId, navigate }) {
  const { currentCourse, loadCourseDetail, loading } = useStore();

  useEffect(() => { loadCourseDetail(courseId); }, [courseId, loadCourseDetail]);

  if (loading) return <div className="loading">加载中...</div>;
  if (!currentCourse) return <div className="error">课程不存在</div>;

  return (
    <div className="course-detail-page">
      <button className="btn-back" onClick={() => navigate('#/courses')}>← 返回课程列表</button>
      <h1>{currentCourse.title}</h1>
      <p>{currentCourse.description}</p>
      <div className="chapters-list">
        <h2>章节列表</h2>
        {(currentCourse.chapters || []).map((ch, i) => (
          <div key={ch.id} className="chapter-item">
            <span className="chapter-number">第{i + 1}章</span>
            <span className="chapter-title">{ch.title}</span>
            {ch.labs && ch.labs.length > 0 && (
              <span className="chapter-lab" onClick={(e) => { e.stopPropagation(); navigate(`#/courses/${courseId}/labs/${ch.labs[0].id}`); }}>
                实验 →
              </span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
