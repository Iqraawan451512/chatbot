import React, { useState, useEffect, useRef } from 'react';
import apiClient, { getErrorMessage } from '../services/apiClient';

const FILTERS = ['all', 'incomplete', 'completed'];

// Inline text editor shared by item and list-title editing
const InlineEditor = ({ initial, busy, onSave, onCancel, label, className = '' }) => {
  const [draft, setDraft] = useState(initial);
  const inputRef = useRef(null);

  useEffect(() => {
    inputRef.current?.select();
  }, []);

  const save = () => {
    const text = draft.trim();
    if (!text || text === initial) {
      onCancel();
      return;
    }
    onSave(text);
  };

  return (
    <span className={`inline-editor ${className}`}>
      <input
        ref={inputRef}
        value={draft}
        onChange={(e) => setDraft(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === 'Enter') save();
          if (e.key === 'Escape') onCancel();
        }}
        className="input todo-edit-input"
        aria-label={label}
        disabled={busy}
      />
      <button className="btn btn-primary btn-sm" onClick={save} disabled={busy || !draft.trim()}>Save</button>
      <button className="btn btn-ghost btn-sm" onClick={onCancel} disabled={busy}>Cancel</button>
    </span>
  );
};

const ConfirmDelete = ({ label, busy, onConfirm, onCancel }) => (
  <span className="confirm-delete">
    <span className="confirm-label">{label}</span>
    <button className="btn btn-danger btn-sm" onClick={onConfirm} disabled={busy}>Delete</button>
    <button className="btn btn-ghost btn-sm" onClick={onCancel} disabled={busy}>Keep</button>
  </span>
);

const TodoItem = ({ todo, number, busy, onToggle, onSave, onDelete, onAddSub, isSub = false }) => {
  const done = todo.status === 'completed';
  const [editing, setEditing] = useState(false);
  const [confirmingDelete, setConfirmingDelete] = useState(false);
  const subCount = todo.subtasks?.length || 0;

  if (editing) {
    return (
      <li className={`todo-item editing ${isSub ? 'sub-item' : ''}`}>
        <span className="todo-num">{number}</span>
        <InlineEditor
          initial={todo.description}
          busy={busy}
          label="Edit item"
          onCancel={() => setEditing(false)}
          onSave={async (text) => {
            if (await onSave(todo, text)) setEditing(false);
          }}
        />
      </li>
    );
  }

  return (
    <li className={`todo-item ${done ? 'completed' : ''} ${confirmingDelete ? 'confirming' : ''} ${isSub ? 'sub-item' : ''}`}>
      <span className="todo-num">{number}</span>
      <button
        className="todo-check"
        onClick={() => onToggle(todo)}
        disabled={busy}
        aria-label={done ? `Mark "${todo.description}" as not done` : `Mark "${todo.description}" as done`}
        title={done ? 'Mark as not done' : 'Mark as done'}
      >
        {done ? '✓' : ''}
      </button>
      <span className="todo-text" onDoubleClick={() => setEditing(true)} title="Double-click to edit">
        {todo.description}
      </span>

      {confirmingDelete ? (
        <ConfirmDelete
          label={subCount ? `Delete with ${subCount} sub-item(s)?` : 'Delete?'}
          busy={busy}
          onConfirm={() => onDelete(todo)}
          onCancel={() => setConfirmingDelete(false)}
        />
      ) : (
        <span className="todo-actions">
          {onAddSub && (
            <button className="icon-btn" onClick={() => onAddSub(todo)} disabled={busy} aria-label={`Add a sub-item under "${todo.description}"`} title="Add sub-item">
              ＋
            </button>
          )}
          <button className="icon-btn" onClick={() => setEditing(true)} disabled={busy} aria-label={`Edit "${todo.description}"`} title="Edit">
            ✎
          </button>
          <button
            className="icon-btn danger"
            onClick={() => setConfirmingDelete(true)}
            disabled={busy}
            aria-label={`Delete "${todo.description}"`}
            title="Delete"
          >
            🗑
          </button>
        </span>
      )}
    </li>
  );
};

const ListCard = ({ list, numberOf, filter, busy, run, userId }) => {
  const [collapsed, setCollapsed] = useState(false);
  const [editingTitle, setEditingTitle] = useState(false);
  const [confirmingDelete, setConfirmingDelete] = useState(false);
  const [newItem, setNewItem] = useState('');
  const [subParentId, setSubParentId] = useState(null);
  const [newSubItem, setNewSubItem] = useState('');

  const matches = (t) => filter === 'all' || t.status === filter;
  const subsOf = (t) => (t.subtasks || []).filter(matches);
  // Show an item if it, or any of its sub-items, matches the filter
  const visible = list.tasks.filter(t => matches(t) || subsOf(t).length > 0 || t.id === subParentId);
  const everything = list.tasks.flatMap(t => [t, ...(t.subtasks || [])]);
  const done = everything.filter(t => t.status === 'completed').length;

  const openSubForm = (todo) => {
    setNewSubItem('');
    setSubParentId(id => (id === todo.id ? null : todo.id));
  };

  const addSubItem = (e, parent) => {
    e.preventDefault();
    const text = newSubItem.trim();
    if (!text) return;
    run(async () => {
      await apiClient.addTask(userId, text, list.id, parent.id);
      setNewSubItem('');
      setSubParentId(null);
    });
  };

  const addItem = (e) => {
    e.preventDefault();
    const text = newItem.trim();
    if (!text) return;
    run(async () => {
      await apiClient.addTask(userId, text, list.id);
      setNewItem('');
    });
  };

  const toggleItem = (todo) => run(() =>
    apiClient.updateTask(userId, todo.id, {
      status: todo.status === 'completed' ? 'incomplete' : 'completed'
    })
  );

  return (
    <section className={`list-card ${confirmingDelete ? 'confirming' : ''}`}>
      <header className="list-card-head">
        {editingTitle ? (
          <InlineEditor
            initial={list.title}
            busy={busy}
            label="Edit list title"
            className="title-editor"
            onCancel={() => setEditingTitle(false)}
            onSave={async (title) => {
              if (await run(() => apiClient.renameList(userId, list.id, title))) setEditingTitle(false);
            }}
          />
        ) : (
          <>
            <button
              className="list-toggle"
              onClick={() => setCollapsed(c => !c)}
              aria-expanded={!collapsed}
              aria-label={collapsed ? `Expand ${list.title}` : `Collapse ${list.title}`}
            >
              <span className={`caret ${collapsed ? 'collapsed' : ''}`}>▾</span>
            </button>
            <h3 className="list-title" onDoubleClick={() => setEditingTitle(true)} title="Double-click to rename">
              {list.title}
            </h3>
            <span className="list-count">{done}/{everything.length}</span>

            {confirmingDelete ? (
              <ConfirmDelete
                label={everything.length ? `Delete list and ${everything.length} item(s)?` : 'Delete list?'}
                busy={busy}
                onConfirm={() => run(() => apiClient.deleteList(userId, list.id))}
                onCancel={() => setConfirmingDelete(false)}
              />
            ) : (
              <span className="list-actions">
                <button className="icon-btn" onClick={() => setEditingTitle(true)} disabled={busy} aria-label={`Rename ${list.title}`} title="Rename list">
                  ✎
                </button>
                <button className="icon-btn danger" onClick={() => setConfirmingDelete(true)} disabled={busy} aria-label={`Delete ${list.title}`} title="Delete list">
                  🗑
                </button>
              </span>
            )}
          </>
        )}
      </header>

      {!collapsed && (
        <div className="list-card-body">
          {visible.length > 0 ? (
            <ul className="list-items">
              {visible.map(todo => {
                const subs = subsOf(todo);
                const addingSub = subParentId === todo.id;
                const itemProps = {
                  busy,
                  onToggle: toggleItem,
                  onSave: (item, description) => run(() => apiClient.updateTask(userId, item.id, { description })),
                  onDelete: (item) => run(() => apiClient.deleteTask(userId, item.id))
                };
                return (
                  <React.Fragment key={todo.id}>
                    <TodoItem todo={todo} number={numberOf[todo.id]} onAddSub={openSubForm} {...itemProps} />
                    {(subs.length > 0 || addingSub) && (
                      <li className="sub-group">
                        <ul className="sub-items">
                          {subs.map(sub => (
                            <TodoItem key={sub.id} todo={sub} number={numberOf[sub.id]} isSub {...itemProps} />
                          ))}
                        </ul>
                        {addingSub && (
                          <form className="add-item-form sub-form" onSubmit={(e) => addSubItem(e, todo)}>
                            <input
                              type="text"
                              value={newSubItem}
                              onChange={(e) => setNewSubItem(e.target.value)}
                              onKeyDown={(e) => { if (e.key === 'Escape') setSubParentId(null); }}
                              placeholder={`Add a sub-item under "${todo.description}"…`}
                              className="input add-item-input"
                              disabled={busy}
                              autoFocus
                              aria-label={`Add a sub-item under ${todo.description}`}
                            />
                            <button type="submit" className="btn btn-ghost btn-sm" disabled={busy || !newSubItem.trim()}>+ Add</button>
                          </form>
                        )}
                      </li>
                    )}
                  </React.Fragment>
                );
              })}
            </ul>
          ) : (
            <p className="list-empty">
              {list.tasks.length === 0 ? 'No items yet.' : 'Nothing here for this filter.'}
            </p>
          )}

          <form className="add-item-form" onSubmit={addItem}>
            <input
              type="text"
              value={newItem}
              onChange={(e) => setNewItem(e.target.value)}
              placeholder={`Add an item to ${list.title}…`}
              className="input add-item-input"
              disabled={busy}
              aria-label={`Add an item to ${list.title}`}
            />
            <button type="submit" className="btn btn-ghost btn-sm" disabled={busy || !newItem.trim()}>+ Add</button>
          </form>
        </div>
      )}
    </section>
  );
};

const TodoList = ({ userId, lists, loading, error, onChanged }) => {
  const [newListTitle, setNewListTitle] = useState('');
  const [filter, setFilter] = useState('all');
  const [busy, setBusy] = useState(false);
  const [actionError, setActionError] = useState('');

  const topLevel = lists.flatMap(l => l.tasks);
  const allTasks = topLevel.flatMap(t => [t, ...(t.subtasks || [])]);
  const completedCount = allTasks.filter(t => t.status === 'completed').length;
  const progress = allTasks.length ? Math.round((completedCount / allTasks.length) * 100) : 0;

  // Number items 1, 2, 3… across all lists, sub-items 1.1, 1.2…, matching the chat
  const numberOf = {};
  topLevel.forEach((t, i) => {
    numberOf[t.id] = `${i + 1}`;
    (t.subtasks || []).forEach((sub, k) => { numberOf[sub.id] = `${i + 1}.${k + 1}`; });
  });

  // Run an API action, then reload the lists from the backend. Returns true on success.
  const run = async (action) => {
    setBusy(true);
    setActionError('');
    try {
      await action();
      await onChanged();
      return true;
    } catch (err) {
      setActionError(getErrorMessage(err));
      return false;
    } finally {
      setBusy(false);
    }
  };

  const createList = (e) => {
    e.preventDefault();
    const title = newListTitle.trim();
    if (!title) return;
    run(async () => {
      await apiClient.createList(userId, title);
      setNewListTitle('');
    });
  };

  const shownError = actionError || error;

  return (
    <div className="panel todo-list-component">
      <div className="panel-header">
        <div>
          <h2>My lists</h2>
          <p className="panel-sub">
            {lists.length} list{lists.length === 1 ? '' : 's'} · {completedCount} of {allTasks.length} items done
          </p>
        </div>
        <span className="progress-ring" style={{ '--p': progress }}>
          <span>{progress}%</span>
        </span>
      </div>

      <div className="progress-bar"><span style={{ width: `${progress}%` }} /></div>

      <form className="todo-input-area" onSubmit={createList}>
        <input
          type="text"
          value={newListTitle}
          onChange={(e) => setNewListTitle(e.target.value)}
          placeholder="New list title, e.g. Groceries"
          className="input"
          disabled={busy}
          maxLength={100}
          aria-label="New list title"
        />
        <button type="submit" className="btn btn-primary" disabled={busy || !newListTitle.trim()}>
          + New list
        </button>
      </form>

      <div className="filter-tabs" role="tablist">
        {FILTERS.map(f => (
          <button
            key={f}
            role="tab"
            aria-selected={filter === f}
            className={`filter-tab ${filter === f ? 'active' : ''}`}
            onClick={() => setFilter(f)}
          >
            {f === 'incomplete' ? 'Active' : f.charAt(0).toUpperCase() + f.slice(1)}
          </button>
        ))}
      </div>

      {shownError && <div className="alert">{shownError}</div>}

      <div className="todo-items">
        {loading && lists.length === 0 ? (
          <p className="empty-state">Loading your lists…</p>
        ) : lists.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">🗂️</div>
            <p>No lists yet. Create one above, or tell the assistant<br />"Create a list called Groceries".</p>
          </div>
        ) : (
          lists.map(list => (
            <ListCard
              key={list.id}
              list={list}
              numberOf={numberOf}
              filter={filter}
              busy={busy}
              run={run}
              userId={userId}
            />
          ))
        )}
      </div>

      {lists.length > 0 && (
        <p className="todo-hint">Tip: ＋ adds a sub-item, double-click anything to edit it. Numbers match the chat, e.g. "add fruits in task 1".</p>
      )}
    </div>
  );
};

export default TodoList;
