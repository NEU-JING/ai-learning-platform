import React, { useState, useEffect } from 'react';
import { HashRouter, Routes, Route, useNavigate } from 'react-router-dom';
import { Topbar, MobileNav, CommandPalette } from './nav';
import { useTweaks, TweaksPanel, TweakSection, TweakRadio, TweakColor, TweakButton } from './tweaks-panel';
import { Icon } from './icons';
import HomePage from './pages/HomePage';
import CoursesPage from './pages/CoursesPage';
import CourseDetailPage from './pages/CourseDetailPage';
import ChapterPage from './pages/ChapterPage';
import LabPage from './pages/LabPage';
import ProgressPage from './pages/ProgressPage';

const BRAND_TO_HEX = { indigo: "#818cf8", teal: "#2dd4bf", amber: "#f5b342", rose: "#fb7185", lime: "#a3e635" };
const HEX_TO_BRAND = { "#818cf8": "indigo", "#2dd4bf": "teal", "#f5b342": "amber", "#fb7185": "rose", "#a3e635": "lime" };

const TWEAK_DEFAULTS = {
  "theme": "dark",
  "brand": "indigo",
  "density": "standard",
  "corners": "soft",
  "hero_layout": "centered",
  "show_mobile_nav": false
};

const ScreenStub = ({ title, desc }) => {
  const navigate = useNavigate();
  return (
    <div className="screen container" style={{ paddingTop: 80, paddingBottom: 80, textAlign: "center" }}>
      <div style={{ display: "inline-grid", placeItems: "center", width: 48, height: 48, borderRadius: 12, background: "var(--surface)", border: "1px solid var(--line)", color: "var(--brand)", marginBottom: 16 }}>
        <Icon name="message" size={20} />
      </div>
      <h1 className="h-1">{title}</h1>
      <p className="muted" style={{ marginTop: 8, fontSize: 14, maxWidth: 420, margin: "8px auto 0" }}>{desc}</p>
      <button className="btn btn-secondary" style={{ marginTop: 20 }} onClick={() => navigate('/')}>
        <Icon name="arrowLeft" size={12} /> 返回首页
      </button>
    </div>
  );
};

const AppContent = () => {
  const [searchOpen, setSearchOpen] = useState(false);
  const [tweaksOpen, setTweaksOpen] = useState(false);
  const [t, setTweak] = useTweaks(TWEAK_DEFAULTS);

  // Apply tweak attributes to <html>
  useEffect(() => {
    const el = document.documentElement;
    el.setAttribute("data-theme", t.theme);
    el.setAttribute("data-brand", t.brand);
    el.setAttribute("data-density", t.density);
    el.setAttribute("data-corners", t.corners);
  }, [t.theme, t.brand, t.density, t.corners]);

  // Cmd/Ctrl+K opens search
  useEffect(() => {
    const onKey = (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setSearchOpen(true);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  return (
    <div className="app">
      <Topbar onOpenSearch={() => setSearchOpen(true)} onOpenTweaks={() => setTweaksOpen(true)} />

      <main className="app-main">
        <Routes>
          <Route path="/" element={<HomePage tweaks={t} />} />
          <Route path="/courses" element={<CoursesPage />} />
          <Route path="/courses/:id" element={<CourseDetailPage />} />
          <Route path="/chapter/:id" element={<ChapterPage />} />
          <Route path="/lab/:id" element={<LabPage />} />
          <Route path="/progress" element={<ProgressPage />} />
          <Route path="/discuss" element={<ScreenStub title="讨论区" desc="P1 阶段开放：每章节问答、共学小组、教研团队答疑。" />} />
        </Routes>
      </main>

      <MobileNav />

      <CommandPalette
        open={searchOpen}
        onClose={() => setSearchOpen(false)}
      />

      <TweaksPanel title="设计参数" open={tweaksOpen} onClose={() => setTweaksOpen(false)}>
        <TweakSection label="主题" />
        <TweakRadio
          label="模式"
          options={[
            { value: "dark", label: "暗色" },
            { value: "light", label: "亮色" },
          ]}
          value={t.theme}
          onChange={(v) => setTweak("theme", v)}
        />
        <TweakColor
          label="品牌色"
          options={["#818cf8", "#2dd4bf", "#f5b342", "#fb7185", "#a3e635"]}
          value={BRAND_TO_HEX[t.brand] || "#818cf8"}
          onChange={(hex) => setTweak("brand", HEX_TO_BRAND[hex] || "indigo")}
        />

        <TweakSection label="布局" />
        <TweakRadio
          label="密度"
          options={[
            { value: "compact", label: "紧凑" },
            { value: "standard", label: "标准" },
            { value: "spacious", label: "宽松" },
          ]}
          value={t.density}
          onChange={(v) => setTweak("density", v)}
        />
        <TweakRadio
          label="圆角"
          options={[
            { value: "square", label: "直角" },
            { value: "soft", label: "微圆" },
            { value: "pill", label: "胶囊" },
          ]}
          value={t.corners}
          onChange={(v) => setTweak("corners", v)}
        />
        <TweakRadio
          label="首页 Hero"
          options={[
            { value: "centered", label: "居中" },
            { value: "split", label: "左右" },
          ]}
          value={t.hero_layout}
          onChange={(v) => setTweak("hero_layout", v)}
        />

        <TweakSection label="跳转屏幕" />
        <TweakButton label="01 · 首页" onClick={() => window.location.hash = '#/' } />
        <TweakButton label="02 · 课程列表" onClick={() => window.location.hash = '#/courses' } secondary />
        <TweakButton label="03 · 课程详情" onClick={() => window.location.hash = '#/courses/3' } secondary />
        <TweakButton label="04 · 章节阅读" onClick={() => window.location.hash = '#/chapter/33' } secondary />
        <TweakButton label="05 · 在线实验" onClick={() => window.location.hash = '#/lab/35' } secondary />
        <TweakButton label="06 · 学习进度" onClick={() => window.location.hash = '#/progress' } secondary />
      </TweaksPanel>
    </div>
  );
};

const App = () => (
  <HashRouter>
    <AppContent />
  </HashRouter>
);

export default App;
