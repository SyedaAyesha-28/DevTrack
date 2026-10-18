
import { useEffect, useMemo, useState } from "react";
import { issueApi } from "./services/issueApi";
import "./App.css";

const statusLabels = {
  open: "Open",
  in_progress: "In Progress",
  resolved: "Resolved",
  closed: "Closed",
};

function formatDate(value) {
  if (!value) return "—";

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;

  return date.toLocaleDateString("en-US", {
    month: "short",
    day: "2-digit",
    year: "numeric",
  });
}

function App() {
  const [issues, setIssues] = useState([]);
  const [loading, setLoading] = useState(true);
  const [pageError, setPageError] = useState("");
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [priorityFilter, setPriorityFilter] = useState("all");
  const [showForm, setShowForm] = useState(false);
  const [saving, setSaving] = useState(false);
  const [updatingId, setUpdatingId] = useState(null);
  const [deletingId, setDeletingId] = useState(null);
  const [formError, setFormError] = useState("");
  const [duplicateLoading, setDuplicateLoading] = useState(false);
  const [duplicateResult, setDuplicateResult] = useState(null);
  const [form, setForm] = useState({
    title: "",
    description: "",
    priority: "medium",
  });

  async function loadIssues() {
    setLoading(true);
    setPageError("");

    try {
      const data = await issueApi.getAll();

      if (!Array.isArray(data)) {
        throw new Error("The API returned an unexpected issue list.");
      }

      setIssues(data);
    } catch (error) {
      setPageError(error.message || "Could not load issues.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadIssues();
  }, []);

  const filteredIssues = useMemo(() => {
    const query = search.trim().toLowerCase();

    return issues.filter((issue) => {
      const matchesSearch =
        !query ||
        issue.title?.toLowerCase().includes(query) ||
        issue.description?.toLowerCase().includes(query) ||
        String(issue.id).includes(query);

      const matchesStatus =
        statusFilter === "all" || issue.status === statusFilter;

      const matchesPriority =
        priorityFilter === "all" || issue.priority === priorityFilter;

      return matchesSearch && matchesStatus && matchesPriority;
    });
  }, [issues, search, statusFilter, priorityFilter]);

  const counts = {
    total: issues.length,
    open: issues.filter((issue) => issue.status === "open").length,
    progress: issues.filter((issue) => issue.status === "in_progress").length,
    resolved: issues.filter(
      (issue) =>
        issue.status === "resolved" || issue.status === "closed",
    ).length,
  };

  function openCreateForm() {
    setForm({ title: "", description: "", priority: "medium" });
    setFormError("");
    setDuplicateResult(null);
    setShowForm(true);
  }

  function closeCreateForm() {
    if (saving || duplicateLoading) return;
    setShowForm(false);
    setFormError("");
    setDuplicateResult(null);
  }

  async function checkDuplicates() {
    const title = form.title.trim();

    if (!title) {
      setFormError("Enter an issue title before checking duplicates.");
      return;
    }

    setDuplicateLoading(true);
    setFormError("");
    setDuplicateResult(null);

    try {
      const result = await issueApi.checkSemanticDuplicates(
        { title, description: form.description.trim() },
        0.65,
      );

      setDuplicateResult(result);
    } catch (error) {
      setFormError(
        `Duplicate check failed: ${error.message}. You can try again.`,
      );
    } finally {
      setDuplicateLoading(false);
    }
  }

  async function handleCreateIssue(event) {
    event.preventDefault();
    setFormError("");

    const title = form.title.trim();

    if (!title) {
      setFormError("Please enter an issue title.");
      return;
    }

    setSaving(true);

    try {
      const created = await issueApi.create({
        title,
        description: form.description.trim(),
        priority: form.priority,
        status: "open",
      });

      setIssues((current) => [created, ...current]);
      setShowForm(false);
      setForm({ title: "", description: "", priority: "medium" });
      setDuplicateResult(null);
    } catch (error) {
      setFormError(error.message || "Could not create the issue.");
    } finally {
      setSaving(false);
    }
  }

  async function updateStatus(issueId, nextStatus) {
    const currentIssue = issues.find((issue) => issue.id === issueId);
    if (!currentIssue || currentIssue.status === nextStatus) return;

    setUpdatingId(issueId);
    setPageError("");

    try {
      const updated = await issueApi.update(issueId, {
        status: nextStatus,
      });

      setIssues((current) =>
        current.map((issue) => (issue.id === issueId ? updated : issue)),
      );
    } catch (error) {
      setPageError(`Could not update issue #${issueId}: ${error.message}`);
    } finally {
      setUpdatingId(null);
    }
  }

  async function deleteIssue(issue) {
    const confirmed = window.confirm(
      `Delete issue #${issue.id}: "${issue.title}"? This cannot be undone.`,
    );

    if (!confirmed) return;

    setDeletingId(issue.id);
    setPageError("");

    try {
      await issueApi.delete(issue.id);
      setIssues((current) =>
        current.filter((item) => item.id !== issue.id),
      );
    } catch (error) {
      setPageError(`Could not delete issue #${issue.id}: ${error.message}`);
    } finally {
      setDeletingId(null);
    }
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <a className="brand" href="#dashboard" aria-label="DevTrack home">
          <span className="brand-mark">D</span>
          <span>devtrack<span className="brand-dot">.</span></span>
        </a>

        <div className="workspace-label">WORKSPACE</div>
        <div className="workspace-switcher">
          <span className="workspace-avatar">D</span>
          <span className="workspace-name">
            <strong>DevTrack Team</strong>
            <small>Development workspace</small>
          </span>
          <span className="switcher-arrow">⌄</span>
        </div>

        <div className="nav-label">GENERAL</div>
        <nav className="navigation" aria-label="Main navigation">
          <a className="nav-item active" href="#dashboard">
            <span className="nav-icon">▦</span> Overview
          </a>
          <a className="nav-item" href="#issues">
            <span className="nav-icon">☷</span> All issues
            <span className="nav-count">{issues.length}</span>
          </a>
          <a className="nav-item" href="#duplicate-detection">
            <span className="nav-icon">◎</span> Duplicate detection
            <span className="nav-tag">AI</span>
          </a>
        </nav>

        <div className="sidebar-bottom">
          <div className="help-card">
            <span className="help-icon">✳</span>
            <strong>Built for better bug tracking</strong>
            <p>Find issues, organize work, and reduce duplicate reports.</p>
          </div>
          <div className="profile">
            <div className="profile-avatar">A</div>
            <div className="profile-details">
              <strong>DevTrack Admin</strong>
              <small>Project workspace</small>
            </div>
            <span className="profile-menu">···</span>
          </div>
        </div>
      </aside>

      <main className="main-content" id="dashboard">
        <header className="topbar">
          <div className="breadcrumbs">
            Workspace <span>/</span> <strong>Overview</strong>
          </div>
          <div className="topbar-right">
            <span className="environment">
              <span className="connection-dot" />
              Live API
            </span>
            <button className="avatar-button" type="button" aria-label="Profile">
              A
            </button>
          </div>
        </header>

        <section className="page-content">
          <div className="page-heading">
            <div>
              <div className="eyebrow">PROJECT WORKSPACE</div>
              <h1>Issue overview</h1>
              <p className="page-subtitle">
                Track bugs, manage priorities, and keep development moving.
              </p>
            </div>
            <button className="primary-button" onClick={openCreateForm}>
              <span>＋</span> New issue
            </button>
          </div>

          {pageError && (
            <div className="error-banner" role="alert">
              <span>{pageError}</span>
              <button type="button" onClick={loadIssues}>Retry loading</button>
            </div>
          )}

          <section className="stats-grid" aria-label="Issue summary">
            <StatCard label="Total issues" value={counts.total}
              detail="Across this workspace" icon="☷" tone="purple" />
            <StatCard label="Open issues" value={counts.open}
              detail="Waiting to be picked up" icon="◷" tone="orange" />
            <StatCard label="In progress" value={counts.progress}
              detail="Currently being worked on" icon="↗" tone="blue" />
            <StatCard label="Resolved / closed" value={counts.resolved}
              detail="Completed issues" icon="✓" tone="green" />
          </section>

          <section className="issues-panel" id="issues">
            <div className="panel-heading">
              <div>
                <h2>
                  All issues <span className="subtle-count">{issues.length}</span>
                </h2>
                <p>Review and manage reported issues.</p>
              </div>
              <span className="demo-label">
                <span className="connection-dot" /> MySQL data
              </span>
            </div>

            <div className="filters">
              <label className="search-box">
                <span aria-hidden="true">⌕</span>
                <input
                  type="search"
                  placeholder="Search issues by title, description or ID..."
                  value={search}
                  onChange={(event) => setSearch(event.target.value)}
                  aria-label="Search issues"
                />
                {search && (
                  <button type="button" className="clear-search"
                    onClick={() => setSearch("")} aria-label="Clear search">
                    ×
                  </button>
                )}
              </label>

              <label className="filter-control">
                <span className="filter-caption">Status</span>
                <select value={statusFilter}
                  onChange={(event) => setStatusFilter(event.target.value)}
                  aria-label="Filter by status">
                  <option value="all">All statuses</option>
                  <option value="open">Open</option>
                  <option value="in_progress">In progress</option>
                  <option value="resolved">Resolved</option>
                  <option value="closed">Closed</option>
                </select>
              </label>

              <label className="filter-control">
                <span className="filter-caption">Priority</span>
                <select value={priorityFilter}
                  onChange={(event) => setPriorityFilter(event.target.value)}
                  aria-label="Filter by priority">
                  <option value="all">All priorities</option>
                  <option value="critical">Critical</option>
                  <option value="high">High</option>
                  <option value="medium">Medium</option>
                  <option value="low">Low</option>
                </select>
              </label>
            </div>

            <div className="table-scroll">
              <table className="issues-table">
                <thead>
                  <tr>
                    <th>ISSUE</th>
                    <th>STATUS</th>
                    <th>PRIORITY</th>
                    <th>CREATED</th>
                    <th>UPDATE STATUS</th>
                    <th>ACTIONS</th>
                  </tr>
                </thead>
                <tbody>
                  {loading ? (
                    <tr>
                      <td colSpan="6">
                        <div className="empty-state">
                          <strong>Loading issues...</strong>
                          <p>Fetching records from the DevTrack API.</p>
                        </div>
                      </td>
                    </tr>
                  ) : filteredIssues.map((issue) => (
                    <tr key={issue.id}>
                      <td>
                        <div className="issue-title-cell">
                          <span className="issue-id">#{issue.id}</span>
                          <div className="issue-copy">
                            <strong>{issue.title}</strong>
                            <span>{issue.description || "No description provided."}</span>
                          </div>
                        </div>
                      </td>
                      <td>
                        <span className={`status-badge status-${issue.status}`}>
                          <span className="status-dot" />
                          {statusLabels[issue.status] || issue.status}
                        </span>
                      </td>
                      <td>
                        <span className={`priority priority-${issue.priority}`}>
                          <span className="priority-symbol">
                            {issue.priority === "critical" ? "‼"
                              : issue.priority === "high" ? "↑"
                              : issue.priority === "medium" ? "↗" : "↓"}
                          </span>
                          {issue.priority?.charAt(0).toUpperCase() +
                            issue.priority?.slice(1)}
                        </span>
                      </td>
                      <td className="date-cell">{formatDate(issue.created_at)}</td>
                      <td>
                        <label className="sr-only" htmlFor={`status-${issue.id}`}>
                          Update status for {issue.title}
                        </label>
                        <select id={`status-${issue.id}`}
                          className="row-status-select"
                          value={issue.status}
                          disabled={updatingId === issue.id}
                          onChange={(event) =>
                            updateStatus(issue.id, event.target.value)
                          }>
                          <option value="open">Open</option>
                          <option value="in_progress">In progress</option>
                          <option value="resolved">Resolved</option>
                          <option value="closed">Closed</option>
                        </select>
                      </td>
                      <td>
                        <button
                          className="delete-button"
                          type="button"
                          disabled={deletingId === issue.id}
                          onClick={() => deleteIssue(issue)}
                        >
                          {deletingId === issue.id ? "Deleting..." : "Delete"}
                        </button>
                      </td>
                    </tr>
                  ))}

                  {!loading && filteredIssues.length === 0 && (
                    <tr>
                      <td colSpan="6">
                        <div className="empty-state">
                          <span>⌕</span>
                          <strong>No matching issues</strong>
                          <p>Try a different search term or change your filters.</p>
                          <button type="button" className="text-button"
                            onClick={() => {
                              setSearch("");
                              setStatusFilter("all");
                              setPriorityFilter("all");
                            }}>
                            Clear filters
                          </button>
                        </div>
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>

            <div className="table-footer">
              <span>
                Showing <strong>{loading ? 0 : filteredIssues.length}</strong> of{" "}
                <strong>{issues.length}</strong> issues
              </span>
              <span>DevTrack workspace</span>
            </div>
          </section>

          <section className="duplicate-banner" id="duplicate-detection">
            <div className="duplicate-icon">✳</div>
            <div className="duplicate-text">
              <strong>Catch duplicate issues before they pile up</strong>
              <p>
                Check whether a new report describes an issue already in your
                database using semantic similarity.
              </p>
            </div>
            <span className="coming-soon">Semantic API enabled</span>
          </section>

          <footer className="page-footer">
            <span>DevTrack · Issue management workspace</span>
            <span>React · Flask · MySQL</span>
          </footer>
        </section>
      </main>

      {showForm && (
        <div className="modal-backdrop" onMouseDown={(event) => {
          if (event.target === event.currentTarget) closeCreateForm();
        }}>
          <section className="issue-modal" role="dialog" aria-modal="true"
            aria-labelledby="new-issue-title">
            <div className="modal-heading">
              <div>
                <div className="eyebrow">ISSUE MANAGEMENT</div>
                <h2 id="new-issue-title">Create an issue</h2>
                <p>This issue will be saved to your MySQL database.</p>
              </div>
              <button type="button" className="modal-close"
                onClick={closeCreateForm} aria-label="Close dialog">×</button>
            </div>

            <form onSubmit={handleCreateIssue}>
              <label className="form-field">
                <span>Issue title <b>*</b></span>
                <input autoFocus maxLength={200} required
                  value={form.title}
                  onChange={(event) => {
                    setForm((current) => ({ ...current, title: event.target.value }));
                    setDuplicateResult(null);
                  }}
                  placeholder="e.g. Login page returns a 500 error" />
              </label>

              <label className="form-field">
                <span>Description</span>
                <textarea rows={4} value={form.description}
                  onChange={(event) => {
                    setForm((current) => ({ ...current, description: event.target.value }));
                    setDuplicateResult(null);
                  }}
                  placeholder="Describe what happened and how to reproduce it..." />
              </label>

              <label className="form-field">
                <span>Priority</span>
                <select value={form.priority}
                  onChange={(event) =>
                    setForm((current) => ({ ...current, priority: event.target.value }))
                  }>
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="critical">Critical</option>
                </select>
              </label>

              <button className="secondary-button duplicate-check-button"
                type="button" disabled={duplicateLoading || saving}
                onClick={checkDuplicates}>
                {duplicateLoading ? "Checking for similar issues..." : "Check for duplicates"}
              </button>

              {duplicateResult && (
                <div className="duplicate-results" role="status">
                  {duplicateResult.count > 0 ? (
                    <>
                      <strong>
                        Found {duplicateResult.count} possible duplicate
                        {duplicateResult.count === 1 ? "" : "s"}
                      </strong>
                      <p>Review these matches before creating your issue.</p>
                      {duplicateResult.matches.map((match,) => (
                        <div className="duplicate-match" key={match.issue.id}>
                          <div className="duplicate-match-details">
                      <strong>
                        #{match.issue.id} {match.issue.title}
                      </strong>
                       <div className="duplicate-match-meta">
        <span>Status: {match.issue.status.replace("_", " ")}</span>
        <span>Priority: {match.issue.priority}</span>
      </div>
      </div>
    
  <span className="similarity-score" >
    {(match.similarity*100).toFixed(1)}% similarity
  </span>
</div>
                      ))}
                    </>
                  ) : (
                    <p>No possible duplicates were found at the selected threshold.</p>
                  )}
                </div>
              )}

              {formError && <p className="form-error" role="alert">{formError}</p>}

              <div className="modal-actions">
                <button type="button" className="secondary-button"
                  onClick={closeCreateForm} disabled={saving || duplicateLoading}>
                  Cancel
                </button>
                <button type="submit" className="primary-button"
                  disabled={saving || duplicateLoading}>
                  {saving ? "Saving..." : "Create issue"}
                </button>
              </div>
              <p className="form-note">
                Creating an issue writes it to the database. Checking duplicates
                does not create or modify any records.
              </p>
            </form>
          </section>
        </div>
      )}
    </div>
  );
}

function StatCard({ label, value, detail, icon, tone }) {
  return (
    <article className="stat-card">
      <div className="stat-top">
        <span className="stat-label">{label}</span>
        <span className={`stat-icon stat-icon-${tone}`}>{icon}</span>
      </div>
      <div className="stat-value">{value}</div>
      <div className="stat-detail">{detail}</div>
    </article>
  );
}

export default App;
