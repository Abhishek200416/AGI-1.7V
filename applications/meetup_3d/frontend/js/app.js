/**
 * NexusMeet 3D — Core Application Controller & REST API Integration.
 */

let meetupsData = [];

// Initialize application
document.addEventListener('DOMContentLoaded', () => {
  loadMeetupsAndStats();
  setupScrollTracking();
});

async function loadMeetupsAndStats() {
  try {
    const [meetupsRes, statsRes] = await Promise.all([
      fetch('/api/meetups'),
      fetch('/api/stats'),
    ]);

    const meetupsJson = await meetupsRes.json();
    const statsJson = await statsRes.json();

    if (meetupsJson.success && meetupsJson.events) {
      meetupsData = meetupsJson.events;
      renderMeetupSections(meetupsData);

      // Connect data to 3D Three.js Spatial Scene
      if (window.spatialScene) {
        window.spatialScene.addMeetupNodes(meetupsData);
      }
    }

    if (statsJson.success) {
      document.getElementById('stat-events').textContent = `${statsJson.total_events} EVENTS`;
      document.getElementById('stat-rsvps').textContent = `${statsJson.total_rsvps} RSVPS`;
    }
  } catch (err) {
    console.error('Failed loading meetups:', err);
    showToast('Failed connecting to REST API backend.', 'error');
  }
}

function renderMeetupSections(events) {
  const container = document.getElementById('dynamic-sections');
  container.innerHTML = '';

  events.forEach((evt, idx) => {
    const section = document.createElement('section');
    const alignClass = idx % 2 === 0 ? 'section-right' : 'section-left';
    section.className = `story-section ${alignClass}`;
    section.id = evt.event_id;
    section.setAttribute('data-step', idx + 1);

    const capPercent = Math.min(100, Math.round((evt.rsvp_count / evt.capacity) * 100));
    const isFull = evt.is_full;

    section.innerHTML = `
      <div class="glass-card" style="border-top: 3px solid ${evt.glow_color}">
        <span class="card-tag" style="color: ${evt.glow_color}">0${idx + 1} // ${evt.category}</span>
        <h2 class="event-title">${evt.title}</h2>
        <div class="event-subtitle">${evt.subtitle}</div>
        <p class="event-desc">${evt.description}</p>
        
        <div class="event-meta">
          <div class="meta-row">
            <span class="meta-icon">📅</span>
            <span>${evt.date_str} (${evt.time_str})</span>
          </div>
          <div class="meta-row">
            <span class="meta-icon">📍</span>
            <span>${evt.location}</span>
          </div>
        </div>

        <div class="capacity-container">
          <div class="capacity-label">
            <span>RSVP Capacity (${evt.rsvp_count} / ${evt.capacity})</span>
            <span>${capPercent}%</span>
          </div>
          <div class="capacity-track">
            <div class="capacity-fill" style="width: ${capPercent}%; background: ${evt.glow_color}"></div>
          </div>
        </div>

        <div class="tags-row">
          ${evt.tags.map(t => `<span class="tag-pill">#${t}</span>`).join('')}
        </div>

        <div class="card-action">
          <button class="btn btn-primary" onclick="openRSVPModal('${evt.event_id}')" ${isFull ? 'disabled' : ''}>
            ${isFull ? 'Event Full' : 'Reserve Spatial Pass →'}
          </button>
        </div>
      </div>
    `;
    container.appendChild(section);
  });
}

function setupScrollTracking() {
  const trackerBar = document.getElementById('tracker-bar');
  const trackerLabel = document.getElementById('tracker-label');

  window.addEventListener('scroll', () => {
    const sections = document.querySelectorAll('.story-section');
    const scrollPos = window.scrollY + window.innerHeight / 2;

    sections.forEach((sec, idx) => {
      const top = sec.offsetTop;
      const height = sec.offsetHeight;
      if (scrollPos >= top && scrollPos < top + height) {
        const total = sections.length;
        trackerLabel.textContent = `SECTION 0${idx + 1} / 0${total}`;
        const pct = ((idx + 1) / total) * 100;
        trackerBar.style.setProperty('--scroll-pct', `${pct}%`);
      }
    });
  });
}

function openRSVPModal(eventId) {
  const event = meetupsData.find(e => e.event_id === eventId);
  if (!event) return;

  document.getElementById('rsvp-event-id').value = event.event_id;
  document.getElementById('modal-category').textContent = event.category.toUpperCase();
  document.getElementById('modal-title').textContent = event.title;
  document.getElementById('modal-subtitle').textContent = `Date: ${event.date_str}`;
  document.getElementById('rsvp-modal').classList.add('active');
  document.getElementById('rsvp-name').focus();
}

function closeModal() {
  document.getElementById('rsvp-modal').classList.remove('active');
  document.getElementById('rsvp-form').reset();
}

async function submitRSVP() {
  const eventId = document.getElementById('rsvp-event-id').value;
  const name = document.getElementById('rsvp-name').value.trim();
  const email = document.getElementById('rsvp-email').value.trim();
  const submitBtn = document.getElementById('rsvp-submit-btn');

  if (!name || !email) {
    showToast('Please enter both name and email.', 'error');
    return;
  }

  submitBtn.disabled = true;
  submitBtn.textContent = 'Registering...';

  try {
    const res = await fetch(`/api/meetups/${eventId}/rsvp`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, email }),
    });

    const data = await res.json();
    if (res.ok && data.success) {
      showToast(data.message, 'success');
      closeModal();
      // Reload updated meetup state
      loadMeetupsAndStats();
    } else {
      showToast(data.error || 'Registration failed.', 'error');
    }
  } catch (err) {
    showToast('Network error during RSVP.', 'error');
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = 'Confirm RSVP';
  }
}

function showToast(message, type = 'success') {
  const container = document.getElementById('toast-container');
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = `
    <span>${type === 'success' ? '✅' : '⚠️'}</span>
    <div>${message}</div>
  `;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

// Close modal on backdrop click
document.getElementById('rsvp-modal').addEventListener('click', (e) => {
  if (e.target.id === 'rsvp-modal') closeModal();
});
document.getElementById('modal-close').addEventListener('click', closeModal);
