/**
 * 游戏化组件 — 等级/XP/徽章/连击 展示（Phase 4 F1）
 * 纯展示组件：接收 gamification summary 数据，返回 HTML 片段。
 */

const BADGE_META = {
  first_lab: { icon: '🏅', label: '首个实验' },
  chain_complete: { icon: '🏆', label: '任务链达人' },
  streak_7: { icon: '🔥', label: '连击7天' },
};

export function renderGamificationPanel(g) {
  if (!g) return '';
  const levelXp = g.level * 100;           // 当前级门槛
  const levelBase = (g.level - 1) * 100;   // 上一级基点
  const inLevel = Math.min(100, Math.round(((g.total_xp - levelBase) / 100) * 100));
  const badges = (g.badges && g.badges.length)
    ? g.badges.map((b) => {
        const meta = BADGE_META[b] || { icon: '🏅', label: b };
        return `<span class="gp-badge" title="${meta.label}">${meta.icon}</span>`;
      }).join('')
    : '<span class="gp-empty">暂无徽章</span>';
  return `
    <div class="gamification-panel">
      <div class="gp-main">
        <div class="gp-level">Lv.${g.level}</div>
        <div class="gp-xpbar">
          <div class="gp-xpbar-fill" style="width:${Math.max(0, inLevel)}%"></div>
        </div>
        <div class="gp-xp">${g.total_xp} XP</div>
        <span class="gp-streak">🔥 连续学习 ${g.daily_streak || 0} 天</span>
      </div>
      <div class="gp-badges">${badges}</div>
    </div>`;
}

export function renderDailyChallenge(c, xp = 20) {
  if (!c) return '';
  return `
    <div class="daily-challenge">
      <h3 class="dc-title">🎯 今日挑战 <span class="dc-xp">+${xp * 2} XP</span></h3>
      <p class="dc-task">${c.task}</p>
      <textarea class="dc-code" rows="4" placeholder="在这里写代码..."></textarea>
      <button class="btn btn-primary btn-sm dc-submit">提交</button>
      <div class="dc-result muted"></div>
    </div>`;
}