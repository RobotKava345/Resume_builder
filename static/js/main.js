document.querySelectorAll('[data-template-mini-preview]').forEach((frame) => {
    const preview = frame.querySelector('iframe');
    if (!preview) return;

    const fitPreview = () => {
        const scale = Math.min(0.42, Math.max(0.2, (frame.clientWidth - 24) / 794));
        preview.style.left = `${(frame.clientWidth - 794 * scale) / 2}px`;
        preview.style.transform = `scale(${scale})`;
    };

    fitPreview();
    if ('ResizeObserver' in window) new ResizeObserver(fitPreview).observe(frame);
});

(() => {
    const modalElement = document.getElementById('workspaceModal');
    if (!modalElement || !window.bootstrap) return;

    const modal = bootstrap.Modal.getOrCreateInstance(modalElement);
    const modalTitle = document.getElementById('workspaceModalTitle');
    const modalBody = document.getElementById('workspaceModalBody');

    function displayForm(html, actionUrl) {
        const parsed = new DOMParser().parseFromString(html, 'text/html');
        const form = parsed.querySelector('main form');
        if (!form) return false;

        const heading = parsed.querySelector('main h1, main h2');
        modalTitle.textContent = heading?.textContent.trim() || 'Редагування';
        modalBody.replaceChildren();

        const description = [...parsed.querySelectorAll('main p')]
            .find((paragraph) => !paragraph.closest('form'));
        if (description) {
            const note = document.createElement('p');
            note.className = 'text-muted';
            note.textContent = description.textContent.trim();
            modalBody.append(note);
        }

        form.action = actionUrl;
        form.classList.add('workspace-modal-form');
        modalBody.append(form);

        form.querySelectorAll('a').forEach((link) => {
            if (/скасувати|cancel/i.test(link.textContent)) {
                link.href = '#';
                link.setAttribute('data-bs-dismiss', 'modal');
            }
        });
        return true;
    }

    document.addEventListener('click', async (event) => {
        const link = event.target.closest('a[data-modal-form]');
        if (!link) return;
        event.preventDefault();
        modalTitle.textContent = 'Завантаження…';
        modalBody.innerHTML = '<div class="text-center py-4"><div class="spinner-border" role="status"><span class="visually-hidden">Завантаження</span></div></div>';
        modal.show();

        try {
            const response = await fetch(link.href, {
                headers: { 'X-Requested-With': 'XMLHttpRequest' },
                credentials: 'same-origin',
            });
            if (response.redirected && !response.url.includes(link.pathname)) {
                window.location.assign(response.url);
                return;
            }
            const html = await response.text();
            if (!response.ok || !displayForm(html, link.href)) {
                throw new Error('Не вдалося завантажити форму.');
            }
        } catch (error) {
            modalTitle.textContent = 'Помилка';
            modalBody.textContent = error.message || 'Не вдалося завантажити форму.';
        }
    });

    modalBody.addEventListener('submit', async (event) => {
        const form = event.target.closest('form.workspace-modal-form');
        if (!form) return;
        event.preventDefault();
        const submitButton = form.querySelector('[type="submit"]');
        if (submitButton) submitButton.disabled = true;

        try {
            const response = await fetch(form.action, {
                method: form.method || 'POST',
                body: new FormData(form),
                headers: { 'X-Requested-With': 'XMLHttpRequest' },
                credentials: 'same-origin',
            });
            if (response.redirected) {
                window.location.assign(response.url);
                return;
            }
            const html = await response.text();
            if (!response.ok || !displayForm(html, form.action)) {
                throw new Error('Не вдалося зберегти зміни. Перевірте введені дані.');
            }
        } catch (error) {
            modalTitle.textContent = 'Помилка';
            modalBody.prepend(Object.assign(document.createElement('div'), {
                className: 'alert alert-danger',
                textContent: error.message || 'Не вдалося зберегти зміни.',
            }));
        }
    });
})();
