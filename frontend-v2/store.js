/**
 * Store - React Context 状态管理
 * 管理全局状态：用户、课程、学习进度
 */

const { createContext, useContext, useState, useEffect, useCallback } = React;

// 创建 Context
const StoreContext = createContext(null);

// Store Provider
const StoreProvider = ({ children }) => {
  // 用户状态
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('user');
    return saved ? JSON.parse(saved) : null;
  });
  
  // 课程列表
  const [courses, setCourses] = useState([]);
  const [coursesLoading, setCoursesLoading] = useState(false);
  const [coursesError, setCoursesError] = useState(null);
  
  // 当前学习状态
  const [currentCourse, setCurrentCourse] = useState(null);
  const [currentChapter, setCurrentChapter] = useState(null);
  
  // 学习进度
  const [progress, setProgress] = useState({
    streak_days: 0,
    total_minutes: 0,
    chapters_completed: 0,
    labs_completed: 0,
    weekly: [0, 0, 0, 0, 0, 0, 0],
    recent: [],
  });
  
  // 加载课程列表
  const loadCourses = useCallback(async () => {
    setCoursesLoading(true);
    setCoursesError(null);
    try {
      const response = await window.api.courses.getList({ perPage: 100 });
      // 适配后端数据结构
      const courseList = response.items || response;
      setCourses(courseList.map(c => ({
        id: c.id,
        title: c.title,
        subtitle: c.description?.substring(0, 50) || '',
        description: c.description,
        level: c.level,
        category: c.category,
        duration_hours: c.duration_hours,
        chapters_total: c.chapters_count || 0,
        labs_total: c.labs_count || 0,
        students: c.enrolled_count || 0,
        rating: c.rating || 4.8,
        cover_image: c.cover_image,
        order_index: c.order_index,
      })));
    } catch (err) {
      setCoursesError(err.message);
      console.error('Failed to load courses:', err);
    } finally {
      setCoursesLoading(false);
    }
  }, []);
  
  // 加载课程详情
  const loadCourseDetail = useCallback(async (courseId) => {
    try {
      const [detail, chapters] = await Promise.all([
        window.api.courses.getDetail(courseId),
        window.api.courses.getChapters(courseId),
      ]);
      
      setCurrentCourse({
        ...detail,
        chapters: chapters.map(ch => ({
          id: ch.id,
          title: ch.title,
          order_num: ch.order_num,
          duration: ch.duration_minutes || 30,
          type: ch.has_lab ? 'lab' : 'text',
          status: 'not_started',
        })),
      });
      return { detail, chapters };
    } catch (err) {
      console.error('Failed to load course detail:', err);
      throw err;
    }
  }, []);
  
  // 加载章节详情
  const loadChapter = useCallback(async (chapterId) => {
    try {
      const chapter = await window.api.courses.getChapter(chapterId);
      setCurrentChapter(chapter);
      return chapter;
    } catch (err) {
      console.error('Failed to load chapter:', err);
      throw err;
    }
  }, []);
  
  // 更新学习进度
  const updateProgress = useCallback(async (chapterId, percent) => {
    try {
      await window.api.progress.updateChapter(chapterId, percent);
      // 重新加载进度
      await loadProgress();
    } catch (err) {
      console.error('Failed to update progress:', err);
    }
  }, []);
  
  // 加载学习进度
  const loadProgress = useCallback(async () => {
    if (!user) return;
    try {
      const [stats, recent] = await Promise.all([
        window.api.progress.getStats(),
        window.api.progress.getRecent(),
      ]);
      
      setProgress({
        streak_days: stats.streak_days || 0,
        total_minutes: stats.total_minutes || 0,
        chapters_completed: stats.chapters_completed || 0,
        labs_completed: stats.labs_completed || 0,
        weekly: stats.weekly_activity || [0, 0, 0, 0, 0, 0, 0],
        recent: recent || [],
      });
    } catch (err) {
      console.error('Failed to load progress:', err);
    }
  }, [user]);
  
  // 登录
  const login = useCallback(async (email, password) => {
    const response = await window.api.auth.login(email, password);
    localStorage.setItem('access_token', response.access_token);
    localStorage.setItem('refresh_token', response.refresh_token);
    localStorage.setItem('user', JSON.stringify(response.user));
    setUser(response.user);
    return response;
  }, []);
  
  // 注册
  const register = useCallback(async (email, username, password) => {
    const response = await window.api.auth.register(email, username, password);
    return response;
  }, []);
  
  // 登出
  const logout = useCallback(async () => {
    await window.api.auth.logout();
    setUser(null);
    setCourses([]);
    setCurrentCourse(null);
    setCurrentChapter(null);
  }, []);
  
  // 初始化时加载课程
  useEffect(() => {
    loadCourses();
  }, [loadCourses]);
  
  // 用户登录后加载进度
  useEffect(() => {
    if (user) {
      loadProgress();
    }
  }, [user, loadProgress]);
  
  const value = {
    // 状态
    user,
    courses,
    coursesLoading,
    coursesError,
    currentCourse,
    currentChapter,
    progress,
    
    // 方法
    login,
    register,
    logout,
    loadCourses,
    loadCourseDetail,
    loadChapter,
    updateProgress,
    loadProgress,
    setCurrentCourse,
    setCurrentChapter,
  };
  
  return React.createElement(StoreContext.Provider, { value }, children);
};

// Hook
const useStore = () => {
  const context = useContext(StoreContext);
  if (!context) {
    throw new Error('useStore must be used within StoreProvider');
  }
  return context;
};

// 导出
window.StoreContext = StoreContext;
window.StoreProvider = StoreProvider;
window.useStore = useStore;
