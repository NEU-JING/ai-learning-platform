/**
 * CapstoneView — 挑战与任务链（Phase 4 F2/F1）
 * 返回 DOM Node（事件用 addEventListener 绑定）。
 */
import { API } from '../services/api.js';
import { Store } from '../core/store.js';
import { renderGamificationPanel, renderDailyChallenge } from '../components/GamificationPanel.js';

const store = Store.getInstance();

function esc(s) {
  if (s == null) return '';
  return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function navbar() {
  const isAuth = !!store.state.token;
  return `
    <nav class="navbar">
      <a href="#/" class="navbar-brand"><div class="navbar-logo">AI</div><span>AI学习平台</span></a>
      <ul class="navbar-nav">
        <li><a href="#/">首页</a></li>
        <li><a href="#/courses">课程</a></li>
        <li><a href="#/progress">学习进度</a></li>
        <li><a href="#/capstone" class="active">挑战</a></li>
      </ul>
      <div class="navbar-right">
        ${isAuth && store.state.user
          ? `<span class="user-name">${esc(store.state.user.email)}</span>`
          : `<a href="#/login" class="btn btn-secondary btn-sm">登录</a>`}
      </div>
    </nav>`;
}

function chainCard(c, idx) {
  return `
    <div class="card chain-card" data-chain-index="${idx}">
      <h3>${esc(c.title)}</h3>
      <p class="muted">${esc(c.description || '')}</p>
      <span class="chain-tags">${(c.skill_tags || []).map((t) => `<span class="tag">${esc(t)}</span>`).join(' ') || ''}</span>
      <button class="btn btn-primary btn-sm chain-start" data-chain-id="${c.id}" data-index="${idx}">开始 / 继续</button>
      <div class="chain-task-area" data-chain-id="${c.id}"></div>
      <div class="chain-result" data-chain-id="${c.id}"></div>
    </div>`;
}

export default async function CapstoneView() {
  if (!store.state.token) {
    const el = document.createElement('div');
    el.className = 'page page-enter';
    el.innerHTML = `<div class="error-page"><h1>请先登录</h1><a href="#/login" class="btn btn-primary">去登录</a></div>`;
    return el;
  }

  const container = document.createElement('div');
  container.className = 'page capstone-page page-enter';

  let gamification = { total_xp: 0, level: 1, badges: [], daily_streak: 0 };
  let daily = null;
  let chains = [];
  try { gamification = await API.gamification.me(); } catch (e) { /* ignore */ }
  try { daily = await API.gamification.todayChallenge(); } catch (e) { daily = null; }
  try { chains = await API.capstone.chains(); } catch (e) { chains = []; }

  container.innerHTML = `
    ${navbar()}
    <div class="container" style="padding:24px 0 60px;">
      <h1>⚔️ 挑战与任务链</h1>
      <p class="muted" style="margin-bottom:24px;">代码跑通即验证，证据自动沉淀。</p>

      <div class="gamification-slot">${renderGamificationPanel(gamification)}</div>
      <div class="daily-slot">${renderDailyChallenge(daily)}</div>

      <h2 style="margin-top:28px;">🔗 任务链</h2>
      ${chains.length ? `<div class="chains-grid">${chains.map(chainCard).join('')}</div>` : '<p class="muted">暂无可用的任务链</p>'}
    </div>`;

  // ── 事件委托 ─────────────────────────────────────────────
  container.addEventListener('click', async (ev) => {
    const startBtn = ev.target.closest('.chain-start');
    if (startBtn) {
      await loadTask(container, startBtn.dataset.chainId);
    }
    const submitBtn = ev.target.closest('.chain-submit');
    if (submitBtn) {
      await submitTask(container, submitBtn.dataset.chainId, submitBtn.dataset.taskId, submitBtn.dataset.index);
    }
    const dcBtn = ev.target.closest('.dc-submit');
    if (dcBtn) {
      await submitDaily(container);
    }
  });

  return container;
}

async function loadTask(container, chainId) {
  const area = container.querySelector(`[data-chain-id="${chainId}"].chain-task-area`);
  if (!area) return;
  try {
    const res = await API.capstone.nextTask(chainId);
    if (!res.has_next) {
      area.innerHTML = '<p class="chain-done">🎉 任务链已完成！查看证据卡 ↓</p>';
      await loadEvidence(container, chainId);
      return;
    }
    const t = res.task;
    area.innerHTML = `
      <div class="task-box">
        <div class="task-title">任务 ${t.seq}: ${esc(t.title)}</div>
        <p class="muted">${esc(t.scenario || '')}</p>
        <textarea class="task-code" rows="5" data-chain="${chainId}" placeholder="在这里写代码..."></textarea>
        <button class="btn btn-primary btn-sm chain-submit" data-chain-id="${chainId}" data-task-id="${t.id}">提交评测</button>
      </div>`;
  } catch (e) {
    area.innerHTML = `<p class="muted">加载任务失败: ${esc(e.message)}</p>`;
  }
}

async function submitTask(container, chainId, taskId, idx) {
  const code = container.querySelector(`[data-chain="${chainId}"].task-code`);
  const result = container.querySelector(`[data-chain-id="${chainId}"].chain-result`);
  if (!code) return;
  result.innerHTML = '<div class="chain-result-pending">⏳ 评测中...</div>';
  try {
    const res = await API.capstone.submitTask(chainId, taskId, code.value);
    if (res.status === 'passed') {
      result.innerHTML = `
        <div class="chain-ok">✅ 通过！${res.xp_awarded ? `+${res.xp_awarded} XP` : ''}${res.chain_completed ? ' · 🏆 任务链完成!' : ''}</div>`;
      await loadTask(container, chainId);  // 解锁下一个 or 完成
    } else {
      result.innerHTML = `<div class="chain-fail">❌ 未通过${res.feedback ? `: ${esc(res.feedback)}` : ''}</div>`;
    }
  } catch (e) {
    result.innerHTML = `<div class="chain-fail">提交失败: ${esc(e.message)}</div>`;
  }
}

async function loadEvidence(container, chainId) {
  const area = container.querySelector(`[data-chain-id="${chainId}"].chain-task-area`);
  try {
    const card = await API.capstone.evidence(chainId);
    if (!card) return;
    const rows = card.tasks.map((t) => `
      <tr>
        <td>${t.seq}</td>
        <td>${esc(t.title)}</td>
        <td>${t.passed ? '✅' : '❌'}</td>
        <td>${t.score != null ? t.score : '-'}</td>
      </tr>`).join('');
    area.innerHTML += `
      <div class="evidence-card">
        <h4>📄 证据卡 · ${esc(card.title)}</h4>
        <table class="evidence-table"><thead><tr><th>#</th><th>任务</th><th>状态</th><th>得分</th></tr></thead><tbody>${rows}</tbody></table>
      </div>`;
  } catch (e) { /* ignore */ }
}

async function submitDaily(container) {
  const dc = container.querySelector('.dc-code');
  const result = container.querySelector('.dc-result');
  if (!dc) return;
  result.textContent = '⏳ 提交中...';
  try {
    const res = await API.gamification.submitChallenge(dc.value);
    if (res.passed) {
      result.innerHTML = `<span class="chain-ok">✅ 挑战通过！+${res.xp_awarded} XP · 连击+1</span>`;
    } else {
      result.innerHTML = `<span class="chain-fail">❌ 未通过${res.feedback ? `: ${esc(res.feedback)}` : ''}</span>`;
    }
  } catch (e) {
    result.textContent = '提交失败: ' + e.message;
  }
}