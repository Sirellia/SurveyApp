/* SurveyApp — main.js */

/* ── Тост-уведомление ─────────────────────────────────────── */
function showToast(msg, type = 'info') {
  const icons = { success: '✅', danger: '⚠️', info: 'ℹ️', warning: '⚡' };
  const t = document.createElement('div');
  t.className = 'toast';
  t.innerHTML = `<span>${icons[type] || 'ℹ️'}</span><span>${msg}</span>`;
  document.body.appendChild(t);
  setTimeout(() => t.remove(), 3200);
}

/* ── Копирование ссылки ───────────────────────────────────── */
function copyLink(text) {
  navigator.clipboard.writeText(text).then(() => {
    showToast('Ссылка скопирована!', 'success');
  }).catch(() => {
    const el = document.createElement('textarea');
    el.value = text;
    document.body.appendChild(el);
    el.select();
    document.execCommand('copy');
    el.remove();
    showToast('Ссылка скопирована!', 'success');
  });
}

/* ── Рейтинговые кнопки ───────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.rating-group').forEach(group => {
    const buttons = group.querySelectorAll('.rating-btn');
    const input   = group.querySelector('input[type="hidden"]');
    buttons.forEach(btn => {
      btn.addEventListener('click', () => {
        buttons.forEach(b => b.classList.remove('selected'));
        btn.classList.add('selected');
        if (input) input.value = btn.dataset.value;
      });
    });
  });

  /* ── Подтверждение удаления ───────────────────────────────── */
  document.querySelectorAll('[data-confirm]').forEach(el => {
    el.addEventListener('click', e => {
      if (!confirm(el.dataset.confirm)) e.preventDefault();
    });
  });

  /* ── Автоскрытие алертов (не ошибки) ─────────────────────── */
  document.querySelectorAll('.alert-success, .alert-info').forEach(a => {
    setTimeout(() => {
      a.style.transition = 'opacity 0.5s';
      a.style.opacity = '0';
      setTimeout(() => a.remove(), 500);
    }, 4000);
  });
});
