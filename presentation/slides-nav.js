/**
 * Presentation slide order — update if files are renamed or reordered.
 */
(function () {
    var SLIDES = [
        'slide01_tytul.html',
        'slide02_scenariusz.html',
        'slide02b_zalozenia.html',
        'slide03_build_vs_buy.html',
        'slide04_wybor_stacku.html',
        'slide04b_powerapps_react.html',
        'slide05_architektura.html',
        'slide06_przeplyw.html',
        'slide07_erd.html',
        'slide08_normalizacja.html',
        'slide09_dfd.html',
        'slide10_sekwencja.html',
        'slide11_analityka.html',
        'slide12_bezpieczenstwo.html',
        'slide13_koszty.html',
        'slide14_kod.html',
        'slide15_kod_weryfikacyjny.html',
        'slide16_podsumowanie.html'
    ];

    var file = (window.location.pathname.split('/').pop() || '').split('?')[0] || '';
    if (!file || file === '') file = 'slide01_tytul.html';
    var index = SLIDES.indexOf(decodeURIComponent(file));
    if (index < 0) index = 0;

    function slideHref(filename) {
        try {
            return new URL(filename, window.location.href).href;
        } catch (e) {
            return filename;
        }
    }

    function go(delta) {
        var next = index + delta;
        if (next < 0 || next >= SLIDES.length) return;
        window.location.href = slideHref(SLIDES[next]);
    }

    var css =
        '.slides-nav-ui{position:fixed;z-index:9998;bottom:24px;left:50%;transform:translateX(-50%);display:flex;align-items:center;gap:10px;padding:8px 12px;border-radius:999px;background:rgba(22,29,51,0.85);border:1px solid rgba(255,255,255,0.12);box-shadow:0 8px 32px rgba(0,0,0,0.35);backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);font-family:system-ui,-apple-system,sans-serif;}' +
        '.slides-nav-ui button{-webkit-appearance:none;appearance:none;border:none;margin:0;cursor:pointer;display:inline-flex;align-items:center;justify-content:center;width:40px;height:40px;border-radius:10px;background:rgba(255,255,255,0.1);color:#f1f5f9;transition:background .15s ease,transform .15s ease;}' +
        '.slides-nav-ui button:hover:not(:disabled){background:rgba(126,186,66,0.28);}' +
        '.slides-nav-ui button:focus-visible{outline:2px solid #7eba42;outline-offset:2px;}' +
        '.slides-nav-ui button:disabled{opacity:0.35;cursor:not-allowed;}' +
        '.slides-nav-ui svg{display:block;}' +
        '.slides-nav-label{font-size:11px;font-weight:600;color:#9fb0c9;letter-spacing:0.06em;padding:0 6px;user-select:none;}';

    var style = document.createElement('style');
    style.textContent = css;
    document.head.appendChild(style);

    var prevSvg =
        '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 18l-6-6 6-6"/></svg>';
    var nextSvg =
        '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M9 18l6-6-6-6"/></svg>';

    var wrap = document.createElement('div');
    wrap.className = 'slides-nav-ui';
    wrap.setAttribute('role', 'navigation');
    wrap.setAttribute('aria-label', 'Nawigacja slajdów');

    var btnPrev = document.createElement('button');
    btnPrev.type = 'button';
    btnPrev.className = 'slides-nav-prev';
    btnPrev.setAttribute('aria-label', 'Poprzedni slajd');
    btnPrev.innerHTML = prevSvg;
    btnPrev.disabled = index === 0;

    var label = document.createElement('span');
    label.className = 'slides-nav-label';
    label.textContent = (index + 1) + ' / ' + SLIDES.length;

    var btnNext = document.createElement('button');
    btnNext.type = 'button';
    btnNext.className = 'slides-nav-next';
    btnNext.setAttribute('aria-label', 'Następny slajd');
    btnNext.innerHTML = nextSvg;
    btnNext.disabled = index === SLIDES.length - 1;

    btnPrev.addEventListener('click', function () { go(-1); });
    btnNext.addEventListener('click', function () { go(1); });

    wrap.appendChild(btnPrev);
    wrap.appendChild(label);
    wrap.appendChild(btnNext);
    document.body.appendChild(wrap);

    document.addEventListener('keydown', function (e) {
        if (e.key !== 'ArrowLeft' && e.key !== 'ArrowRight') return;
        var el = e.target;
        if (el && (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA' || el.tagName === 'SELECT' || (el.isContentEditable && el.isContentEditable === 'true'))) return;
        if (e.key === 'ArrowLeft') {
            if (index > 0) { e.preventDefault(); go(-1); }
        } else if (e.key === 'ArrowRight') {
            if (index < SLIDES.length - 1) { e.preventDefault(); go(1); }
        }
    });
})();
