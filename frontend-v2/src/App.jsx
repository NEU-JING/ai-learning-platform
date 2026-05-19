import { useState, useEffect } from 'react';
import { useStore } from './store';

// Pages
import HomePage from './pages/HomePage';
import CoursesPage from './pages/CoursesPage';
import CourseDetailPage from './pages/CourseDetailPage';
import LabPage from './pages/LabPage';
import ProgressPage from './pages/ProgressPage';
import LoginPage from './pages/LoginPage';

export default function App() {
  const [route, setRoute] = useState(window.location.hash || '#/');
  const { user, loadCourses } = useStore();

  useEffect(() => {
    const handler = () => setRoute(window.location.hash || '#/');
    window.addEventListener('hashchange', handler);
    return () => window.removeEventListener('hashchange', handler);
  }, []);

  useEffect(() => { loadCourses(); }, [loadCourses]);

  const navigate = (path) => { window.location.hash = path; };

  const renderPage = () => {
    if (route.startsWith('#/courses/') && route.includes('/labs/')) {
      const labId = route.split('/labs/')[1];
      return <LabPage labId={labId} navigate={navigate} />;
    }
    if (route.startsWith('#/courses/')) {
      const id = route.split('#/courses/')[1];
      return <CourseDetailPage courseId={id} navigate={navigate} />;
    }
    switch (route) {
      case '#/courses': return <CoursesPage navigate={navigate} />;
      case '#/progress': return <ProgressPage navigate={navigate} />;
      case '#/login': return <LoginPage navigate={navigate} />;
      default: return <HomePage navigate={navigate} />;
    }
  };

  return (
    <div className="app">
      <nav className="navbar">
        <a href="#/" className="nav-brand">AI学习平台</a>
        <div className="nav-links">
          <a href="#/courses">课程</a>
          <a href="#/progress">学习进度</a>
          {user ? (
            <span className="user-info">{user.username}</span>
          ) : (
            <a href="#/login">登录</a>
          )}
        </div>
      </nav>
      <main className="main-content">{renderPage()}</main>
    </div>
  );
}
