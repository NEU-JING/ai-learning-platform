# E2E 测试补充要求

**变更**: 002-ailp-v4-refactor  
**检查时间**: 2026-05-31  
**状态**: ❌ E2E 用例数量不足

---

## 当前状态

| 项目 | 数值 |
|------|------|
| E2E 配置 | ✅ playwright.config.js |
| 现有 E2E 用例 | 2 个 |
| AC 总数 | 14 个 (Phase 1) |
| 最低要求 | 7 个 (AC × 0.5) |
| **缺口** | **5 个** |

---

## 现有 E2E 用例

```
tests/e2e/
├── auth.spec.js          # 登录/注册
└── navigation.spec.js    # 导航流程
```

---

## 要求补充的 E2E 用例

基于 Phase 1 的 AC，需要补充以下场景：

| AC 编号 | 场景描述 | 优先级 | 建议文件名 |
|:---:|:---------|:---:|:---|
| AC1 | 入学诊断 - 根据背景推荐路径 | P0 | `diagnosis.spec.js` |
| AC2 | 入学诊断 - Fast Track 检测 | P0 | `diagnosis.spec.js` |
| AC3 | 路径进度追踪 - 查看学习进度 | P0 | `path-progress.spec.js` |
| AC4 | 能力缺口诊断 - 识别薄弱技能 | P0 | `skill-gap.spec.js` |
| AC5 | Fast Track 模式 - 快速路径 | P1 | `fast-track.spec.js` |
| AC6 | 路径可视化 - 渲染路径图 | P1 | `visualization.spec.js` |
| AC7 | Radar 技能模型 - 显示10维技能 | P0 | `radar-display.spec.js` |
| AC8 | Radar 认证 - 登录后查看 | P0 | `radar-auth.spec.js` |
| AC9 | 技能更新 - 实验完成后更新 | P1 | `radar-update.spec.js` |
| AC10 | 时间衰减 - 技能分数计算 | P2 | `radar-decay.spec.js` |

---

## 优先级 P0 用例示例

### `diagnosis.spec.js`
```javascript
import { test, expect } from '@playwright/test';

test.describe('入学诊断', () => {
  test('AC1: 根据背景推荐合适的学习路径', async ({ page }) => {
    // 1. 登录
    await page.goto('/login');
    await page.fill('[name="email"]', 'test@example.com');
    await page.fill('[name="password"]', 'password');
    await page.click('button[type="submit"]');
    
    // 2. 进入诊断页面
    await page.goto('/diagnosis');
    
    // 3. 填写背景信息
    await page.selectOption('[name="background"]', 'computer_science');
    await page.selectOption('[name="target_role"]', 'ai-engineer');
    await page.fill('[name="available_time"]', '15');
    
    // 4. 提交诊断
    await page.click('button[type="submit"]');
    
    // 5. 验证推荐结果
    await expect(page.locator('.recommended-path')).toBeVisible();
    await expect(page.locator('.path-name')).toContainText('AI 工程师');
  });
  
  test('AC2: Fast Track 检测与起点调整', async ({ page }) => {
    // 类似流程，验证 Fast Track 逻辑
  });
});
```

### `radar-display.spec.js`
```javascript
import { test, expect } from '@playwright/test';

test.describe('Radar 技能雷达', () => {
  test('AC7: 显示10维技能模型', async ({ page }) => {
    await page.goto('/radar');
    
    // 验证 10 个维度显示
    const dimensions = await page.locator('.radar-dimension').count();
    expect(dimensions).toBe(10);
    
    // 验证雷达图渲染
    await expect(page.locator('.radar-chart')).toBeVisible();
  });
  
  test('AC8: 未登录时重定向到登录页', async ({ page }) => {
    await page.goto('/radar');
    await expect(page).toHaveURL('/login');
  });
});
```

---

## 补充后检查

添加 E2E 用例后，验证数量：
```bash
find tests/e2e -name "*.spec.js" | wc -l
# 应 >= 7
```

---

## 与 PR 创建的关联

1. 先补充 E2E 用例到当前分支
2. 提交并推送：`git add tests/e2e/ && git commit -m "test(e2e): 补充 Phase 1 E2E 用例" && git push`
3. 然后创建 PR
4. CI 会自动运行 E2E 测试
