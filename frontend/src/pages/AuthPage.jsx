import React, { useState } from 'react';
import apiClient, { getErrorMessage } from '../services/apiClient';

const AuthPage = ({ mode, onModeChange, onAuthenticated, onBack, notice }) => {
  const isSignUp = mode === 'signup';
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const switchMode = (next) => {
    setError('');
    onModeChange(next);
  };

  const validate = () => {
    if (isSignUp && !name.trim()) return 'Please enter your name.';
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email.trim())) return 'Please enter a valid email address.';
    if (isSignUp && password.length < 8) return 'Password must be at least 8 characters.';
    if (!password) return 'Please enter your password.';
    return '';
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const problem = validate();
    if (problem) {
      setError(problem);
      return;
    }
    setSubmitting(true);
    setError('');
    try {
      const session = isSignUp
        ? await apiClient.signUp(name.trim(), email.trim(), password)
        : await apiClient.signIn(email.trim(), password);
      onAuthenticated(session);
    } catch (err) {
      setError(getErrorMessage(err));
      setSubmitting(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="landing-glow glow-1" aria-hidden="true" />
      <div className="landing-glow glow-2" aria-hidden="true" />

      <div className="auth-shell">
        <button className="auth-back" onClick={onBack}>← Back to home</button>

        <div className="auth-card">
          <div className="brand auth-brand">
            <span className="brand-mark">✓</span>
            <span className="brand-name">TaskFlow AI</span>
          </div>

          <h1>{isSignUp ? 'Create your account' : 'Welcome back'}</h1>
          <p className="auth-sub">
            {isSignUp ? 'Start organizing your tasks in seconds.' : 'Sign in to pick up where you left off.'}
          </p>

          <div className="auth-tabs" role="tablist">
            <button
              role="tab"
              aria-selected={!isSignUp}
              className={`auth-tab ${!isSignUp ? 'active' : ''}`}
              onClick={() => switchMode('signin')}
            >
              Sign in
            </button>
            <button
              role="tab"
              aria-selected={isSignUp}
              className={`auth-tab ${isSignUp ? 'active' : ''}`}
              onClick={() => switchMode('signup')}
            >
              Sign up
            </button>
          </div>

          {notice && !error && <div className="auth-notice">{notice}</div>}

          <form onSubmit={handleSubmit} className="auth-form" noValidate>
            {isSignUp && (
              <label className="field">
                <span>Full name</span>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Your full name"
                  autoComplete="name"
                  autoFocus
                />
              </label>
            )}

            <label className="field">
              <span>Email</span>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                autoComplete="email"
                autoFocus={!isSignUp}
              />
            </label>

            <label className="field">
              <span>Password</span>
              <div className="password-wrap">
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder={isSignUp ? 'At least 8 characters' : 'Your password'}
                  autoComplete={isSignUp ? 'new-password' : 'current-password'}
                />
                <button
                  type="button"
                  className="password-toggle"
                  onClick={() => setShowPassword(v => !v)}
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                >
                  {showPassword ? 'Hide' : 'Show'}
                </button>
              </div>
            </label>

            {error && <p className="form-error" role="alert">{error}</p>}

            <button type="submit" className="btn btn-primary btn-lg auth-submit" disabled={submitting}>
              {submitting ? 'Please wait…' : isSignUp ? 'Create account' : 'Sign in'}
            </button>
          </form>

          <p className="auth-switch">
            {isSignUp ? 'Already have an account? ' : "Don't have an account? "}
            <button className="link-btn" onClick={() => switchMode(isSignUp ? 'signin' : 'signup')}>
              {isSignUp ? 'Sign in' : 'Create one'}
            </button>
          </p>
        </div>
      </div>
    </div>
  );
};

export default AuthPage;
