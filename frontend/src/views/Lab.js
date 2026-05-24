/**
 * Lab View - SPA 版本（替代传统 lab.html 重定向）
 * v2.0: 内联 Monaco 编辑器 + 代码提交 + 暗色主题
 */
import { API } from '../services/api.js';
import { Store } from '../core/store.js';

const store = Store.getInstance();

export default async function Lab({ params }) {
  const chapterId = params?.id;
  if (!chapterId) {
    return '<div class="error-page"><h1>实验ID缺失</h1><a href="#/courses" class="btn btn-primary">返回课程列表</a></div>';
  }

  const container = document.createElement('div');
  container.className = 'page lab-page page-enter';

  const isAuth = !!store.state.token;
  const navbar = `
    <nav class="navbar">
      <a href="#/" class="navbar-brand">
        <div class="navbar-logo">AI</div>
        <span>AI学习平台</span>
      </a>
      <ul class="navbar-nav">
        <li><a href="#/">首页</a></li>
        <li><a href="#/courses">课程</a></li>
        <li><a href="#/progress">学习进度</a></li>
          <li><a href="#/profile/settings">我的公开主页</a></li>
      </ul>
      <div class="navbar-right">
        ${isAuth && store.state.user
          ? `<span class="user-name">${store.state.user.email}</span>
             <a href="#" class="btn btn-secondary btn-sm" onclick="window.$store.dispatch('logout'); window.location.hash='#/'; return false;">退出</a>`
          : `<a href="#/login" class="btn btn-secondary btn-sm">登录</a>
             <a href="#/register" class="btn btn-primary btn-sm">注册</a>`
        }
      </div>
    </nav>`;

  container.innerHTML = `
    ${navbar}
    <div class="container">
      <div class="loading" style="padding:60px 0;"><span style="font-size:2rem;">⏳</span><br>加载实验环境...</div>
    </div>`;

  try {
    const labRes = await API.courses.getChapterLab(chapterId);
    if (!labRes) throw new Error('实验不存在');

    const lab = labRes;
    const chapterTitle = lab.title || '实验';

    // Parse hints
    let hints = [];
    try { hints = JSON.parse(lab.hints || '[]'); } catch (e) {
      hints = Array.isArray(lab.hints) ? lab.hints : [];
    }

    container.innerHTML = `
      ${navbar}
      <div class="container">
        <div style="padding:16px 0;">
          <a href="#/chapters/${chapterId}" class="btn btn-ghost btn-sm" style="color:var(--text-secondary);">
            ← 返回章节
          </a>
        </div>

        <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-bottom:40px;">
          <!-- Lab description -->
          <div class="code-editor-container">
            <div class="code-editor-header">
              <span>📋 ${lab.title || '实验'}</span>
            </div>
            <div style="padding:20px;overflow-y:auto;max-height:200px;">
              <p style="color:var(--text-secondary);font-size:0.9rem;line-height:1.7;">
                ${lab.description || '完成以下实验内容'}
              </p>
              ${hints.length > 0 ? `
                <div style="margin-top:12px;padding:12px;background:rgba(251,191,36,0.1);border-radius:var(--radius-sm);">
                  <strong style="color:var(--warning);font-size:0.85rem;">💡 提示</strong>
                  <ul style="margin-top:6px;padding-left:16px;">
                    ${hints.map(h => `<li style="color:var(--text-secondary);font-size:0.85rem;margin-bottom:4px;">${h}</li>`).join('')}
                  </ul>
                </div>` : ''}
            </div>
          </div>

          <!-- Output area -->
          <div class="code-editor-container">
            <div class="code-editor-header">
              <span>📤 运行结果</span>
            </div>
            <div class="code-output" id="lab-output" style="max-height:200px;overflow-y:auto;font-size:0.82rem;">
              点击「运行」查看输出结果
            </div>
          </div>
        </div>

        <!-- Code editor -->
        <div class="code-editor-container" style="margin-bottom:20px;">
          <div class="code-editor-header">
            <span>💻 代码编辑器</span>
            <div class="code-editor-toolbar">
              <button class="btn btn-secondary btn-sm" onclick="resetEditor()">重置</button>
              <button class="btn btn-primary btn-sm" onclick="runLab()">▶ 运行</button>
              <button class="btn btn-primary btn-sm" onclick="submitLab()" style="background:var(--gradient-success);">📤 提交</button>
            </div>
          </div>
          <div id="monaco-container" style="height:400px;"></div>
        </div>

        <div id="lab-result" style="display:none;"></div>
      </div>`;

    // Initialize Monaco editor
    setTimeout(() => initMonaco(lab.starter_code || '', chapterId), 200);

  } catch (err) {
    container.innerHTML = `
      ${navbar}
      <div class="container">
        <div class="error-page" style="min-height:50vh;">
          <h1>😅</h1>
          <p style="color:var(--text-secondary);margin-top:16px;">${err.message || '加载实验失败'}</p>
          <a href="#/courses" class="btn btn-primary" style="margin-top:16px;">返回课程列表</a>
        </div>
      </div>`;
  }

  return container;
}

// Monaco editor instance (global for button handlers)
let monacoEditor = null;

function initMonaco(starterCode, chapterId) {
  if (typeof monaco === 'undefined' || !monaco.editor) {
    // Monaco not loaded yet, retry
    setTimeout(() => initMonaco(starterCode, chapterId), 500);
    return;
  }

  const container = document.getElementById('monaco-container');
  if (!container) return;

  monacoEditor = monaco.editor.create(container, {
    value: starterCode,
    language: 'python',
    theme: 'vs-dark',
    fontSize: 14,
    fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
    minimap: { enabled: false },
    lineNumbers: 'on',
    scrollBeyondLastLine: false,
    automaticLayout: true,
    padding: { top: 12 },
    renderWhitespace: 'selection',
    tabSize: 4,
  });

  // Make functions global for button onclick
  window.resetEditor = () => {
    if (monacoEditor) monacoEditor.setValue(starterCode);
  };

  window.runLab = async () => {
    const output = document.getElementById('lab-output');
    if (!output || !monacoEditor) return;
    const code = monacoEditor.getValue();
    output.innerHTML = '<span style="color:var(--text-muted);">⏳ 运行中...</span>';

    try {
      const res = await API.labs.submit(chapterId, code);
      output.innerHTML = '';
      if (res.output) {
        output.innerHTML = `<span class="success">${escapeHtml(res.output)}</span>`;
      }
      if (res.error) {
        output.innerHTML += `<span class="error">${escapeHtml(res.error)}</span>`;
      }
      if (!res.output && !res.error) {
        output.innerHTML = '<span class="success">✅ 执行成功（无输出）</span>';
      }
    } catch (err) {
      output.innerHTML = `<span class="error">❌ ${escapeHtml(err.message || '运行失败')}</span>`;
    }
  };

  window.submitLab = async () => {
    if (!monacoEditor) return;
    const code = monacoEditor.getValue();
    const resultDiv = document.getElementById('lab-result');
    if (!resultDiv) return;

    resultDiv.style.display = 'block';
    resultDiv.innerHTML = '<div style="padding:20px;text-align:center;color:var(--text-muted);">⏳ 提交评测中...</div>';

    try {
      const res = await API.labs.submit(chapterId, code);
      const passed = res.passed_tests || 0;
      const total = res.total_tests || 0;
      const allPassed = res.all_passed || false;

      if (allPassed) {
        resultDiv.innerHTML = `
          <div style="padding:16px 20px;background:rgba(16,185,129,0.1);border:1px solid rgba(16,185,129,0.3);border-radius:var(--radius-md);margin-top:16px;">
            <strong style="color:var(--success);font-size:1.1rem;">✅ 全部通过！</strong>
            <span style="color:var(--text-secondary);margin-left:8px;">${passed}/${total} 测试通过</span>
          </div>`;
      } else {
        resultDiv.innerHTML = `
          <div style="padding:16px 20px;background:rgba(239,68,68,0.1);border:1px solid rgba(239,68,68,0.3);border-radius:var(--radius-md);margin-top:16px;">
            <strong style="color:var(--danger);font-size:1.1rem;">❌ ${passed}/${total} 通过</strong>
            ${res.errors ? `<pre style="margin-top:8px;color:var(--danger);font-size:0.85rem;white-space:pre-wrap;">${escapeHtml(res.errors)}</pre>` : ''}
          </div>`;
      }
    } catch (err) {
      resultDiv.innerHTML = `
        <div style="padding:16px 20px;background:rgba(239,68,68,0.1);border:1px solid rgba(239,68,68,0.3);border-radius:var(--radius-md);margin-top:16px;">
          <strong style="color:var(--danger);">❌ 提交失败</strong>
          <p style="color:var(--text-secondary);margin-top:4px;">${escapeHtml(err.message || '未知错误')}</p>
        </div>`;
    }
  };
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}
