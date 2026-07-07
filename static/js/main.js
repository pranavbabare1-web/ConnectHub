/* ── ConnectHub Main JS ── */

// ── Theme ──
const root = document.documentElement;
const saved = localStorage.getItem('theme') || 'dark';
root.dataset.theme = saved;

function toggleTheme() {
  const next = root.dataset.theme === 'dark' ? 'light' : 'dark';
  root.dataset.theme = next;
  localStorage.setItem('theme', next);
  document.querySelectorAll('.theme-toggle').forEach(btn => {
    btn.textContent = next === 'dark' ? '☀️' : '🌙';
  });
}

document.addEventListener('DOMContentLoaded', () => {
  // Set theme toggle icon
  document.querySelectorAll('.theme-toggle').forEach(btn => {
    btn.textContent = root.dataset.theme === 'dark' ? '☀️' : '🌙';
    btn.addEventListener('click', toggleTheme);
  });

  // ── Auto-dismiss messages ──
  const toasts = document.querySelectorAll('.message-toast');
  toasts.forEach(t => {
    setTimeout(() => fadeOut(t), 4000);
    t.addEventListener('click', () => fadeOut(t));
  });

  // ── Like buttons ──
  document.querySelectorAll('.like-btn').forEach(btn => {
    btn.addEventListener('click', handleLike);
  });

  // ── Comment toggles ──
  document.querySelectorAll('.comment-toggle-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const postId = btn.dataset.postId;
      const section = document.getElementById(`comments-${postId}`);
      section.classList.toggle('open');
    });
  });

  // ── Comment forms ──
  document.querySelectorAll('.comment-form').forEach(form => {
    form.addEventListener('submit', handleComment);
  });

  // ── Delete comment ──
  document.querySelectorAll('.comment-del').forEach(btn => {
    btn.addEventListener('click', handleDeleteComment);
  });

  // ── Follow buttons ──
  document.querySelectorAll('.follow-btn[data-username]').forEach(btn => {
    btn.addEventListener('click', handleFollow);
  });

  // ── Image preview in composer ──
  const imageInput = document.getElementById('id_image');
  if (imageInput) {
    imageInput.addEventListener('change', handleImagePreview);
  }

  // ── Char counter ──
  const textarea = document.querySelector('.post-textarea');
  if (textarea) {
    textarea.addEventListener('input', updateCharCount);
  }

  // ── Remove image preview ──
  const removeBtn = document.querySelector('.remove-image-btn');
  if (removeBtn) {
    removeBtn.addEventListener('click', () => {
      const wrap = document.querySelector('.image-preview-wrap');
      wrap.style.display = 'none';
      if (imageInput) imageInput.value = '';
    });
  }
});

// ── Helpers ──
function getCsrf() {
  return document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
         document.cookie.split('; ').find(r => r.startsWith('csrftoken='))?.split('=')[1] || '';
}

function fadeOut(el) {
  el.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
  el.style.opacity = '0';
  el.style.transform = 'translateX(20px)';
  setTimeout(() => el.remove(), 300);
}

function showToast(msg, type = 'success') {
  const container = document.querySelector('.messages-container') || (() => {
    const c = document.createElement('div');
    c.className = 'messages-container';
    document.body.appendChild(c);
    return c;
  })();
  const toast = document.createElement('div');
  toast.className = `message-toast ${type}`;
  toast.textContent = msg;
  container.appendChild(toast);
  setTimeout(() => fadeOut(toast), 4000);
  toast.addEventListener('click', () => fadeOut(toast));
}

// ── Like handler ──
async function handleLike(e) {
  const btn = e.currentTarget;
  const postId = btn.dataset.postId;
  const csrf = getCsrf();

  btn.disabled = true;
  try {
    const res = await fetch(`/post/${postId}/like/`, {
      method: 'POST',
      headers: { 'X-CSRFToken': csrf, 'Content-Type': 'application/json' },
    });
    const data = await res.json();
    const icon = btn.querySelector('.like-icon');
    const count = btn.querySelector('.like-count');
    if (data.liked) {
      btn.classList.add('liked');
      icon.textContent = '❤️';
      // Heart burst animation
      btn.style.transform = 'scale(1.15)';
      setTimeout(() => btn.style.transform = '', 200);
    } else {
      btn.classList.remove('liked');
      icon.textContent = '🤍';
    }
    count.textContent = data.count;
  } catch { showToast('Something went wrong.', 'error'); }
  btn.disabled = false;
}

// ── Comment handler ──
async function handleComment(e) {
  e.preventDefault();
  const form = e.currentTarget;
  const postId = form.dataset.postId;
  const input = form.querySelector('.comment-input');
  const text = input.value.trim();
  if (!text) return;

  const csrf = getCsrf();
  const formData = new FormData();
  formData.append('text', text);
  formData.append('csrfmiddlewaretoken', csrf);

  try {
    const res = await fetch(`/post/${postId}/comment/`, {
      method: 'POST',
      headers: { 'X-Requested-With': 'XMLHttpRequest' },
      body: formData,
    });
    const data = await res.json();
    if (data.success) {
      input.value = '';
      const section = document.getElementById(`comments-${postId}`);
      const formRow = section.querySelector('.comment-form-row');
      const commentHtml = `
        <div class="comment-item" id="comment-item-${data.comment_id}">
          <img src="${data.profile_image || '/static/images/default.png'}" alt="" class="comment-avatar">
          <div class="comment-body">
            <div class="comment-meta">
              <span class="comment-username">${data.username}</span>
              <span class="comment-time">${data.created_at}</span>
              <button class="comment-del" data-comment-id="${data.comment_id}" onclick="deleteCommentById(${data.comment_id}, ${postId}, this)">✕</button>
            </div>
            <p class="comment-text">${escapeHtml(data.text)}</p>
          </div>
        </div>`;
      formRow.insertAdjacentHTML('beforebegin', commentHtml);
      // Update count
      const countEl = document.querySelector(`.comment-toggle-btn[data-post-id="${postId}"] .comment-count`);
      if (countEl) countEl.textContent = data.count;
    }
  } catch { showToast('Could not post comment.', 'error'); }
}

// ── Delete comment ──
async function deleteCommentById(commentId, postId, btn) {
  const csrf = getCsrf();
  try {
    const res = await fetch(`/comment/${commentId}/delete/`, {
      method: 'POST',
      headers: { 'X-CSRFToken': csrf, 'X-Requested-With': 'XMLHttpRequest' },
    });
    const data = await res.json();
    if (data.success) {
      document.getElementById(`comment-item-${commentId}`)?.remove();
      const countEl = document.querySelector(`.comment-toggle-btn[data-post-id="${postId}"] .comment-count`);
      if (countEl) countEl.textContent = data.count;
    }
  } catch { showToast('Could not delete comment.', 'error'); }
}

async function handleDeleteComment(e) {
  const btn = e.currentTarget;
  const commentId = btn.dataset.commentId;
  const postId = btn.dataset.postId;
  await deleteCommentById(commentId, postId, btn);
}

// ── Follow handler ──
async function handleFollow(e) {
  const btn = e.currentTarget;
  const username = btn.dataset.username;
  const csrf = getCsrf();

  btn.disabled = true;
  try {
    const res = await fetch(`/follow/${username}/`, {
      method: 'POST',
      headers: { 'X-CSRFToken': csrf },
    });
    const data = await res.json();
    if (data.following) {
      btn.textContent = 'Following';
      btn.classList.add('following');
      showToast(`Now following @${username}!`);
    } else {
      btn.textContent = 'Follow';
      btn.classList.remove('following');
    }
    // Update follower count if on profile page
    const followerCount = document.querySelector('.follower-count-display');
    if (followerCount) followerCount.textContent = data.followers_count;
  } catch { showToast('Something went wrong.', 'error'); }
  btn.disabled = false;
}

// ── Image preview ──
function handleImagePreview(e) {
  const file = e.target.files[0];
  if (!file) return;
  const wrap = document.querySelector('.image-preview-wrap');
  const img = wrap.querySelector('img');
  const reader = new FileReader();
  reader.onload = ev => { img.src = ev.target.result; wrap.style.display = 'block'; };
  reader.readAsDataURL(file);
}

// ── Char counter ──
function updateCharCount() {
  const textarea = document.querySelector('.post-textarea');
  const counter = document.querySelector('.char-count');
  if (!counter) return;
  const len = textarea.value.length;
  const max = 2000;
  counter.textContent = `${len} / ${max}`;
  counter.style.color = len > max * 0.9 ? 'var(--coral)' : '';
}

// ── Escape HTML ──
function escapeHtml(str) {
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

// ── Mobile image attach ──
function triggerImageInput() {
  document.getElementById('id_image')?.click();
}
