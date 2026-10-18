const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:5000/api";

async function request(path, options = {}) {
  let response;

  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...options,
      headers: {
        ...(options.body ? { "Content-Type": "application/json" } : {}),
        ...options.headers,
      },
    });
  } catch {
    throw new Error(
      "Cannot connect to the DevTrack API. Check that your Flask backend is running.",
    );
  }

  if (!response.ok) {
    let message = `Request failed with status ${response.status}.`;

    try {
      const data = await response.json();
      if (data.error) message = data.error;
    } catch {
      // Keep the fallback message if the response isn't JSON.
    }

    throw new Error(message);
  }

  if (response.status === 204) {
    return null;
  }

  return response.json();
}

export const issueApi = {
  getAll() {
    return request("/issues");
  },

  getById(id) {
    return request(`/issues/${id}`);
  },

  create(issue) {
    return request("/issues", {
      method: "POST",
      body: JSON.stringify(issue),
    });
  },

  update(id, changes) {
    return request(`/issues/${id}`, {
      method: "PATCH",
      body: JSON.stringify(changes),
    });
  },

  delete(id) {
    return request(`/issues/${id}`, {
      method: "DELETE",
    });
  },

  checkSemanticDuplicates(issue, threshold = 0.65, excludeIssueId) {
    return request("/issues/check-semantic-duplicates", {
      method: "POST",
      body: JSON.stringify({
        title: issue.title,
        description: issue.description || "",
        threshold,
        ...(excludeIssueId != null
          ? { exclude_issue_id: excludeIssueId }
          : {}),
      }),
    });
  },
}; 