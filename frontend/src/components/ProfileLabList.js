/**
 * ProfileLabList — lab submissions on public profile
 *
 * Features:
 *   - Default show first 5 items
 *   - "展开全部（N 个实验）" button to expand
 *   - Empty state: "暂无实验记录"
 *   - Ordered by completed_at DESC (already from API)
 */

/**
 * @param {Array|null} labs - Array of lab items from API, null if hidden
 * @param {number|null} labsTotal - Total lab count
 * @param {string} containerId
 * @returns {string} HTML string
 */
export function ProfileLabList(labs, labsTotal, containerId = 'profile-labs') {
  // If labs is null, the dimension is hidden — render nothing
  if (labs === null || labs === undefined) {
    return '';
  }

  const total = labsTotal != null ? labsTotal : labs.length;
  const isEmpty = labs.length === 0;

  if (isEmpty) {
    return `
      <div id="${containerId}" class="profile-labs-container">
        <h3 class="profile-section-title">实验记录</h3>
        <div class="profile-empty-state">暂无实验记录</div>
      </div>
    `;
  }

  const PREVIEW_COUNT = 5;
  const isCollapsed = total > PREVIEW_COUNT;

  const labItems = labs.map((lab, idx) => {
    const date = lab.completed_at ? new Date(lab.completed_at).toLocaleDateString('zh-CN') : '';
    const scoreColor = lab.score >= 90 ? '#48bb78' : lab.score >= 70 ? '#ecc94b' : '#fc8181';
    const hiddenClass = idx >= PREVIEW_COUNT ? 'profile-lab-item-hidden' : '';
    return `
      <div class="profile-lab-item ${hiddenClass}" data-lab-index="${idx}">
        <div class="profile-lab-info">
          <span class="profile-lab-title">${_escapeHtml(lab.lab_title)}</span>
          <span class="profile-lab-course">${_escapeHtml(lab.course_title)}</span>
          ${date ? `<span class="profile-lab-date">${date}</span>` : ''}
        </div>
        <div class="profile-lab-score" style="color:${scoreColor}">
          ${lab.score.toFixed(0)}分
        </div>
      </div>
    `;
  }).join('');

  const expandBtn = isCollapsed ? `
    <button class="profile-expand-btn" id="${containerId}-expand"
            data-total="${total}" onclick="
              document.querySelectorAll('#${containerId} .profile-lab-item-hidden')
                .forEach(el => el.style.display = 'flex');
              this.style.display = 'none';
            ">
      展开全部（${total} 个实验）
    </button>
  ` : '';

  return `
    <div id="${containerId}" class="profile-labs-container">
      <h3 class="profile-section-title">实验记录</h3>
      <div class="profile-lab-list">
        ${labItems}
      </div>
      ${expandBtn}
    </div>
  `;
}

function _escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str || '';
  return div.innerHTML;
}

export default ProfileLabList;
