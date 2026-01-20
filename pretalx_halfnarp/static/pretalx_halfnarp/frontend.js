document.addEventListener('DOMContentLoaded', function () {
    const submissionsContainers = document.querySelectorAll('.submissions');

    const csrfInput = document.querySelector("[name=csrfmiddlewaretoken]");
    const csrfToken = csrfInput ? csrfInput.value : '';

    const saveHandler = deduplicate(savePreferredTalks);

    submissionsContainers.forEach(container => {
        container.addEventListener('click', function (e) {
            // Ensure we don't trigger the favourite state if someone just
            // clicked the "more info" link
            if (e.target.closest('a')) {
                return;
            }

            const submissionEl = e.target.closest('.submission');

            if (submissionEl && container.contains(submissionEl)) {
                submissionEl.classList.toggle('preferred');
                saveHandler();
            }
        });
    });

    function savePreferredTalks() {
        const allSubmissions = document.querySelectorAll('.submissions .submission.preferred');

        const preferredTalkIds = Array.from(allSubmissions).map(function (el) {
            return parseInt(el.dataset.id, 10);
        });

        console.log('start save', 'preferredTalkIds=', preferredTalkIds);

        const cleanPath = window.location.pathname.replace(/\/?$/, '/');
        const url = window.location.origin + cleanPath + 'my-preferences/';

        return fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                preferred_submissions: preferredTalkIds
            })
        }).then(async response => {
            if (!response.ok) {
                const text = await response.text();
                throw new Error(`Server returned ${response.status}: ${text}`);
            }
        });
    }

    function deduplicate(action) {
        let actionInProgress = false;
        let actionPending = false;

        return async function applyActionOrSetFlag() {
            if (actionInProgress) {
                console.log('action still running, setting pending flag');
                actionPending = true;
                return;
            }

            actionInProgress = true;
            console.log('apply action');

            try {
                await action();
                console.log('action done');
                actionInProgress = false;

                if (actionPending) {
                    console.log('pending flag set, re-run action');
                    actionPending = false;
                    applyActionOrSetFlag();
                }
            } catch (error) {
                console.error('Save failed:', error);
                actionPending = false;
                actionInProgress = false;
            }
        };
    }
});
