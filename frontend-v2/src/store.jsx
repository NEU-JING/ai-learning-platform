import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { api } from './api';

const StoreContext = createContext(null);
export const useStore = () => useContext(StoreContext);

export function StoreProvider({ children }) {
  const [user, setUser] = useState(null);
  const [courses, setCourses] = useState([]);
  const [currentCourse, setCurrentCourse] = useState(null);
  const [currentChapter, setCurrentChapter] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Auto-load user on mount
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      api.auth.me().then(setUser).catch(() => {
        localStorage.removeItem('access_token');
      });
    }
  }, []);

  const login = useCallback(async (email, password) => {
    const data = await api.auth.login(email, password);
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('refresh_token', data.refresh_token);
    const me = await api.auth.me();
    setUser(me);
    return me;
  }, []);

  const register = useCallback(async (email, username, password) => {
    const data = await api.auth.register(email, username, password);
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('refresh_token', data.refresh_token);
    setUser(data);
    return data;
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setUser(null);
  }, []);

  const loadCourses = useCallback(async () => {
    setLoading(true);
    try {
      const data = await api.courses.list();
      setCourses(data.items || data);
      setError(null);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, []);

  const loadCourseDetail = useCallback(async (id) => {
    setLoading(true);
    try {
      const course = await api.courses.get(id);
      const chapters = await api.courses.chapters(id);
      setCurrentCourse({ ...course, chapters: chapters.items || chapters });
      setError(null);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, []);

  const value = {
    user, courses, currentCourse, currentChapter, loading, error,
    login, register, logout, loadCourses, loadCourseDetail, setCurrentChapter, setError,
  };

  return <StoreContext.Provider value={value}>{children}</StoreContext.Provider>;
}
