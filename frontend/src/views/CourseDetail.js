/**
 * Course Detail View - Redirects to traditional course.html page
 * SPA module shell for compatibility with SPA router.
 */

export default async function CourseDetail({ params }) {
  const courseId = params?.id;
  if (courseId) {
    window.location.href = `/course.html?id=${courseId}`;
    return '<div class="loading">正在跳转到课程详情...</div>';
  }
  return '<div class="error-page"><h1>课程ID缺失</h1><a href="/spa.html">返回首页</a></div>';
}
