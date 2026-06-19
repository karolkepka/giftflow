/**
 * Sets --slide-scale so the 1280×720 slide fits the visible viewport.
 * Fixed UI on document.body should stay outside .slide-scale-inner.
 */
(function () {
    var BASE_W = 1280;
    var BASE_H = 720;
    var MAX_SCALE = 1;

    function readViewport() {
        var vv = window.visualViewport;
        if (vv && vv.width > 0 && vv.height > 0) {
            return { w: vv.width, h: vv.height };
        }
        return { w: window.innerWidth, h: window.innerHeight };
    }

    function sync() {
        var v = readViewport();
        var s = Math.min(v.w / BASE_W, v.h / BASE_H, MAX_SCALE);
        if (!isFinite(s) || s <= 0) {
            s = 1;
        }
        document.documentElement.style.setProperty('--slide-scale', String(s));
    }

    window.addEventListener('resize', sync);
    window.addEventListener('orientationchange', sync);
    if (window.visualViewport) {
        window.visualViewport.addEventListener('resize', sync);
        window.visualViewport.addEventListener('scroll', sync);
    }
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', sync);
    } else {
        sync();
    }
})();
