# AC Coverage Matrix: 公开能力主页

> 生成时间：2026-05-24
> 来源：`spec.md` AC1-AC12 + `test_profile_integration.py`

## 覆盖总览

| AC | 场景 | 集成测试用例 | 其他测试补充 | 状态 |
|:--:|------|-------------|-------------|:----:|
| AC1 | 访问者查看已开启的公开主页（全部维度可见） | `TestAC1FullVisibility::test_visitor_sees_all_data_without_login` | `TestFullVisibility::test_returns_complete_data` | ✅ |
| AC2 | 访问者查看已开启的主页（部分维度隐藏） | `TestAC2PartialVisibility::test_labs_and_certs_hidden_but_basic_info_and_radar_shown` | `TestPartialVisibility::test_basic_info_hidden`, `test_skill_radar_hidden`, `test_labs_hidden`, `test_certificates_hidden` | ✅ |
| AC3 | 用户首次开启公开主页 | `TestAC3FirstTimeEnable::test_first_enable_auto_sets_all_dimensions`, `test_display_name_defaults_to_username` | `TestFirstTimeEnable::test_first_enable_creates_profile_with_all_dimensions`, `test_first_enable_sets_display_name_to_username` | ✅ |
| AC4 | 用户逐步调整可见性设置 | `TestAC4AdjustAndPreview::test_hide_basic_info_then_visit_matches_preview`, `test_profile_url_available_for_copy` | `TestDimensionToggle::test_toggle_dimension_does_not_change_is_public` | ✅ |
| AC5 | 一键隐藏全部维度后访问主页 | `TestAC5AllDimensionsHidden::test_all_hidden_still_returns_200_with_username`, `test_no_not_enabled_message_when_all_hidden` | `TestPartialVisibility::test_all_dimensions_hidden_but_is_public` | ✅ |
| AC6 | 访问不存在的用户名 | `TestAC6NonexistentUser::test_nonexistent_returns_404` | `TestUserNotFound::test_nonexistent_username_returns_404` | ✅ |
| AC7 | 访问未开启公开主页的用户 | `TestAC7ProfileNotEnabled::test_never_enabled_returns_403`, `test_disabled_profile_returns_403` | `TestNoProfileRecord::test_no_profile_returns_403`, `TestProfileNotPublic::test_is_public_false_returns_403` | ✅ |
| AC8 | 用户没有任何实验和认证时开启主页 | `TestAC8ZeroData::test_zero_labs_shows_empty_list`, `test_zero_data_radar_shows_initial_scores` | `TestZeroLabsZeroCertificates::test_empty_labs_and_certs` | ✅ |
| AC9 | 用户拥有大量实验数据时主页列表展示 | `TestAC9LargeDataset::test_labs_total_matches_passed_submissions`, `test_labs_ordered_by_completed_at_desc` | `TestLabListOrdering::test_labs_ordered_by_completed_at_desc`, `test_best_score_per_lab` | ✅ |
| AC10 | 分享链接在社交媒体展示富媒体卡片 | `TestAC10OGTags::test_public_profile_response_contains_username_for_og` | `TestOGTagInjection::test_public_user_has_og_tags`, `test_public_user_has_og_image`, `test_all_dimensions_hidden_og_tags` | ✅ |
| AC11 | 用户关闭公开主页后已分享的链接失效 | `TestAC11CloseProfileLinkInvalidated::test_close_then_visit_returns_403`, `test_url_persists_after_close_and_reopen`, `test_reopen_resets_all_dimensions_to_visible` | `TestCloseProfile::test_close_preserves_dimensions`, `TestReEnableProfile::test_re_enable_resets_all_dimensions_to_true` | ✅ |
| AC12 | 并发访问同一公开主页 | `TestAC12ConcurrentAccess::test_concurrent_reads_return_same_data` | — | ✅ |

## 业务规则覆盖

| 规则 | 描述 | 测试覆盖 | 状态 |
|:----:|------|---------|:----:|
| BR1 | 隐私默认隐藏 | `TestAC7ProfileNotEnabled`, `TestSecurityDataLeakage::test_no_profile_cannot_access_skill_radar_via_profile_api` | ✅ |
| BR2 | 数据来源不可编辑 | `TestAC1FullVisibility` — 数据来自 LabSubmission/LearningProgress | ✅ |
| BR3 | 技能分数动态计算 | `TestAC8ZeroData::test_zero_data_radar_shows_initial_scores` | ✅ |
| BR4 | 维度独立控制 | `TestAC2PartialVisibility`, `TestAC4AdjustAndPreview`, `TestAC5AllDimensionsHidden` | ✅ |
| BR5 | 主页状态与维度状态分离 | `TestAC3FirstTimeEnable`, `TestAC11CloseProfileLinkInvalidated::test_reopen_resets_all_dimensions_to_visible` | ✅ |
| BR6 | 所见即所得 | `TestAC4AdjustAndPreview::test_hide_basic_info_then_visit_matches_preview` | ✅ |
| BR7 | 链接持久性 | `TestAC11CloseProfileLinkInvalidated::test_url_persists_after_close_and_reopen` | ✅ |
| BR8 | 访问无需登录 | `TestAC1FullVisibility::test_visitor_sees_all_data_without_login` | ✅ |
| BR9 | 已删除用户的主页不可访问 | `TestSecurityDataLeakage::test_inactive_user_returns_404_not_403` | ✅ |

## 集成测试：完整链路覆盖

| 链路步骤 | 测试用例 | 状态 |
|---------|---------|:----:|
| 开启主页 | `TestFullLifecycle` Step 1 | ✅ |
| 访问主页 | `TestFullLifecycle` Step 2 | ✅ |
| 调整可见性 | `TestFullLifecycle` Step 3 | ✅ |
| 预览主页 | `TestFullLifecycle` Step 4 | ✅ |
| 分享链接 | `TestFullLifecycle` Step 5 | ✅ |
| 关闭主页 | `TestFullLifecycle` Step 6 | ✅ |
| 访问失效 | `TestFullLifecycle` Step 7 | ✅ |

## 安全测试覆盖

| 安全场景 | 测试用例 | 状态 |
|---------|---------|:----:|
| 未开启主页的用户数据不可通过 API 探测获取 | `TestSecurityDataLeakage::test_no_profile_cannot_access_skill_radar_via_profile_api` | ✅ |
| is_public=false 的用户数据不可泄露 | `TestSecurityDataLeakage::test_disabled_profile_cannot_leak_data` | ✅ |
| 已删除用户返回 404 而非 403（防止用户存在性泄漏） | `TestSecurityDataLeakage::test_inactive_user_returns_404_not_403` | ✅ |
| 隐藏维度的数据不出现在 API 响应中 | `TestSecurityDataLeakage::test_hidden_dimension_data_not_in_response` | ✅ |
| 匿名用户无法访问设置端点 | `TestSecurityDataLeakage::test_anonymous_cannot_access_settings_endpoint` | ✅ |
| 用户无法修改他人设置 | `TestSecurityDataLeakage::test_user_cannot_modify_another_users_settings` | ✅ |

## 测试统计

| 指标 | 数值 |
|------|:----:|
| 集成测试文件 | `test_profile_integration.py` |
| 集成测试用例数 | 27 |
| 全量测试总数 | 177 |
| 全量通过率 | 100% |
| AC 覆盖率 | 12/12 (100%) |
| BR 覆盖率 | 9/9 (100%) |
