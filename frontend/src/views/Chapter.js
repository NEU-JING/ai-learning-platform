/**
 * Chapter View - Redirects to traditional chapter.html page
 */

export default async function Chapter({ params }) {
  const chapterId = params?.id;
  if (chapterId) {
    window.location.href = `/chapter.html?id=${chapterId}`;
    return '<div class="loading">正在跳转到章节学习...</div>';
  }
  return '<div class="error-page"><h1>章节ID缺失</h1><a href="/spa.html">返回首页</a></div>';
}
