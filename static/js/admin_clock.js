/**
 * Direct HH:MM Time Input & Formatter for Django Admin
 */
(function () {
    'use strict';

    function formatToHHMM(val) {
        if (!val) return '';
        val = val.trim();

        // If already HH:MM or HH:MM:SS
        const parts = val.split(':');
        if (parts.length >= 2) {
            let h = parseInt(parts[0], 10);
            let m = parseInt(parts[1], 10);
            if (!isNaN(h) && !isNaN(m)) {
                h = Math.min(Math.max(h, 0), 23);
                m = Math.min(Math.max(m, 0), 59);
                return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`;
            }
        }

        // Digits only e.g. "1430" or "930" or "9"
        const clean = val.replace(/\D/g, '');
        if (clean.length === 4) {
            let h = parseInt(clean.substring(0, 2), 10);
            let m = parseInt(clean.substring(2, 4), 10);
            h = Math.min(Math.max(h, 0), 23);
            m = Math.min(Math.max(m, 0), 59);
            return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`;
        } else if (clean.length === 3) {
            let h = parseInt(clean.substring(0, 1), 10);
            let m = parseInt(clean.substring(1, 3), 10);
            return `0${h}:${String(m).padStart(2, '0')}`;
        } else if (clean.length === 1 || clean.length === 2) {
            let h = parseInt(clean, 10);
            h = Math.min(Math.max(h, 0), 23);
            return `${String(h).padStart(2, '0')}:00`;
        }

        return val;
    }

    function getCurrentHHMM() {
        const now = new Date();
        const h = String(now.getHours()).padStart(2, '0');
        const m = String(now.getMinutes()).padStart(2, '0');
        return `${h}:${m}`;
    }

    function formatForDjango(hhmm) {
        if (!hhmm) return '';
        const parts = hhmm.split(':');
        if (parts.length === 2) {
            return `${parts[0]}:${parts[1]}:00`;
        }
        return hhmm;
    }

    function attachHHMMHandler(input) {
        if (input.dataset.hhmmAttached) return;
        input.dataset.hhmmAttached = 'true';

        // Set placeholder & hint
        input.placeholder = 'HH:MM (e.g. 14:30)';
        input.setAttribute('autocomplete', 'off');

        // Initial format check
        if (input.value) {
            const formatted = formatToHHMM(input.value);
            if (formatted) input.value = formatted;
        }

        // Live typing mask
        input.addEventListener('input', function (e) {
            let val = input.value;

            // Auto insert colon if 2 digits entered and no colon
            if (/^\d{2}$/.test(val) && e.inputType !== 'deleteContentBackward') {
                input.value = val + ':';
            }
        });

        // Format cleanly on blur
        input.addEventListener('blur', function () {
            if (input.value.trim() !== '') {
                const formatted = formatToHHMM(input.value);
                if (formatted) {
                    input.value = formatted;
                }
            }
        });

        // Quick Preset Chips Container
        const chipsContainer = document.createElement('span');
        chipsContainer.className = 'time-preset-chips';

        const presets = [
            { label: 'Now', time: 'now', class: 'chip-now' },
            { label: '09:00', time: '09:00' },
            { label: '12:00', time: '12:00' },
            { label: '14:30', time: '14:30' },
            { label: '17:00', time: '17:00' },
            { label: '20:00', time: '20:00' }
        ];

        presets.forEach(p => {
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.className = `time-chip-btn ${p.class || ''}`;
            btn.textContent = p.label;

            btn.addEventListener('click', function (e) {
                e.preventDefault();
                if (p.time === 'now') {
                    input.value = getCurrentHHMM();
                } else {
                    input.value = p.time;
                }
                input.dispatchEvent(new Event('input', { bubbles: true }));
                input.dispatchEvent(new Event('change', { bubbles: true }));
                input.focus();
            });

            chipsContainer.appendChild(btn);
        });

        // Insert chips right after the time input
        if (input.nextSibling) {
            input.parentNode.insertBefore(chipsContainer, input.nextSibling);
        } else {
            input.parentNode.appendChild(chipsContainer);
        }

        // Intercept form submit to ensure Django gets valid HH:MM:SS format
        const form = input.closest('form');
        if (form && !form.dataset.hhmmSubmitAttached) {
            form.dataset.hhmmSubmitAttached = 'true';
            form.addEventListener('submit', function () {
                const timeFields = form.querySelectorAll('input.vTimeField, input[type="time"], input[name$="_1"]');
                timeFields.forEach(f => {
                    if (f.value.trim() !== '') {
                        const formatted = formatToHHMM(f.value);
                        f.value = formatForDjango(formatted);
                    }
                });
            });
        }
    }

    function initHHMMTimeInputs() {
        const inputs = document.querySelectorAll('input.vTimeField, input[type="time"], input[name$="_1"]');
        inputs.forEach(attachHHMMHandler);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initHHMMTimeInputs);
    } else {
        initHHMMTimeInputs();
    }

    setInterval(initHHMMTimeInputs, 1500);
})();
