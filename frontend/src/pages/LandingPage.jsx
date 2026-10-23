import React from 'react';

const FEATURES = [
  {
    icon: '💬',
    title: 'Just say it',
    text: 'Type "remind me to pay rent" and it becomes a task. No forms, no menus, no friction.'
  },
  {
    icon: '✏️',
    title: 'Edit & delete anywhere',
    text: 'Rename or remove tasks from your list in one click, or just ask: "edit task 2 to…".'
  },
  {
    icon: '🗂️',
    title: 'Lists for everything',
    text: 'Group items under titled lists like Groceries or Work. They update live as you chat.'
  },
  {
    icon: '🔒',
    title: 'Secure accounts',
    text: 'Sign in with your email. Passwords are hashed and your tasks stay private to you.'
  },
  {
    icon: '🌐',
    title: 'Speaks your language',
    text: 'Built to understand English and Urdu, so you can plan the way you think.'
  },
  {
    icon: '🧠',
    title: 'Powered by MCP tools',
    text: 'A structured tool layer means the assistant only ever does what you asked.'
  }
];

const STEPS = [
  { title: 'Create an account', text: 'Sign up with your name and email. It takes under a minute.' },
  { title: 'Chat or click', text: 'Tell the assistant what you need, or add tasks straight to your list.' },
  { title: 'Get it done', text: 'Edit, complete and clear tasks as your day moves along.' }
];

const BOARD_TASKS = [
  { text: 'Submit project report', done: true },
  { text: 'Book dentist appointment', done: true },
  { text: 'Buy groceries for the week', done: false, active: true },
  { text: 'Call mom after work', done: false },
  { text: 'Plan weekend trip', done: false }
];

const HeroBoard = () => {
  const today = new Date().toLocaleDateString(undefined, { weekday: 'long', month: 'short', day: 'numeric' });
  const done = BOARD_TASKS.filter(t => t.done).length;
  const pct = Math.round((done / BOARD_TASKS.length) * 100);

  return (
    <div className="hero-visual" aria-hidden="true">
      <div className="board">
        <div className="board-head">
          <div>
            <p className="board-label">Today's plan</p>
            <p className="board-date">{today}</p>
          </div>
          <span className="board-ring" style={{ '--p': pct }}><span>{pct}%</span></span>
        </div>

        <div className="board-progress"><span style={{ width: `${pct}%` }} /></div>

        <ul className="board-list">
          {BOARD_TASKS.map((t, i) => (
            <li key={t.text} className={`board-row ${t.done ? 'done' : ''} ${t.active ? 'active' : ''}`}>
              <span className="board-num">{i + 1}</span>
              <span className="board-check">{t.done ? '✓' : ''}</span>
              <span className="board-text">{t.text}</span>
              {t.active && (
                <span className="board-actions">
                  <span className="board-action">✎</span>
                  <span className="board-action danger">🗑</span>
                </span>
              )}
            </li>
          ))}
        </ul>

        <div className="board-input">
          <span>+ Add a task, or ask the assistant…</span>
        </div>
      </div>
    </div>
  );
};

const LandingPage = ({ onSignIn, onSignUp }) => {
  return (
    <div className="landing">
      <div className="landing-glow glow-1" aria-hidden="true" />
      <div className="landing-glow glow-2" aria-hidden="true" />

      <nav className="landing-nav">
        <div className="brand">
          <span className="brand-mark">✓</span>
          <span className="brand-name">TaskFlow AI</span>
        </div>
        <div className="nav-links">
          <a href="#features">Features</a>
          <a href="#how">How it works</a>
          <button className="nav-signin" onClick={onSignIn}>Sign in</button>
          <button className="btn btn-outline btn-sm" onClick={onSignUp}>Get started</button>
        </div>
      </nav>

      <header className="hero">
        <div className="hero-copy">
          <span className="eyebrow">
            <span className="pulse-dot" /> AI-powered task management
          </span>
          <h1>
            Your to-do list,<br />
            <span className="gradient-text">now a conversation.</span>
          </h1>
          <p className="hero-sub">
            TaskFlow AI turns plain language into organized tasks. Add, edit and
            check things off by chatting, or with a single click.
          </p>
          <div className="hero-ctas">
            <button className="btn btn-primary btn-lg" onClick={onSignUp}>
              Get started free <span aria-hidden="true">→</span>
            </button>
            <button className="btn btn-outline btn-lg" onClick={onSignIn}>
              Sign in
            </button>
          </div>
          <ul className="hero-points">
            <li>✓ Free to use</li>
            <li>✓ Secure sign-in</li>
            <li>✓ Works in seconds</li>
          </ul>
        </div>

        <HeroBoard />
      </header>

      <section id="features" className="landing-section">
        <div className="section-head">
          <span className="eyebrow plain">Features</span>
          <h2>Everything you need to stay on top of things</h2>
          <p>A focused toolkit that keeps you organized without slowing you down.</p>
        </div>
        <div className="feature-grid">
          {FEATURES.map((f) => (
            <article key={f.title} className="feature-card">
              <div className="feature-icon">{f.icon}</div>
              <h3>{f.title}</h3>
              <p>{f.text}</p>
            </article>
          ))}
        </div>
      </section>

      <section id="how" className="landing-section">
        <div className="section-head">
          <span className="eyebrow plain">How it works</span>
          <h2>From thought to done in three steps</h2>
        </div>
        <ol className="steps">
          {STEPS.map((s, i) => (
            <li key={s.title} className="step">
              <span className="step-num">{i + 1}</span>
              <h3>{s.title}</h3>
              <p>{s.text}</p>
            </li>
          ))}
        </ol>
      </section>

      <section className="cta-band">
        <h2>Ready to clear your head?</h2>
        <p>Create your free account and add your first task in under a minute.</p>
        <div className="hero-ctas center">
          <button className="btn btn-primary btn-lg" onClick={onSignUp}>
            Create free account <span aria-hidden="true">→</span>
          </button>
          <button className="btn btn-outline btn-lg" onClick={onSignIn}>
            I already have an account
          </button>
        </div>
      </section>

      <footer className="landing-footer">
        <div className="brand">
          <span className="brand-mark">✓</span>
          <span className="brand-name">TaskFlow AI</span>
        </div>
        <p>© {new Date().getFullYear()} TaskFlow AI. Built with FastAPI, React and MCP.</p>
      </footer>
    </div>
  );
};

export default LandingPage;
