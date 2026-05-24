/**
 * ProfileRadarChart — skill radar visualization
 *
 * Desktop (>=768px): SVG radar chart with polygon fill
 * Mobile (<768px): Horizontal bar chart with labels and scores
 *
 * No external dependencies — pure SVG + CSS.
 * Data shape: { skills: { "python": { score: 85, label: "Python基础" }, ... } }
 */

/**
 * Render the radar/bar chart component.
 * Returns an HTML string.
 *
 * @param {Object|null} skillRadar - The skill_radar object from API, or null if hidden
 * @param {string} containerId - DOM id for the container
 * @returns {string} HTML string
 */
export function ProfileRadarChart(skillRadar, containerId = 'profile-radar') {
  if (!skillRadar || !skillRadar.skills) {
    return '';
  }

  const entries = Object.entries(skillRadar.skills);
  if (entries.length === 0) {
    return '';
  }

  // Build both charts; JS on mount will pick the right one based on viewport
  return `
    <div id="${containerId}" class="profile-radar-container">
      <h3 class="profile-section-title">技能雷达</h3>
      <div class="profile-radar-desktop" id="${containerId}-desktop">
        ${_renderSVGChart(entries, skillRadar.overall_score)}
      </div>
      <div class="profile-radar-mobile" id="${containerId}-mobile">
        ${_renderBarChart(entries)}
      </div>
      ${skillRadar.strongest && skillRadar.strongest.length > 0 ? `
        <div class="profile-radar-summary">
          <span class="profile-radar-label">优势技能：</span>
          ${skillRadar.strongest.map(s => {
            const skill = skillRadar.skills[s];
            return `<span class="profile-radar-tag">${skill ? skill.label : s}</span>`;
          }).join('')}
        </div>
      ` : ''}
      <div class="profile-radar-overall">
        综合评分：<strong>${(skillRadar.overall_score || 0).toFixed(1)}</strong>
      </div>
    </div>
  `;
}

/**
 * Post-mount: attach resize listener to toggle desktop/mobile charts
 */
export function initRadarResize(containerId = 'profile-radar') {
  const container = document.getElementById(containerId);
  if (!container) return;

  const desktop = document.getElementById(`${containerId}-desktop`);
  const mobile = document.getElementById(`${containerId}-mobile`);
  if (!desktop || !mobile) return;

  function updateVisibility() {
    const isMobile = window.innerWidth < 768;
    desktop.style.display = isMobile ? 'none' : 'block';
    mobile.style.display = isMobile ? 'block' : 'none';
  }

  updateVisibility();
  window.addEventListener('resize', updateVisibility);

  // Return cleanup function
  return () => window.removeEventListener('resize', updateVisibility);
}

// ── SVG Radar Chart (desktop) ────────────────────────────────────────────

function _renderSVGChart(entries, overallScore) {
  const n = entries.length;
  if (n < 3) {
    // Too few dimensions for a radar — fall back to bar chart
    return _renderBarChart(entries);
  }

  const size = 280;
  const cx = size / 2;
  const cy = size / 2;
  const radius = 110;
  const angleStep = (2 * Math.PI) / n;

  // Generate polygon points for each skill
  const points = entries.map(([key, val], i) => {
    const angle = angleStep * i - Math.PI / 2; // start from top
    const r = (Math.max(0, Math.min(100, val.score)) / 100) * radius;
    const x = cx + r * Math.cos(angle);
    const y = cy + r * Math.sin(angle);
    return { x, y, key, val, angle };
  });

  const polygonStr = points.map(p => `${p.x},${p.y}`).join(' ');

  // Grid rings (25%, 50%, 75%, 100%)
  const rings = [0.25, 0.5, 0.75, 1.0].map(pct => {
    const ringPoints = [];
    for (let i = 0; i < n; i++) {
      const angle = angleStep * i - Math.PI / 2;
      const r = pct * radius;
      ringPoints.push(`${cx + r * Math.cos(angle)},${cy + r * Math.sin(angle)}`);
    }
    return ringPoints.join(' ');
  });

  // Axis lines + labels
  const axes = points.map(p => {
    const labelR = radius + 24;
    const lx = cx + labelR * Math.cos(p.angle);
    const ly = cy + labelR * Math.sin(p.angle);
    const textAnchor = Math.abs(Math.cos(p.angle)) < 0.1 ? 'middle'
      : Math.cos(p.angle) > 0 ? 'start' : 'end';
    return `
      <line x1="${cx}" y1="${cy}" x2="${cx + radius * Math.cos(p.angle)}"
            y2="${cy + radius * Math.sin(p.angle)}"
            stroke="var(--border-color, #e2e8f0)" stroke-width="1" />
      <text x="${lx}" y="${ly}" text-anchor="${textAnchor}"
            dominant-baseline="middle"
            fill="var(--text-secondary, #64748b)" font-size="11">
        ${p.val.label || p.key} ${p.val.score.toFixed(0)}
      </text>
    `;
  }).join('');

  return `
    <svg viewBox="0 0 ${size} ${size}" class="profile-radar-svg" role="img"
         aria-label="技能雷达图">
      ${rings.map(pts => `
        <polygon points="${pts}" fill="none"
                 stroke="var(--border-color, #e2e8f0)" stroke-width="1" />
      `).join('')}
      ${axes}
      <polygon points="${polygonStr}"
               fill="rgba(99, 102, 241, 0.2)"
               stroke="rgba(99, 102, 241, 0.8)" stroke-width="2" />
      ${points.map(p => `
        <circle cx="${p.x}" cy="${p.y}" r="4"
                fill="rgba(99, 102, 241, 1)" />
      `).join('')}
    </svg>
  `;
}

// ── Horizontal Bar Chart (mobile) ────────────────────────────────────────

function _renderBarChart(entries) {
  const bars = entries.map(([key, val]) => {
    const score = Math.max(0, Math.min(100, val.score));
    const scoreColor = score >= 80 ? '#48bb78' : score >= 60 ? '#ecc94b' : '#fc8181';
    return `
      <div class="profile-bar-row">
        <span class="profile-bar-label">${val.label || key}</span>
        <div class="profile-bar-track">
          <div class="profile-bar-fill" style="width:${score}%; background:${scoreColor}"></div>
        </div>
        <span class="profile-bar-score">${score.toFixed(0)}</span>
      </div>
    `;
  }).join('');

  return `<div class="profile-bar-chart">${bars}</div>`;
}

export default ProfileRadarChart;
