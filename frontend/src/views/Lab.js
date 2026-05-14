/**
 * Lab View - Redirects to traditional lab.html page
 */

export default async function Lab({ params }) {
  const labId = params?.id;
  if (labId) {
    window.location.href = `/lab.html?id=${labId}`;
    return '<div class="loading">正在跳转到实验室...</div>';
  }
  return '<div class="error-page"><h1>实验ID缺失</h1><a href="/spa.html">返回首页</a></div>';
}
