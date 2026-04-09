(() => {
    // ── Marker check ────────────────────────────────────────────────────────
    function checkMarker() {
        for (const node of document.childNodes) {
            if (node.nodeType === Node.COMMENT_NODE) {
                const text = node.nodeValue.trim().toLowerCase();
                if (text.startsWith("enable accessabilitizer")) return true;
            }
            if (node.nodeType === Node.ELEMENT_NODE) break;
        }
        return false;
    }

    console.log("Content script loaded");

    // ── Flicker detection (NEW) ─────────────────────────────────────────────
    function detectFlickerMode() {
        return /_flicker[._]/.test(window.location.pathname);
    }

    let flickerEnabled = detectFlickerMode();

    // Hook for backend / GPU pipeline
    function applyFlickerReduction() {
        if (!flickerEnabled) return;

        console.log("Flicker Reduction mode active");

        // Placeholder:
        // This is where your backend-processed HTML or GPU pipeline can hook in.
        // Examples:
        // - adjust CSS filters
        // - stabilize canvas frames
        // - apply temporal smoothing to video elements

        document.body.style.willChange = "transform";
    }

    // ── Text-to-Speech ───────────────────────────────────────────────────────
    let currentUtterance = null;
    let ttsEnabled = true;

    function getPageText() {
        const body = document.body;
        if (!body) return "";
        const walker = document.createTreeWalker(body, NodeFilter.SHOW_TEXT, {
            acceptNode(node) {
                const parent = node.parentElement;
                if (!parent) return NodeFilter.FILTER_REJECT;
                const tag = parent.tagName.toLowerCase();
                if (["script", "style", "noscript", "head"].includes(tag))
                    return NodeFilter.FILTER_REJECT;

                const cs = window.getComputedStyle(parent);
                if (cs.display === "none" || cs.visibility === "hidden")
                    return NodeFilter.FILTER_REJECT;

                return NodeFilter.FILTER_ACCEPT;
            },
        });

        const chunks = [];
        let node;
        while ((node = walker.nextNode())) {
            const t = node.nodeValue.trim();
            if (t) chunks.push(t);
        }
        return chunks.join(" ");
    }

    function ttsStart() {
        if (!ttsEnabled) return;
        window.speechSynthesis.cancel();

        const text = getPageText();
        if (!text) return;

        currentUtterance = new SpeechSynthesisUtterance(text);
        currentUtterance.rate = 1;
        currentUtterance.pitch = 1;
        currentUtterance.onend = () => { currentUtterance = null; };

        window.speechSynthesis.speak(currentUtterance);
    }

    function ttsStop() {
        window.speechSynthesis.cancel();
        currentUtterance = null;
    }

    function ttsPause() {
        if (window.speechSynthesis.speaking && !window.speechSynthesis.paused)
            window.speechSynthesis.pause();
    }

    function ttsResume() {
        if (window.speechSynthesis.paused)
            window.speechSynthesis.resume();
    }

    function ttsStatus() {
        return {
            speaking: window.speechSynthesis.speaking,
            paused: window.speechSynthesis.paused,
            enabled: ttsEnabled,
        };
    }

    // ── Lifecycle fixes ──────────────────────────────────────────────────────
    window.addEventListener("pagehide", (e) => {
        if (e.persisted) ttsStop();
    });

    window.addEventListener("pageshow", (e) => {
        if (e.persisted && ttsEnabled) setTimeout(ttsStart, 300);
    });

    function onReady() {
        applyFlickerReduction(); // NEW

        if (ttsEnabled) ttsStart();
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", onReady);
    } else {
        setTimeout(onReady, 300);
    }

    // ── Message listener ─────────────────────────────────────────────────────
    chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
        switch (msg.type) {
            case "CHECK_ENABLED":
                sendResponse({ enabled: checkMarker() });
                break;

            case "GET_URL":
                sendResponse({ url: window.location.href });
                break;

            case "SWITCH_VERSION":
                window.location.href = msg.url;
                break;

            case "TTS_START":
                ttsStart();
                sendResponse({ ok: true });
                break;

            case "TTS_STOP":
                ttsStop();
                sendResponse({ ok: true });
                break;

            case "TTS_PAUSE":
                ttsPause();
                sendResponse({ ok: true });
                break;

            case "TTS_RESUME":
                ttsResume();
                sendResponse({ ok: true });
                break;

            case "TTS_STATUS":
                sendResponse(ttsStatus());
                break;

            case "TTS_SET_ENABLED":
                ttsEnabled = msg.enabled;
                if (!ttsEnabled) ttsStop();
                else ttsStart();
                sendResponse({ ok: true });
                break;

            case "GET_TTS_ENABLED":
                sendResponse({ enabled: ttsEnabled });
                break;
        }
    });
})();