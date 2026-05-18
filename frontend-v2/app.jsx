/* App shell — router state, theme application, tweaks panel wiring */

const { useState, useEffect } = React;

const BRAND_TO_HEX = { indigo: "#818cf8", teal: "#2dd4bf", amber: "#f5b342", rose: "#fb7185", lime: "#a3e635" };
const HEX_TO_BRAND = { "#818cf8": "indigo", "#2dd4bf": "teal", "#f5b342": "amber", "#fb7185": "rose", "#a3e635": "lime" };

const TWEAK_DEFAULTS = /*EDITMODE-BEGIN*/{
  "theme": "dark",
  "brand": "indigo",
  "density": "standard",
  "corners": "soft",
  "hero_layout": "centered",
  "show_mobile_nav": false
}/*EDITMODE-END*/;

const App = () => {
  const [route, setRoute] = useState({ name: "home", params: {} });
  const [searchOpen, setSearchOpen] = useState(false);
  const [t, setTweak] = useTweaks(TWEAK_DEFAULTS);

  // Apply tweak attributes to <html>
  useEffect(() => {
    const el = document.documentElement;
    el.setAttribute("data-theme",   t.theme);
    el.setAttribute("data-brand",   t.brand);
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

  const navigate = (name, params = {}) => {
    setRoute({ name, params });
    window.scrollTo({ top: 0, behavior: "instant" });
  };

  // Screen label for comment context
  const screenLabel = {
    home:     "01 首页",
    courses:  "02 课程列表",
    course:   "03 课程详情",
    chapter:  "04 章节阅读",
    lab:      "05 在线实验",
    progress: "06 学习进度",
    discuss:  "07 讨论区",
  }[route.name] || route.name;

  return (
    <div className="app" data-screen-label={screenLabel}>
      <Topbar route={route} onNavigate={navigate} onOpenSearch={() => setSearchOpen(true)} />

      <main className="app-main">
        {route.name === "home"     && <ScreenHome onNavigate={navigate} tweaks={t} />}
        {route.name === "courses"  && <ScreenCourses onNavigate={navigate} />}
        {route.name === "course"   && <ScreenCourseDetail params={route.params} onNavigate={navigate} />}
        {route.name === "chapter"  && <ScreenChapter params={route.params} onNavigate={navigate} />}
        {route.name === "lab"      && <ScreenLab params={route.params} onNavigate={navigate} />}
        {route.name === "progress" && <ScreenProgress onNavigate={navigate} />}
        {route.name === "discuss"  && <ScreenStub title="讨论区" desc="P1 阶段开放：每章节问答、共学小组、教研团队答疑。" onBack={() => navigate("home")} />}
      </main>

      <MobileNav route={route} onNavigate={navigate} />

      <CommandPalette
        open={searchOpen}
        onClose={() => setSearchOpen(false)}
        onNavigate={navigate}
      />

      <TweaksPanel title="设计参数">
        <TweakSection label="主题" />
        <TweakRadio
          label="模式"
          options={[
            { value: "dark",  label: "暗色" },
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
            { value: "compact",   label: "紧凑" },
            { value: "standard",  label: "标准" },
            { value: "spacious",  label: "宽松" },
          ]}
          value={t.density}
          onChange={(v) => setTweak("density", v)}
        />
        <TweakRadio
          label="圆角"
          options={[
            { value: "square", label: "直角" },
            { value: "soft",   label: "微圆" },
            { value: "pill",   label: "胶囊" },
          ]}
          value={t.corners}
          onChange={(v) => setTweak("corners", v)}
        />
        <TweakRadio
          label="首页 Hero"
          options={[
            { value: "centered", label: "居中" },
            { value: "split",    label: "左右" },
          ]}
          value={t.hero_layout}
          onChange={(v) => setTweak("hero_layout", v)}
        />

        <TweakSection label="跳转屏幕" />
        <TweakButton label="01 · 首页"      onClick={() => navigate("home")} />
        <TweakButton label="02 · 课程列表"  onClick={() => navigate("courses")} secondary />
        <TweakButton label="03 · 课程详情"  onClick={() => navigate("course", { id: 3 })} secondary />
        <TweakButton label="04 · 章节阅读"  onClick={() => navigate("chapter", { id: 33 })} secondary />
        <TweakButton label="05 · 在线实验"  onClick={() => navigate("lab", { id: 35 })} secondary />
        <TweakButton label="06 · 学习进度"  onClick={() => navigate("progress")} secondary />
      </TweaksPanel>
    </div>
  );
};

const ScreenStub = ({ title, desc, onBack }) => (
  <div className="screen container" style={{ paddingTop: 80, paddingBottom: 80, textAlign: "center" }}>
    <div style={{ display: "inline-grid", placeItems: "center", width: 48, height: 48, borderRadius: 12, background: "var(--surface)", border: "1px solid var(--line)", color: "var(--brand)", marginBottom: 16 }}>
      <Icon name="message" size={20} />
    </div>
    <h1 className="h-1">{title}</h1>
    <p className="muted" style={{ marginTop: 8, fontSize: 14, maxWidth: 420, margin: "8px auto 0" }}>{desc}</p>
    <button className="btn btn-secondary" style={{ marginTop: 20 }} onClick={onBack}>
      <Icon name="arrowLeft" size={12} /> 返回首页
    </button>
  </div>
);

ReactDOM.createRoot(document.getElementById("root")).render(<App />);
