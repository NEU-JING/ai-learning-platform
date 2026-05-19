import { useStore } from '../store';

export default function CoursesPage({ navigate }) {
  const { courses, loading } = useStore();

  if (loading) return <div className="loading">加载中...</div>;

  return (
    <div className="courses-page">
      <h1>课程体系</h1>
      <div className="courses-grid">
        {courses.map((course, i) => (
          <div key={course.id} className="course-card" onClick={() => navigate(`#/courses/${course.id}`)}>
            <div className="course-phase">Phase {i + 1}</div>
            <h3>{course.title}</h3>
            <p>{course.description}</p>
            <div className="course-meta">
              <span>{course.chapters_count || course.chapter_count || 0} 章节</span>
              <span>{course.labs_count || 0} 实验</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
