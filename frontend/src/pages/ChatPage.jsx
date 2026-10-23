import React, { useState, useEffect, useCallback } from 'react';
import ChatInterface from '../components/ChatInterface';
import TodoList from '../components/TodoList';
import LandingPage from './LandingPage';
import AuthPage from './AuthPage';
import apiClient, {
  getErrorMessage,
  sessionStore,
  setAuthToken,
  setUnauthorizedHandler
} from '../services/apiClient';

const ChatPage = () => {
  const [session, setSession] = useState(sessionStore.load);
  // 'landing' | 'signin' | 'signup' (only used while signed out)
  // /#signin and /#signup open the auth screen directly
  const [view, setView] = useState(() => {
    const hash = window.location.hash.slice(1);
    return hash === 'signin' || hash === 'signup' ? hash : 'landing';
  });
  const [authNotice, setAuthNotice] = useState('');
  const [lists, setLists] = useState([]);
  const [tasksError, setTasksError] = useState('');
  const [tasksLoading, setTasksLoading] = useState(false);

  const user = session?.user;

  const handleAuthenticated = (newSession) => {
    sessionStore.save(newSession);
    setAuthToken(newSession.token);
    setAuthNotice('');
    setSession(newSession);
  };

  const signOut = useCallback((notice = '') => {
    sessionStore.clear();
    setAuthToken(null);
    setSession(null);
    setLists([]);
    setAuthNotice(notice);
    setView(notice ? 'signin' : 'landing');
  }, []);

  // Expired or invalid sessions send the user back to the sign-in screen
  useEffect(() => {
    setUnauthorizedHandler((message) => signOut(message));
    return () => setUnauthorizedHandler(null);
  }, [signOut]);

  // Re-validate a stored session once on load
  useEffect(() => {
    if (session) {
      apiClient.me().catch(() => {});
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Load the user's lists (with their items) from the backend
  const refreshTasks = useCallback(async () => {
    if (!user) return;
    setTasksLoading(true);
    try {
      const data = await apiClient.getLists(user.id);
      setLists(data.lists || []);
      setTasksError('');
    } catch (error) {
      setTasksError(getErrorMessage(error));
    } finally {
      setTasksLoading(false);
    }
  }, [user]);

  useEffect(() => {
    refreshTasks();
  }, [refreshTasks]);

  if (!user) {
    if (view === 'signin' || view === 'signup') {
      return (
        <AuthPage
          mode={view}
          onModeChange={setView}
          onAuthenticated={handleAuthenticated}
          onBack={() => { setAuthNotice(''); setView('landing'); }}
          notice={authNotice}
        />
      );
    }
    return <LandingPage onSignIn={() => setView('signin')} onSignUp={() => setView('signup')} />;
  }

  return (
    <div className="main-app-container">
      <header className="app-header">
        <div className="header-content">
          <div className="brand">
            <span className="brand-mark">✓</span>
            <span className="brand-name">TaskFlow AI</span>
          </div>
          <div className="user-controls">
            <span className="user-chip" title={user.email}>
              <span className="user-avatar">{(user.name || user.email).charAt(0).toUpperCase()}</span>
              {user.name || user.email}
            </span>
            <button onClick={() => signOut()} className="btn btn-ghost">Sign out</button>
          </div>
        </div>
      </header>

      <main className="app-content">
        <section className="todos-section">
          <TodoList
            userId={user.id}
            lists={lists}
            loading={tasksLoading}
            error={tasksError}
            onChanged={refreshTasks}
          />
        </section>

        <section className="chat-section">
          <ChatInterface userId={user.id} userName={user.name} onTasksChanged={refreshTasks} />
        </section>
      </main>

      <footer className="app-footer">
        <p>TaskFlow AI · Your conversations and tasks are stored securely</p>
      </footer>
    </div>
  );
};

export default ChatPage;
