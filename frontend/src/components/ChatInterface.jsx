import React, { useState, useEffect, useRef } from 'react';
import apiClient, { getErrorMessage } from '../services/apiClient';

// `fill` chips put a template in the input for the user to finish instead of sending
const SUGGESTIONS = [
  { label: '🗂️ New list', text: 'Create a list called ', fill: true },
  { label: '➕ Add item', text: 'Add milk to ', fill: true },
  { label: '📋 Show lists', text: 'Show my lists' },
  { label: '↳ Sub-item', text: 'Add fruits in task 1', fill: true },
  { label: '✏️ Edit', text: 'Edit task 1 to ', fill: true },
  { label: '✅ Complete', text: 'Mark task 1 as done' },
  { label: '🗑️ Delete', text: 'Delete task ', fill: true },
  { label: '❓ Help', text: 'Help' }
];

const ChatInterface = ({ userId, userName, onTasksChanged }) => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }, [messages, isLoading]);

  const greeting = () => ({
    id: Date.now(),
    sender: 'ai',
    content: `Hi ${userName || 'there'}! I'm your task assistant. I can create lists and add, edit, complete, or delete the items in them. Try "Create a list called Groceries" or "Add milk, eggs to Groceries".`,
    timestamp: new Date().toISOString()
  });

  // Greet the user when the chat opens
  useEffect(() => {
    if (userId) {
      setMessages([greeting()]);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [userId]);

  const clearChat = () => setMessages([greeting()]);

  const applySuggestion = (suggestion) => {
    if (suggestion.fill) {
      setInputValue(suggestion.text);
      inputRef.current?.focus();
    } else {
      sendMessage(suggestion.text);
    }
  };

  const sendMessage = async (text) => {
    const message = text.trim();
    if (!message || isLoading) return;

    setMessages(prev => [...prev, {
      id: Date.now(),
      sender: 'user',
      content: message,
      timestamp: new Date().toISOString()
    }]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await apiClient.sendMessage(userId, message);

      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        sender: 'ai',
        content: response.response || 'I processed your request successfully.',
        timestamp: response.timestamp || new Date().toISOString()
      }]);

      // The agent may have changed tasks, so reload the real list
      onTasksChanged?.();
    } catch (error) {
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        sender: 'ai',
        isError: true,
        content: getErrorMessage(error),
        timestamp: new Date().toISOString()
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    sendMessage(inputValue);
  };

  return (
    <div className="panel chat-interface">
      <div className="panel-header chat-header">
        <div className="assistant-id">
          <span className="assistant-avatar">✦</span>
          <div>
            <h2>AI Assistant</h2>
            <p className="panel-sub"><span className="status-dot" /> Online</p>
          </div>
        </div>
        <button className="btn btn-ghost btn-sm" onClick={clearChat} disabled={isLoading || messages.length <= 1}>
          Clear chat
        </button>
      </div>

      <div className="chat-messages-container">
        <div className="chat-messages">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`message ${message.sender === 'user' ? 'user-message' : 'ai-message'} ${message.isError ? 'error-message' : ''}`}
            >
              <div className="message-content">{message.content}</div>
              <div className="message-timestamp">
                {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="message ai-message typing" aria-label="Assistant is typing">
              <span /><span /><span />
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      <div className="suggestions">
        {SUGGESTIONS.map(s => (
          <button
            key={s.label}
            className="suggestion-chip"
            onClick={() => applySuggestion(s)}
            disabled={isLoading}
            title={s.fill ? `Fill in: "${s.text}…"` : `Send: "${s.text}"`}
          >
            {s.label}
          </button>
        ))}
      </div>

      <form onSubmit={handleSubmit} className="chat-input-form">
        <input
          ref={inputRef}
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder="e.g. 'Create a list called Work' · 'Add milk to Groceries'"
          disabled={isLoading}
          className="input chat-input"
        />
        <button type="submit" disabled={isLoading || !inputValue.trim()} className="btn btn-primary send-button" aria-label="Send">
          ➤
        </button>
      </form>
    </div>
  );
};

export default ChatInterface;
