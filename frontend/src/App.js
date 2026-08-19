import { useMemo, useState } from "react";
import { BrowserRouter, Routes, Route, Navigate, Link, useLocation, useNavigate, useParams } from "react-router-dom";
import { ArrowRight, Bell, BriefcaseBusiness, Check, ChevronDown, Clock3, Compass, Copy, Download, FileCheck2, Filter, Heart, Home as HomeIcon, Layers3, LogOut, Menu, Search, Settings, Share2, Sparkles, Target, Upload, X, Zap } from "lucide-react";
import "@/App.css";

const skills = ["React", "JavaScript", "TypeScript", "UI/UX", "Python", "Machine Learning", "Node.js", "Figma", "Cloud", "Communication"];
const demoUser = { name: "Aarav Mehta", email: "aarav@demo.com", role: "student", college: "Vellore Institute of Technology", degree: "B.Tech Computer Science", location: "Bengaluru, India", skills: ["React", "JavaScript", "UI/UX"], interests: ["Internships", "Hackathons", "Projects"], goal: "Software Engineer" };
function getCurrentUser() {
  return read("skillbridge_user", demoUser);
}
const opportunities = [
  { id: "frontend-intern", title: "Frontend Developer Intern", org: "TechNova", type: "Internship", location: "Remote", mode: "Remote", skills: ["React", "JavaScript", "UI/UX"], deadline: "25 Aug 2026", score: 94, color: "violet", description: "Join a product team building the next generation of collaborative tools. Ship thoughtful interfaces with experienced mentors." },
  { id: "ai-research", title: "AI / ML Research Intern", org: "Nexa Labs", type: "Research", location: "Pune, India", mode: "Hybrid", skills: ["Python", "Machine Learning"], deadline: "31 Aug 2026", score: 76, color: "cyan", description: "Explore applied machine learning research and turn experiments into useful product intelligence." },
  { id: "fullstack", title: "Full Stack Developer", org: "Orbit Systems", type: "Full-time", location: "Bengaluru, India", mode: "On-site", skills: ["React", "Node.js", "Cloud"], deadline: "12 Sep 2026", score: 82, color: "blue", description: "Build reliable, elegant software for teams that care about craft, speed, and customer impact." },
  { id: "design", title: "UI/UX Design Internship", org: "Morrow Studio", type: "Internship", location: "Remote", mode: "Remote", skills: ["Figma", "UI/UX"], deadline: "04 Sep 2026", score: 71, color: "pink", description: "Shape clear, expressive experiences across a growing family of products." },
  { id: "cyber", title: "Cybersecurity Intern", org: "SecureGrid", type: "Internship", location: "Hyderabad, India", mode: "Hybrid", skills: ["Python", "Cloud"], deadline: "18 Sep 2026", score: 68, color: "amber", description: "Help teams build safer systems through practical security research and automation." },
  { id: "freelance", title: "React Developer Freelance Project", org: "Pollen Commerce", type: "Freelance", location: "Remote", mode: "Remote", skills: ["React", "TypeScript"], deadline: "29 Aug 2026", score: 88, color: "green", description: "Create an inviting storefront experience for an independent marketplace with a global audience." },
  { id: "robotics", title: "Robotics Research Project", org: "Axiom Robotics", type: "Project", location: "Chennai, India", mode: "On-site", skills: ["Python", "IoT"], deadline: "22 Sep 2026", score: 62, color: "orange", description: "Collaborate with a curious research group exploring perception and motion." },
  { id: "startup", title: "Startup Product Intern", org: "Goodfolk", type: "Startup", location: "Remote", mode: "Remote", skills: ["Communication", "UI/UX"], deadline: "15 Sep 2026", score: 79, color: "lime", description: "Work closely with founders to bring new ideas from first sketch to first customer." }
];
function getPersonalizedOpportunities(user) {
  const userSkills = user?.skills || [];

  return opportunities.map((opportunity) => {
    const matchedSkills = opportunity.skills.filter(skill =>
      userSkills.some(userSkill =>
        userSkill.toLowerCase() === skill.toLowerCase()
      )
    );

    const matchBonus = matchedSkills.length * 8;

    return {
      ...opportunity,
      score: Math.min(99, Math.max(50, opportunity.score + matchBonus)),
      matchedSkills
    };
  });
}
const defaultApps = [{ id: "app-1", opportunityId: "frontend-intern", appliedAt: "18 Aug 2026", status: "Under Review" }, { id: "app-2", opportunityId: "freelance", appliedAt: "12 Aug 2026", status: "Shortlisted" }];

function read(key, fallback) { try { return JSON.parse(localStorage.getItem(key)) || fallback; } catch { return fallback; } }
function save(key, value) { localStorage.setItem(key, JSON.stringify(value)); }
const backendUrl = process.env.REACT_APP_BACKEND_URL?.replace(/\/$/, "");
const API = backendUrl ? `${backendUrl}/api` : null;
async function syncApi(path, options = {}) {
  if (!API) return null;
  try {
    return await fetch(`${API}${path}`, {
      headers: { "Content-Type": "application/json" },
      ...options
    });
  } catch {
    return null;
  }
}

function Brand({ compact = false }) { return <Link to="/home" className={`brand ${compact ? "brand-compact" : ""}`} data-testid="brand-home-link"><span className="brand-mark"><span /></span><span>SKILL<span>BRIDGE</span></span></Link>; }

function Landing() { const nav = useNavigate(); const choose = (role) => { save("skillbridge_role", role); nav(`/${role}/login`); }; return <main className="landing page-grid" data-testid="role-selection-page"><div className="landing-nav"><Brand compact /><span className="eyebrow"><span className="pulse-dot" /> AI-POWERED OPPORTUNITY PLATFORM</span></div><section className="landing-hero"><div className="hero-copy"><div className="eyebrow">BRIDGE YOUR NEXT CHAPTER</div><h1>Bridge your skills.<br /><em>Discover</em> your opportunities.</h1><p>AI-powered opportunities built around what you can do.</p><div className="hero-note"><Sparkles size={16} /> Curated for your potential, not just your resume.</div></div><div className="role-grid"><RoleCard role="student" icon={<Compass />} title="I'm a Student" text="Discover internships, hackathons, projects, competitions, research opportunities and career experiences matched to your skills." onClick={() => choose("student")} /><RoleCard role="professional" icon={<BriefcaseBusiness />} title="I'm a Skilled Professional" text="Showcase your expertise and discover projects, freelance work, collaborations and professional opportunities that match your skills." onClick={() => choose("professional")} /></div></section><div className="landing-footer"><span>Trusted by ambitious people building what’s next</span><span className="footer-line" /><span>01 / 02</span></div></main>; }
function RoleCard({ role, icon, title, text, onClick }) { return <button className={`role-card ${role}`} onClick={onClick} data-testid={`${role}-role-card`}><div className="role-card-top"><div className="icon-box">{icon}</div><span className="arrow-circle"><ArrowRight size={18} /></span></div><div><span className="card-kicker">{role === "student" ? "FOR THE CURIOUS" : "FOR THE CAPABLE"}</span><h2>{title}</h2><p>{text}</p></div><span className="card-cta">Continue as {role === "student" ? "Student" : "Skilled Professional"} <ArrowRight size={15} /></span></button>; }

function Auth({ role }) {
  const nav = useNavigate();
  const location = useLocation();

  const [signup, setSignup] = useState(
    location.pathname.includes("/signup")
  );

  const [demo, setDemo] = useState(false);
  const [error, setError] = useState("");

  const [form, setForm] = useState({
    name: "",
    email: "",
    password: "",
    confirm: ""
  });

  const [forgot, setForgot] = useState(false);
  const [forgotEmail, setForgotEmail] = useState("");
  const [forgotSent, setForgotSent] = useState(false);

  const roleName =
    role === "student" ? "Student" : "Skilled Professional";

  const submit = (e) => {
    e.preventDefault();
    setError("");

    const email = form.email.trim().toLowerCase();

    // -----------------------------
    // BASIC VALIDATION
    // -----------------------------

    if (!email || !form.password) {
      setError("Please complete all required fields.");
      return;
    }

    if (signup && !form.name.trim()) {
      setError("Please enter your full name.");
      return;
    }

    if (signup && form.password !== form.confirm) {
      setError("Passwords do not match.");
      return;
    }

    if (form.password.length < 8) {
      setError("Password must be at least 8 characters.");
      return;
    }

    // -----------------------------
    // GET REGISTERED ACCOUNTS
    // -----------------------------

    const accounts = read("skillbridge_accounts", {});

    // =====================================================
    // SIGN UP
    // =====================================================

    if (signup) {
      // Check whether account already exists
      if (accounts[email]) {
        setError(
          "An account with this email already exists. Please sign in."
        );
        return;
      }

      const user = {
        ...demoUser,
        name: form.name.trim(),
        email,
        role,
        skills: [],
        interests: [],
        college: "",
        degree: "",
        location: "",
        goal: ""
      };

      // Save account permanently
      accounts[email] = {
        password: form.password,
        role,
        profile: user
      };

      save("skillbridge_accounts", accounts);

      // Save currently logged-in user
      save("skillbridge_user", user);

      // Keep backend sync
      syncApi("/users", {
        method: "POST",
        body: JSON.stringify(user)
      });

      // First-time user → onboarding
      nav("/onboarding");

      return;
    }

    // =====================================================
    // LOGIN
    // =====================================================

    const account = accounts[email];

    // No registered account
    if (!account) {
      setError(
        "No account found with this email. Please create an account first."
      );
      return;
    }

    // Wrong password
    if (account.password !== form.password) {
      setError("Incorrect password. Please try again.");
      return;
    }

    // Check role
    if (account.role && account.role !== role) {
      setError(
        `This account is registered as a ${
          account.role === "student"
            ? "Student"
            : "Skilled Professional"
        }.`
      );
      return;
    }

    // Restore saved profile
    const user = {
      ...demoUser,
      ...(account.profile || {}),
      email,
      role: account.role || role
    };

    // Save current session
    save("skillbridge_user", user);

    // Sync backend
    syncApi("/users", {
      method: "POST",
      body: JSON.stringify(user)
    });

    // Existing user → DIRECTLY HOME
    nav("/home");
  };

  // =====================================================
  // DEMO LOGIN
  // =====================================================

  const useDemo = () => {
    const user = {
      ...demoUser,
      role,
      ...(role === "professional"
        ? {
            name: "Maya Chen",
            email: "maya@demo.com",
            goal: "Product Design Lead",
            degree: "8 years experience",
            college: "Independent Product Studio",
            skills: ["Figma", "UI/UX", "Communication"]
          }
        : {})
    };

    save("skillbridge_user", user);

    syncApi("/users", {
      method: "POST",
      body: JSON.stringify(user)
    });

    save("skillbridge_apps", defaultApps);

    setDemo(true);

    setTimeout(() => {
      nav("/home");
    }, 350);
  };

  // =====================================================
  // FORGOT PASSWORD
  // =====================================================

  const sendReset = () => {
    if (!forgotEmail.trim()) {
      return;
    }

    setForgotSent(true);
  };

  const closeForgot = () => {
    setForgot(false);
    setForgotSent(false);
    setForgotEmail("");
  };

  return (
    <main className="auth-page">

      <div className="auth-aside">

        <Brand />

        <div className="auth-aside-copy">

          <span className="eyebrow">
            {roleName.toUpperCase()} JOURNEY
          </span>

          <h1>
            Make your next move <em>matter.</em>
          </h1>

          <p>
            One profile. Better-fit opportunities. A bridge from
            what you know to what’s possible.
          </p>

          <div className="proof">

            <div className="avatar-stack">
              <span>AM</span>
              <span>RK</span>
              <span>+</span>
            </div>

            <b>Built for people in motion</b>

          </div>

        </div>

      </div>

      <div className="auth-panel">

        <Link className="back-link" to="/">
          <ArrowRight
            size={15}
            className="back-icon"
          />

          Back to role selection
        </Link>

        <div className="auth-form-wrap">

          <div className="eyebrow">
            WELCOME TO SKILLBRIDGE
          </div>

          <h2>
            {signup
              ? "Create your profile"
              : "Welcome back"}
          </h2>

          <p className="muted">
            {signup
              ? `Start your ${roleName.toLowerCase()} journey today.`
              : "Your next opportunity is closer than you think."}
          </p>

          {error && (
            <div
              className="form-error"
              data-testid="auth-error"
            >
              <X size={15} />
              {error}
            </div>
          )}

          <form
            onSubmit={submit}
            data-testid="auth-form"
          >

            {signup && (
              <Field
                label="Full name"
                value={form.name}
                onChange={(v) =>
                  setForm({
                    ...form,
                    name: v
                  })
                }
                test="auth-name-input"
                placeholder="Your full name"
              />
            )}

            <Field
              label="Email address"
              value={form.email}
              onChange={(v) =>
                setForm({
                  ...form,
                  email: v
                })
              }
              test="auth-email-input"
              placeholder="you@example.com"
              type="email"
            />

            <Field
              label="Password"
              value={form.password}
              onChange={(v) =>
                setForm({
                  ...form,
                  password: v
                })
              }
              test="auth-password-input"
              placeholder="At least 8 characters"
              type="password"
            />

            {signup && (
              <Field
                label="Confirm password"
                value={form.confirm}
                onChange={(v) =>
                  setForm({
                    ...form,
                    confirm: v
                  })
                }
                test="auth-confirm-input"
                placeholder="Repeat your password"
                type="password"
              />
            )}

            <button
              className="primary-btn full"
              type="submit"
              data-testid="auth-submit-button"
            >
              {signup
                ? "Create account"
                : "Sign in"}

              <ArrowRight size={17} />
            </button>

          </form>

          <button
            className="demo-btn"
            onClick={useDemo}
            data-testid="demo-access-button"
          >
            <Zap size={16} />

            Enter demo as {roleName}

            <span>Instant access</span>
          </button>

          <div className="auth-switch">

            {signup
              ? "Already have an account?"
              : "New to SKILLBRIDGE?"}

            {" "}

            <button
              onClick={() => {
                setSignup(!signup);
                setError("");
              }}
              data-testid="auth-mode-toggle"
            >
              {signup
                ? "Sign in"
                : "Create an account"}
            </button>

          </div>

          <button
            className="forgot"
            onClick={() => setForgot(true)}
            data-testid="forgot-password-button"
          >
            Forgot password?
          </button>

          {demo && (
            <div
              className="success-note"
              data-testid="demo-success-message"
            >
              Welcome back — loading your workspace.
            </div>
          )}

        </div>

      </div>

      <Modal
        open={forgot}
        onClose={closeForgot}
        testid="forgot-password-modal"
        eyebrow="RESET LINK"
        title={
          forgotSent
            ? "Check your inbox"
            : "Send yourself a reset"
        }
      >

        {forgotSent ? (
          <>
            <p className="muted">
              A secure reset link is on its way to{" "}
              <b style={{ color: "var(--white)" }}>
                {forgotEmail}
              </b>
              . Follow the link within 15 minutes.
            </p>

            <button
              className="primary-btn full"
              onClick={closeForgot}
              data-testid="forgot-done-button"
            >
              Got it
              <Check size={17} />
            </button>
          </>
        ) : (
          <>
            <p className="muted">
              We’ll send a one-time reset link to your email.
            </p>

            <Field
              label="Email address"
              value={forgotEmail}
              onChange={setForgotEmail}
              test="forgot-email-input"
              placeholder="you@example.com"
              type="email"
            />

            <button
              className="primary-btn full"
              onClick={sendReset}
              data-testid="forgot-submit-button"
            >
              Send reset link
              <ArrowRight size={17} />
            </button>
          </>
        )}

      </Modal>

    </main>
  );
}
function Field({ label, value, onChange, test, placeholder, type = "text" }) { return <label className="field"><span>{label}</span><input data-testid={test} type={type} value={value} placeholder={placeholder} onChange={e => onChange(e.target.value)} /></label>; }
function Modal({ open, onClose, title, eyebrow, testid, children, footer }) { if (!open) return null; return <div className="modal-backdrop" data-testid={testid} onClick={e => e.target === e.currentTarget && onClose()}><div className="modal-panel"><button className="modal-close" onClick={onClose} data-testid={`${testid}-close`}><X size={17} /></button>{eyebrow && <span className="eyebrow">{eyebrow}</span>}<h2>{title}</h2>{children}{footer && <div className="modal-footer">{footer}</div>}</div></div>; }

function Onboarding() { const nav = useNavigate(); const stored = read("skillbridge_user", demoUser); const [user, setUser] = useState(stored); const [step, setStep] = useState(1); const [selected, setSelected] = useState(user.skills || []); const [interests, setInterests] = useState(user.interests || []); const professional = user.role === "professional"; const update = (k, v) => setUser({ ...user, [k]: v }); const toggleInterest = (x) => setInterests(interests.includes(x) ? interests.filter(y => y !== x) : [...interests, x]); const next = () => { if (step < 4) return setStep(step + 1); const final = { ...user, skills: selected, interests }; save("skillbridge_user", final);

// Also update the permanent account profile
const accounts = read("skillbridge_accounts", {});
const email = final.email?.trim().toLowerCase();

if (email && accounts[email]) {
  accounts[email] = {
    ...accounts[email],
    role: final.role,
    profile: final
  };

  save("skillbridge_accounts", accounts);
}

syncApi("/users", {
  method: "POST",
  body: JSON.stringify(final)
});

nav("/home");}; return <main className="onboarding page-grid"><div className="onboard-top"><Brand compact /><span className="step-count">STEP 0{step} <span>/ 04</span></span></div><section className="onboard-content"><div className="onboard-intro"><span className="eyebrow">{professional ? "PROFESSIONAL SETUP" : "STUDENT SETUP"}</span><h1>Let’s make your<br /><em>profile useful.</em></h1><p>A few thoughtful details help us find opportunities that fit the real you.</p></div><div className="onboard-form"><div className="progress-bar"><span style={{ width: `${step * 25}%` }} /></div>{step === 1 && <><h2>First, the basics</h2><p className="muted">Tell us how to introduce you.</p><Field label="Full name" value={user.name} onChange={v => update("name", v)} test="onboarding-name-input" placeholder="Your full name" /><Field label={professional ? "Professional title" : "College / university"} value={user.college} onChange={v => update("college", v)} test="onboarding-title-input" placeholder="Add a detail" /><div className="two-fields"><Field label="Location" value={user.location} onChange={v => update("location", v)} test="onboarding-location-input" placeholder="City, country" /><Field label={professional ? "Years of experience" : "Current year"} value={user.degree} onChange={v => update("degree", v)} test="onboarding-experience-input" placeholder="Choose" /></div></>}{step === 2 && <><h2>What are you good at?</h2><p className="muted">Pick the skills you want opportunities to notice.</p><div className="selected-chips">{selected.map(s => <span key={s}>{s}<button onClick={() => setSelected(selected.filter(x => x !== s))} data-testid={`remove-skill-${s.toLowerCase().replaceAll("/", "-")}`}><X size={13} /></button></span>)}</div><div className="skill-picker">{skills.map(s => <button className={selected.includes(s) ? "chosen" : ""} onClick={() => setSelected(selected.includes(s) ? selected.filter(x => x !== s) : [...selected, s])} key={s} data-testid={`skill-option-${s.toLowerCase().replaceAll("/", "-")}`}>{selected.includes(s) && <Check size={14} />}{s}</button>)}</div></>}{step === 3 && <><h2>{professional ? "How do you want to work?" : "What pulls you forward?"}</h2><p className="muted">Choose a few directions. You can always change them.</p><div className="interest-list">{(professional ? ["Full-time", "Part-time", "Freelance", "Contract", "Project-based", "Collaboration"] : ["Internships", "Hackathons", "Projects", "Freelancing", "Research", "Competitions", "Scholarships", "Workshops"]).map(x => <button className={interests.includes(x) ? "chosen" : ""} key={x} onClick={() => toggleInterest(x)} data-testid={`interest-option-${x.toLowerCase().replaceAll(" ", "-")}`}><span>{x}</span>{interests.includes(x) && <Check size={15} />}</button>)}</div></>}{step === 4 && <div className="ready-state"><div className="ready-icon"><Check /></div><h2>Your profile is ready.</h2><p className="muted">We’ll use your profile to surface a sharper set of possibilities.</p><div className="completion"><span>Profile completion</span><b>{Math.min(95, 60 + selected.length * 4 + interests.length * 3)}%</b><div><i style={{ width: `${Math.min(95, 60 + selected.length * 4 + interests.length * 3)}%` }} /></div></div></div>}<button className="primary-btn full" onClick={next} data-testid="onboarding-next-button">{step === 4 ? "Enter SKILLBRIDGE" : "Continue"}<ArrowRight size={17} /></button></div></section></main>; }

function Protected({ children }) { return read("skillbridge_user", null) ? children : <Navigate to="/" replace />; }
function Layout({ children }) { const loc = useLocation(); const nav = useNavigate(); const user = read("skillbridge_user", demoUser); const [menu, setMenu] = useState(false); const logout = () => { localStorage.removeItem("skillbridge_user"); nav("/"); }; const links = [["/home", "Home", HomeIcon], ["/dashboard", "Dashboard", Layers3], ["/opportunities", "Opportunities", Compass], ["/applications", "My Applications", FileCheck2], ...(user.role === "professional" ? [["/workspace", "Workspace", BriefcaseBusiness]] : [])]; return <div className="app-shell"><header className="app-nav"><Brand compact /><nav className={menu ? "open" : ""}>{links.map(([path, label, Icon]) => <Link className={loc.pathname === path ? "active" : ""} to={path} key={path} data-testid={`nav-${label.toLowerCase().replaceAll(" ", "-")}-link`}><Icon size={16} />{label}</Link>)}</nav><div className="nav-actions"><Link to="/notifications" className="notification-btn" data-testid="notifications-link"><Bell size={18} /><span /></Link><Link to="/profile" className="profile-trigger" data-testid="profile-menu-button"><span className="avatar">{user.role === "professional" ? "MC" : "AM"}</span><span className="profile-name">{user.name}</span><ChevronDown size={15} /></Link><button className="mobile-menu" onClick={() => setMenu(!menu)} data-testid="mobile-menu-button"><Menu /></button></div></header>{children}<button className="logout-fab" onClick={logout} data-testid="logout-button"><LogOut size={14} /> Log out</button></div>; }

function Home() { const nav = useNavigate(); const user = getCurrentUser();
const apps = read("skillbridge_apps", []);
const personalizedOpportunities = getPersonalizedOpportunities(user); return <Layout><main className="content"><section className="welcome-band"><div><span className="eyebrow">AI POWERED SKILL MATCH</span><h1>Find opportunities<br /><em>that fit you.</em></h1><p>Tell SKILLBRIDGE what you can do. We’ll help you discover what fits your skills, interests and potential.</p><div className="button-row"><button className="primary-btn" onClick={() => nav("/skill-match")} data-testid="check-skill-match-button">Check my skill match <ArrowRight size={17} /></button><button className="ghost-btn" onClick={() => nav("/dashboard")} data-testid="go-dashboard-button">Go to dashboard</button></div></div><div className="match-orbit"><div className="orbit-ring"><div><b>94%</b><span>match</span></div></div><span className="orbit-label label-one">React <small>strong</small></span><span className="orbit-label label-two">TypeScript <small>next up</small></span></div></section><section className="section-block"><div className="section-heading"><div><span className="eyebrow">KEEP MOVING</span><h2>My Applications</h2></div><Link to="/applications" className="text-link" data-testid="view-all-applications-link">View all <ArrowRight size={15} /></Link></div><div className="application-strip">{apps.slice(0, 2).map(a => { const o = opportunities.find(x => x.id === a.opportunityId); return <ApplicationRow key={a.id} app={a} opportunity={o} /> })}</div></section><section className="section-block"><div className="section-heading"><div><span className="eyebrow">CURATED FOR YOU</span><h2>Latest opportunities</h2></div><Link to="/opportunities" className="text-link" data-testid="view-all-opportunities-link">Explore all <ArrowRight size={15} /></Link></div><div className="opportunity-grid">{personalizedOpportunities.slice(0, 3).map(o =>  <Oppo rtunityCard key={o.id} opportunity={o} />)}</div></section></main></Layout>; }
function ApplicationRow({ app, opportunity }) { return <div className="application-row" data-testid={`application-row-${app.id}`}><div className={`company-icon ${opportunity.color}`}>{opportunity.org.slice(0, 1)}</div><div className="application-title"><b>{opportunity.title}</b><span>{opportunity.org} · Applied {app.appliedAt}</span></div><span className={`status ${app.status.toLowerCase().replaceAll(" ", "-")}`}>{app.status}</span><button className="icon-btn" data-testid={`view-application-${app.id}`}><ArrowRight size={17} /></button></div>; }
function OpportunityCard({ opportunity }) { const nav = useNavigate(); const apps = read("skillbridge_apps", defaultApps); const saved = read("skillbridge_saved", []); const [isSaved, setSaved] = useState(saved.includes(opportunity.id)); const toggle = () => { const next = isSaved ? saved.filter(x => x !== opportunity.id) : [...saved, opportunity.id]; save("skillbridge_saved", next); setSaved(!isSaved); }; return <article className="opportunity-card" data-testid={`opportunity-card-${opportunity.id}`}><div className="opp-top"><div className={`company-icon ${opportunity.color}`}>{opportunity.org.slice(0, 1)}</div><button className={`save-btn ${isSaved ? "saved" : ""}`} onClick={toggle} data-testid={`save-opportunity-${opportunity.id}`}><Heart size={17} fill={isSaved ? "currentColor" : "none"} /></button></div><span className="opp-type">{opportunity.type}</span><h3>{opportunity.title}</h3><p className="org-name">{opportunity.org}</p><div className="opp-meta"><span><Compass size={14} />{opportunity.location}</span><span><Clock3 size={14} />Due {opportunity.deadline}</span></div><div className="tag-row">{opportunity.skills.map(s => <span key={s}>{s}</span>)}</div><div className="opp-footer"><div className="score"><span>AI match</span><b>{opportunity.score}%</b></div><button className="card-link" onClick={() => nav(`/opportunities/${opportunity.id}`)} data-testid={`view-opportunity-${opportunity.id}`}>View details <ArrowRight size={15} /></button></div></article>; }

function Dashboard() { const user = read("skillbridge_user", demoUser); return <Layout><main className="content"><section className="page-intro"><div><span className="eyebrow">OVERVIEW</span><h1>Good morning, {user.name.split(" ")[0]} <span className="wave">👋</span></h1><p>Here’s your SKILLBRIDGE opportunity overview.</p></div><div className="date-chip">August 2026 <ChevronDown size={15} /></div></section><div className="stat-grid">{[["AI Skill Match", "94%", "↑ 8% this month", "violet"], ["Applications", "12", "3 in progress", "cyan"], ["Saved opportunities", "08", "2 new this week", "blue"], ["New matches", "05", "Since yesterday", "amber"]].map(([a,b,c,d]) => <div className={`stat-card ${d}`} key={a} data-testid={`stat-${a.toLowerCase().replaceAll(" ", "-")}`}><span>{a}</span><strong>{b}</strong><small><i />{c}</small></div>)}</div><div className="dashboard-grid"><section className="match-panel"><div className="section-heading"><div><span className="eyebrow">YOUR SIGNAL</span><h2>Skill match health</h2></div><Target size={21} /></div><div className="match-health"><div className="large-ring"><b>94%</b><span>match</span></div><div className="skill-breakdown">{[["React", "Strong match", "strong"], ["JavaScript", "Strong match", "strong"], ["UI/UX", "Good match", "good"], ["TypeScript", "Recommended", "recommend"]].map(([a,b,c]) => <div className="skill-line" key={a}><span className={`mini-status ${c}`} /> <b>{a}</b><small>{b}</small></div>)}</div></div><Link to="/skill-match" className="outline-btn" data-testid="dashboard-skill-match-link">See full skill analysis <ArrowRight size={16} /></Link></section><section className="activity-panel"><div className="section-heading"><div><span className="eyebrow">RECENT ACTIVITY</span><h2>Stay in the loop</h2></div><Bell size={20} /></div>{["Your profile is 90% complete", "New 96% match found", "Application status changed"].map((x,i) => <div className="activity-item" key={x}><span className={`activity-dot dot-${i}`} /><div><b>{x}</b><small>{i === 0 ? "Add a portfolio to stand out" : i === 1 ? "Frontend role at Lumen" : "TechNova moved your application"}</small></div><span className="activity-time">{i + 1}h</span></div>)}</section></div></main></Layout>; }

function Opportunities() { const [query, setQuery] = useState(""); const [type, setType] = useState("All"); const filtered = useMemo(() => opportunities.filter(o => (type === "All" || o.type === type) && `${o.title} ${o.org} ${o.skills.join(" ")}`.toLowerCase().includes(query.toLowerCase())), [query,type]); return <Layout><main className="content"><section className="page-intro"><div><span className="eyebrow">THE OPPORTUNITY INDEX</span><h1>Find your next <em>yes.</em></h1><p>Thoughtful matches for where you are — and where you want to go.</p></div><div className="opportunity-count"><b>{filtered.length}</b><span>opportunities found</span></div></section><div className="search-toolbar"><div className="search-field"><Search size={18} /><input data-testid="opportunity-search-input" placeholder="Search opportunities..." value={query} onChange={e => setQuery(e.target.value)} /></div><div className="filter-group"><Filter size={16} />{["All", "Internship", "Research", "Freelance", "Project"].map(x => <button className={type === x ? "active" : ""} key={x} onClick={() => setType(x)} data-testid={`filter-${x.toLowerCase()}-button`}>{x}</button>)}</div></div>{filtered.length ? <div className="opportunity-grid all-opps">{filtered.map(o => <OpportunityCard key={o.id} opportunity={o} />)}</div> : <div className="empty-state" data-testid="no-search-results"><Search size={26} /><h2>No opportunities found</h2><p>Try a different search or broaden your filters.</p></div>}</main></Layout>; }
function OpportunityDetail() { const { id } = useParams(); const nav = useNavigate(); const o = opportunities.find(x => x.id === id) || opportunities[0]; const already = read("skillbridge_apps", defaultApps).some(a => a.opportunityId === o.id); const [isSaved, setSaved] = useState(read("skillbridge_saved", []).includes(o.id)); const user = read("skillbridge_user", demoUser); const apply = () => nav(`/apply/${o.id}`); const toggleSave = () => { const saved = read("skillbridge_saved", []); const next = isSaved ? saved.filter(x => x !== o.id) : [...saved, o.id]; save("skillbridge_saved", next); syncApi("/saved/toggle", { method: "POST", body: JSON.stringify({ email: user.email, opportunity_id: o.id }) }); setSaved(!isSaved); }; return <Layout><main className="content detail-page"><Link to="/opportunities" className="back-link" data-testid="back-to-opportunities-link">← Back to opportunities</Link><div className="detail-layout"><article className="detail-main"><div className={`detail-logo ${o.color}`}>{o.org.slice(0,1)}</div><span className="opp-type">{o.type} · {o.mode}</span><h1>{o.title}</h1><p className="detail-org">{o.org} <span>·</span> {o.location}</p><div className="detail-divider" /><h2>About the opportunity</h2><p className="detail-copy">{o.description} You’ll work with a supportive team, learn by doing, and leave with work you’re proud to show.</p><h2>What you’ll bring</h2><div className="detail-tags">{o.skills.map(s => <span key={s}>{s}</span>)}</div><h2>What we offer</h2><div className="offer-grid"><span>✦ Flexible mentorship</span><span>✦ Real product ownership</span><span>✦ Learning budget</span><span>✦ Certificate of completion</span></div></article><aside className="apply-aside"><div className="aside-score"><span>AI SKILL MATCH</span><b>{o.score}%</b><p>Your skills are a strong fit for this role.</p></div><div className="aside-facts"><span><Clock3 /> Deadline <b>{o.deadline}</b></span><span><Compass /> Work mode <b>{o.mode}</b></span><span><BriefcaseBusiness /> Duration <b>3–6 months</b></span></div><button className="primary-btn full" onClick={apply} data-testid="apply-now-button">{already ? "Review application" : "Apply now"} <ArrowRight size={17} /></button><button className={`outline-btn full ${isSaved ? "saved-detail" : ""}`} onClick={toggleSave} data-testid="save-detail-opportunity-button"><Heart size={16} fill={isSaved ? "currentColor" : "none"} /> {isSaved ? "Opportunity saved" : "Save opportunity"}</button></aside></div></main></Layout>; }
function Applications() { const apps = read("skillbridge_apps", defaultApps); return <Layout><main className="content"><section className="page-intro"><div><span className="eyebrow">YOUR JOURNEY</span><h1>My applications</h1><p>Every thoughtful step forward, in one place.</p></div><Link to="/opportunities" className="primary-btn" data-testid="explore-opportunities-button">Explore opportunities <ArrowRight size={16} /></Link></section><div className="applications-list">{apps.map(a => <ApplicationRow key={a.id} app={a} opportunity={opportunities.find(o => o.id === a.opportunityId) || opportunities[0]} />)}</div></main></Layout>; }
function ApplicationFlow() { const { id } = useParams(); const nav = useNavigate(); const user = read("skillbridge_user", demoUser); const o = opportunities.find(x => x.id === id) || opportunities[0]; const [step, setStep] = useState(1); const [resume, setResume] = useState(""); const [cover, setCover] = useState(""); const [submitted, setSubmitted] = useState(false); const submit = () => { const app = { id: `app-${Date.now()}`, opportunityId: o.id, appliedAt: "Today", status: "Applied", resumeName: resume || "Aarav_Mehta_Resume.pdf", coverLetter: cover }; const current = read("skillbridge_apps", defaultApps).filter(a => a.opportunityId !== o.id); save("skillbridge_apps", [...current, app]); syncApi("/applications", { method: "POST", body: JSON.stringify({ email: user.email, opportunity_id: o.id, resume_name: app.resumeName, skills: user.skills, cover_letter: cover }) }); setSubmitted(true); }; if (submitted) return <Layout><main className="content success-page" data-testid="application-success"><div className="ready-icon"><Check /></div><span className="eyebrow">APPLICATION SENT</span><h1>Application submitted<br /><em>successfully.</em></h1><p>Your application for {o.title} at {o.org} is now in My Applications.</p><div className="button-row"><button className="primary-btn" onClick={() => nav("/applications")} data-testid="track-application-button">Track application <ArrowRight size={17} /></button><button className="ghost-btn" onClick={() => nav("/opportunities")} data-testid="back-to-opportunities-success">Explore more</button></div></main></Layout>; return <Layout><main className="content apply-page"><Link to={`/opportunities/${o.id}`} className="back-link" data-testid="back-to-opportunity-detail">← Back to opportunity</Link><div className="apply-header"><div><span className="eyebrow">APPLICATION / {o.org.toUpperCase()}</span><h1>Put your best<br /><em>foot forward.</em></h1></div><span className="step-count" data-testid={`application-step-count-${step}`}>STEP 0{step} <span>/ 04</span></span></div><div className="apply-progress"><span style={{ width: `${step * 25}%` }} /></div><section className="apply-form-panel" data-testid={`application-step-${step}`}>{step === 1 && <><span className="eyebrow">01 / PROFILE</span><h2>Confirm your profile</h2><p className="muted">We’ll share these details with the opportunity team.</p><div className="review-facts"><span>Full name<b>{user.name}</b></span><span>Email<b>{user.email}</b></span><span>Location<b>{user.location}</b></span><span>Top skill<b>{user.skills[0]}</b></span></div></>}{step === 2 && <><span className="eyebrow">02 / RESUME</span><h2>Show us your story</h2><p className="muted">Upload a resume or use your saved profile.</p><label className="upload-box"><Upload size={22} /><b>{resume || "Choose a resume PDF"}</b><small>PDF up to 10 MB</small><input type="file" accept=".pdf" onChange={e => setResume(e.target.files[0]?.name || "")} data-testid="resume-upload-input" /></label></>}{step === 3 && <><span className="eyebrow">03 / INTRODUCTION</span><h2>Make it personal</h2><p className="muted">A thoughtful introduction is often the difference.</p><textarea className="cover-input" value={cover} onChange={e => setCover(e.target.value)} placeholder={`Why are you excited about ${o.org}?`} data-testid="cover-letter-input" /><span className="character-count">{cover.length} / 600</span></>}{step === 4 && <><span className="eyebrow">04 / REVIEW</span><h2>Ready when you are.</h2><div className="submission-card"><b>{o.title}</b><span>{o.org} · {o.location}</span><span>Resume · {resume || "Saved profile resume"}</span><span>Introduction · {cover ? "Added" : "Profile-first application"}</span></div><p className="muted">By submitting, you confirm your profile details are current.</p></>}<div className="apply-buttons">{step > 1 && <button className="ghost-btn" onClick={() => setStep(step - 1)} data-testid="application-back-button">Back</button>}<button className="primary-btn full" onClick={() => step < 4 ? setStep(step + 1) : submit()} data-testid={step === 4 ? "application-submit-button" : "application-next-button"}>{step === 4 ? "Submit application" : "Continue"}<ArrowRight size={17} /></button></div></section></main></Layout>; }

function Workspace() { const [user, setUser] = useState(read("skillbridge_user", { ...demoUser, role: "professional", name: "Maya Chen" })); const [editing, setEditing] = useState(false); return <Layout><main className="content workspace-page"><section className="workspace-hero"><span className="eyebrow">PROFESSIONAL WORKSPACE</span><h1>Make your expertise<br /><em>visible.</em></h1><p>One place to manage your availability, signal your strengths, and find work worthy of your craft.</p><button className="primary-btn" onClick={() => setEditing(true)} data-testid="workspace-edit-profile-button"><Settings size={16} /> Tune your profile</button></section><div className="workspace-stats"><div><span>Profile views</span><b>248</b><small>↑ 24% this month</small></div><div><span>Active conversations</span><b>06</b><small>2 need your reply</small></div><div><span>Match quality</span><b>91%</b><small>Above your category average</small></div></div><div className="workspace-grid"><section className="profile-section"><span className="eyebrow">YOUR POSITIONING</span><h2>{user.goal || "Product Design Lead"}</h2><p>Available for thoughtful teams and ambitious product collaborations.</p><div className="detail-tags">{(user.skills || ["Figma", "UI/UX", "Communication"]).map(s => <span key={s}>{s}</span>)}</div><div className="availability-line"><span>Availability</span><b>Open to project work</b></div><div className="availability-line"><span>Work preference</span><b>Remote · Hybrid</b></div></section><section className="profile-section"><span className="eyebrow">WORK THAT FITS</span><h2>Recommended for you</h2>{opportunities.filter(x => ["Freelance", "Full-time", "Startup"].includes(x.type)).slice(0, 3).map(o => <Link to={`/opportunities/${o.id}`} className="workspace-opportunity" key={o.id} data-testid={`workspace-opportunity-${o.id}`}><span className={`company-icon ${o.color}`}>{o.org[0]}</span><span><b>{o.title}</b><small>{o.org} · {o.score}% match</small></span><ArrowRight size={15} /></Link>)}</section></div><EditProfileModal user={user} open={editing} onClose={() => setEditing(false)} onSave={setUser} testid="workspace-edit-profile-modal" /></main></Layout>; }

function ShareMatchCard() { const [shared, setShared] = useState(false); const share = async () => { const text = "My SKILLBRIDGE AI Skill Match is 94% — React, JavaScript, and UI/UX. Find your fit at SKILLBRIDGE."; setShared(true); try { await navigator.clipboard.writeText(text); } catch { /* clipboard unavailable in some browsers */ } }; const download = () => { const blob = new Blob(["SKILLBRIDGE\nAI SKILL MATCH: 94%\nReact · JavaScript · UI/UX\nTypeScript recommended next"], { type: "text/plain" }); const url = URL.createObjectURL(blob); const link = document.createElement("a"); link.href = url; link.download = "skillbridge-match.txt"; link.click(); URL.revokeObjectURL(url); }; return <section className="share-card-panel"><div className="share-card"><div className="brand brand-compact"><span className="brand-mark"><span /></span><span>SKILL<span>BRIDGE</span></span></div><span className="eyebrow">PERSONAL SIGNAL</span><b>94%</b><span>AI SKILL MATCH</span><div className="share-card-tags"><i>React</i><i>JavaScript</i><i>UI/UX</i></div></div><div><span className="eyebrow">TAKE IT WITH YOU</span><h2>Share your signal.</h2><p className="muted">Give mentors and teams a clear snapshot of what you bring.</p><div className="button-row"><button className="outline-btn" onClick={share} data-testid="share-match-button"><Share2 size={15} /> {shared ? "Copied" : "Copy match"}</button><button className="ghost-btn" onClick={download} data-testid="download-match-button"><Download size={15} /> Download</button></div></div></section>; }
function SkillMatch() { const nav = useNavigate(); return <Layout><main className="content match-page"><section className="match-hero"><div className="eyebrow">YOUR AI SKILL MATCH</div><h1>Good signals.<br /><em>Clear direction.</em></h1><p>We compared your skills, interests and goals with the opportunity landscape.</p><div className="match-result"><div className="large-ring"><b>94%</b><span>match score</span></div><div><h2>You’re closer than you think.</h2><p>Your strongest signal is product-focused frontend work. Add TypeScript to unlock even more of the right opportunities.</p></div></div></section><div className="analysis-grid"><section><span className="eyebrow">THE BREAKDOWN</span><h2>What’s working</h2>{[["React", "Strong match", "Your strongest technical signal", "strong"], ["JavaScript", "Strong match", "High demand across your matches", "strong"], ["UI/UX", "Good match", "A differentiator for product teams", "good"], ["TypeScript", "Skill gap", "Recommended next step", "recommend"]].map(([a,b,c,d]) => <div className="analysis-row" key={a}><span className={`mini-status ${d}`} /><div><b>{a}</b><small>{c}</small></div><strong>{b}</strong></div>)}</section><section className="recommend-panel"><span className="eyebrow">RECOMMENDED NEXT</span><h2>Level up your match</h2><p>Three weeks of focused TypeScript practice could move your profile into the top 10% of frontend matches.</p><div className="recommend-progress"><span><b>TypeScript</b><b>+8% potential</b></span><div><i /></div></div><button className="outline-btn" onClick={() => nav("/opportunities")} data-testid="match-explore-button">See matched roles <ArrowRight size={16} /></button></section></div><ShareMatchCard /></main></Layout>; }
function Notifications() { const user = read("skillbridge_user", demoUser); const notifKey = `skillbridge_notif_read_${user.email}`; const seed = [["Your application status changed.", "TechNova moved your application to Under Review."], ["You have a new 96% skill match.", "Frontend Developer at Lumen is waiting for you."], ["Application deadline is tomorrow.", "Frontend Developer Intern closes in 24 hours."], ["You have 3 new opportunities.", "Curated from your latest skill signals."], ["Your profile is 90% complete.", "Add one more project to stand out."]]; const [readIds, setReadIds] = useState(read(notifKey, [])); const [toast, setToast] = useState(false); const isUnread = i => !readIds.includes(i); const markAll = () => { const all = seed.map((_, i) => i); setReadIds(all); save(notifKey, all); syncApi(`/notifications/${encodeURIComponent(user.email)}/read`, { method: "POST" }); setToast(true); setTimeout(() => setToast(false), 1800); }; const toggle = (i) => { const next = isUnread(i) ? [...readIds, i] : readIds.filter(x => x !== i); setReadIds(next); save(notifKey, next); }; const unreadCount = seed.length - readIds.length; return <Layout><main className="content"><section className="page-intro"><div><span className="eyebrow">INBOX{unreadCount > 0 ? ` · ${unreadCount} UNREAD` : " · ALL CAUGHT UP"}</span><h1>Notifications</h1><p>Small signals worth paying attention to.</p></div><button className="ghost-btn" onClick={markAll} disabled={unreadCount === 0} data-testid="mark-notifications-read-button">{unreadCount === 0 ? "All read" : "Mark all as read"}</button></section>{toast && <div className="success-note" data-testid="notifications-toast"><Check size={15} /> All notifications marked as read.</div>}<div className="notification-list">{seed.map(([title, desc], i) => <button className={`notification-item ${isUnread(i) ? "unread" : ""}`} key={title} onClick={() => toggle(i)} data-testid={`notification-${i}`}><span className="notification-icon"><Bell size={16} /></span><div><b>{title}</b><p>{desc}</p></div><small>{i + 1}h ago</small></button>)}</div></main></Layout>; }
function EditProfileModal({ user, open, onClose, onSave, testid = "edit-profile-modal" }) { const [form, setForm] = useState(user); const [newSkill, setNewSkill] = useState(""); const [status, setStatus] = useState(""); const update = (k, v) => setForm({ ...form, [k]: v }); const addSkill = () => { const s = newSkill.trim(); if (!s || form.skills.includes(s)) return; update("skills", [...form.skills, s]); setNewSkill(""); }; const removeSkill = (s) => update("skills", form.skills.filter(x => x !== s)); const saveAll = async () => { setStatus("saving"); save("skillbridge_user", form); const res = await syncApi("/users", { method: "POST", body: JSON.stringify(form) }); setStatus(res ? "saved" : "local"); onSave(form); setTimeout(() => { setStatus(""); onClose(); }, 900); }; return <Modal open={open} onClose={onClose} testid={testid} eyebrow="EDIT PROFILE" title="Update your signal"><div className="edit-profile-form"><Field label="Full name" value={form.name} onChange={v => update("name", v)} test="edit-name-input" placeholder="Your full name" /><Field label={form.role === "professional" ? "Professional title" : "College / university"} value={form.college} onChange={v => update("college", v)} test="edit-college-input" placeholder="Add a detail" /><Field label={form.role === "professional" ? "Experience" : "Degree / focus"} value={form.degree} onChange={v => update("degree", v)} test="edit-degree-input" placeholder="B.Tech Computer Science" /><Field label="Location" value={form.location} onChange={v => update("location", v)} test="edit-location-input" placeholder="City, country" /><Field label="Career goal" value={form.goal} onChange={v => update("goal", v)} test="edit-goal-input" placeholder="Software Engineer" /><div className="field"><span>Skills</span><div className="selected-chips">{form.skills.map(s => <span key={s}>{s}<button onClick={() => removeSkill(s)} data-testid={`edit-remove-skill-${s.toLowerCase().replaceAll("/", "-")}`}><X size={13} /></button></span>)}</div><div className="add-skill-row"><input value={newSkill} onChange={e => setNewSkill(e.target.value)} onKeyDown={e => e.key === "Enter" && (e.preventDefault(), addSkill())} placeholder="Add a skill" data-testid="edit-new-skill-input" /><button className="outline-btn" onClick={addSkill} data-testid="edit-add-skill-button">Add</button></div></div>{status === "saving" && <div className="success-note"><Clock3 size={15} /> Saving your changes…</div>}{status === "saved" && <div className="success-note" data-testid="edit-profile-saved"><Check size={15} /> Profile updated everywhere.</div>}{status === "local" && <div className="success-note"><Check size={15} /> Saved locally. We’ll re-sync when back online.</div>}<div className="modal-footer"><button className="ghost-btn" onClick={onClose} data-testid="edit-profile-cancel">Cancel</button><button className="primary-btn" onClick={saveAll} data-testid="edit-profile-save">Save changes<ArrowRight size={16} /></button></div></div></Modal>; }
function Profile() { const [user, setUser] = useState(read("skillbridge_user", demoUser)); const [editing, setEditing] = useState(false); const initials = user.name.split(" ").map(x => x[0]).slice(0, 2).join(""); return <Layout><main className="content profile-page"><section className="profile-header"><div className="profile-avatar">{initials}</div><div><span className="eyebrow">{user.role === "professional" ? "SKILLED PROFESSIONAL" : "STUDENT PROFILE"}</span><h1>{user.name}</h1><p>{user.goal} · {user.location}</p></div><button className="outline-btn" onClick={() => setEditing(true)} data-testid="edit-profile-button"><Settings size={15} /> Edit profile</button></section><div className="profile-grid"><section className="profile-section"><span className="eyebrow">ABOUT YOU</span><h2>Your signal</h2><div className="profile-facts"><span>{user.role === "professional" ? "Studio / affiliation" : "College / university"}<b>{user.college}</b></span><span>Focus<b>{user.degree}</b></span><span>Profile match<b>94%</b></span></div></section><section className="profile-section"><span className="eyebrow">SKILLS</span><h2>What you bring</h2><div className="detail-tags">{user.skills.map(s => <span key={s}>{s}</span>)}</div><button className="add-link" onClick={() => setEditing(true)} data-testid="add-skill-button">+ Add a skill</button></section></div><EditProfileModal user={user} open={editing} onClose={() => setEditing(false)} onSave={setUser} testid="edit-profile-modal" /></main></Layout>; }
function App() { return <BrowserRouter><Routes><Route path="/" element={read("skillbridge_user", null) ? <Navigate to="/home" replace /> : <Landing />} /><Route path="/student/login" element={<Auth role="student" />} /><Route path="/student/signup" element={<Auth role="student" />} /><Route path="/professional/login" element={<Auth role="professional" />} /><Route path="/professional/signup" element={<Auth role="professional" />} /><Route path="/onboarding" element={<Protected><Onboarding /></Protected>} /><Route path="/home" element={<Protected><Home /></Protected>} /><Route path="/dashboard" element={<Protected><Dashboard /></Protected>} /><Route path="/opportunities" element={<Protected><Opportunities /></Protected>} /><Route path="/opportunities/:id" element={<Protected><OpportunityDetail /></Protected>} /><Route path="/apply/:id" element={<Protected><ApplicationFlow /></Protected>} /><Route path="/applications" element={<Protected><Applications /></Protected>} /><Route path="/skill-match" element={<Protected><SkillMatch /></Protected>} /><Route path="/workspace" element={<Protected><Workspace /></Protected>} /><Route path="/notifications" element={<Protected><Notifications /></Protected>} /><Route path="/profile" element={<Protected><Profile /></Protected>} /><Route path="*" element={<Navigate to="/" replace />} /></Routes></BrowserRouter>; }
// Compatibility wrapper for the home-page JSX component reference.
function Oppo({ opportunity }) {
  return <OpportunityCard opportunity={opportunity} />;
}

export default App;
