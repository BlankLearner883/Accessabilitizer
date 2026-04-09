const UNSUPPORTED_PREFIXES = ["chrome://", "edge://", "about:", "chrome-extension://"];

function isUnsupportedUrl(url) {
    return UNSUPPORTED_PREFIXES.some(p => (url || "").startsWith(p));
}

function sendToContent(type, payload = {}, isRetry = false) {
    return new Promise((resolve, reject) => {
        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
            const tab = tabs[0];
            if (!tab || !tab.id) { reject(new Error("No active tab")); return; }

            if (isUnsupportedUrl(tab.url)) {
                reject(new Error("Unsupported page"));
                return;
            }

            chrome.tabs.sendMessage(tab.id, { type, ...payload }, (response) => {
                const err = chrome.runtime.lastError;
                if (!err) { resolve(response); return; }

                const msg = err.message || "";
                if (!isRetry && msg.includes("Receiving end does not exist")) {
                    chrome.scripting.executeScript(
                        { target: { tabId: tab.id }, files: ["content.js"] },
                        () => {
                            if (chrome.runtime.lastError) {
                                reject(new Error(chrome.runtime.lastError.message));
                                return;
                            }
                            setTimeout(() => {
                                sendToContent(type, payload, true).then(resolve).catch(reject);
                            }, 150);
                        }
                    );
                } else {
                    reject(new Error(msg || "Unknown error"));
                }
            });
        });
    });
}

function getBaseUrl(pageUrl) {
    try {
        const u = new URL(pageUrl);
        let pathname = u.pathname;
        const dotIdx = pathname.lastIndexOf(".");
        if (dotIdx === -1) return pageUrl;

        const ext = pathname.slice(dotIdx + 1);
        let base = pathname.slice(0, dotIdx);

        base = base.replace(/_subtitled$/, "");
        base = base.replace(/_captioned$/, "");
        base = base.replace(/\.dyslexia$/, "");
        base = base.replace(/_flicker$/, "");

        return `${u.origin}${base}.${ext}`;
    } catch (_) {
        return pageUrl;
    }
}

function buildVersionUrl(pageUrl, features) {
    const baseUrl = getBaseUrl(pageUrl);
    try {
        const u = new URL(baseUrl);
        const pathname = u.pathname;
        const dotIdx = pathname.lastIndexOf(".");
        if (dotIdx === -1) return null;

        const base = pathname.slice(0, dotIdx);
        const ext = pathname.slice(dotIdx + 1);

        let newBase = base;

        if (features.dyslexia) newBase += ".dyslexia";
        if (features.captioned) newBase += "_captioned";
        if (features.subtitled) newBase += "_subtitled";
        if (features.flicker) newBase += "_flicker";

        if (
            !features.dyslexia &&
            !features.captioned &&
            !features.subtitled &&
            !features.flicker
        ) {
            return baseUrl;
        }

        return `${u.origin}${newBase}.${ext}`;
    } catch (_) {
        return null;
    }
}

function detectCurrentFeatures(pageUrl) {
    try {
        const pathname = new URL(pageUrl).pathname;
        return {
            dyslexia: /\.dyslexia[._]/.test(pathname) || /\.dyslexia$/.test(pathname),
            captioned: /_captioned[._]/.test(pathname) || /_captioned$/.test(pathname),
            subtitled: /_subtitled[._]/.test(pathname) || /_subtitled$/.test(pathname),
            flicker: /_flicker[._]/.test(pathname) || /_flicker$/.test(pathname)
        };
    } catch (_) {
        return { dyslexia: false, captioned: false, subtitled: false, flicker: false };
    }
}

async function urlExists(url) {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 3000);

    try {
        const res = await fetch(url, {
            method: "GET",
            signal: controller.signal
        });
        clearTimeout(timeout);
        return res.ok;
    } catch (e) {
        clearTimeout(timeout);
        return false;
    }
}

const btnTTS = document.getElementById("btn-tts");
const ttsIndicator = document.getElementById("tts-indicator");
const ttsStateText = document.getElementById("tts-state-text");

let ttsEnabled = true;

function applyTTSToggle(enabled) {
    if (!btnTTS || !ttsIndicator || !ttsStateText) return;

    ttsEnabled = enabled;
    btnTTS.classList.toggle("toggle--on", enabled);
    btnTTS.setAttribute("aria-checked", enabled);
    ttsIndicator.className = "dot " + (enabled ? "dot--active" : "dot--stopped");
    ttsStateText.textContent = enabled ? "Reading aloud" : "TTS off";
    sendToContent("TTS_SET_ENABLED", { enabled }).catch(() => {});
}

if (btnTTS) {
    btnTTS.addEventListener("click", () => {
        applyTTSToggle(!ttsEnabled);
    });
}

const toggleDyslexia = document.getElementById("toggle-dyslexia");
const toggleCaptioned = document.getElementById("toggle-captioned");
const toggleSubtitled = document.getElementById("toggle-subtitled");
const toggleFlicker = document.getElementById("toggle-flicker");

const versionStatus = document.getElementById("version-status");
const btnSwitch = document.getElementById("btn-switch");
const btnOriginal = document.getElementById("btn-original");

let currentPageUrl = "";
let currentFeatures = { dyslexia: false, captioned: false, subtitled: false, flicker: false };
let targetUrl = null;

function getActiveFeatures() {
    return {
        dyslexia: toggleDyslexia?.classList.contains("toggle--on"),
        captioned: toggleCaptioned?.classList.contains("toggle--on"),
        subtitled: toggleSubtitled?.classList.contains("toggle--on"),
        flicker: toggleFlicker?.classList.contains("toggle--on")
    };
}

function setFeatureToggle(el, on) {
    if (!el) return;
    el.classList.toggle("toggle--on", on);
    el.setAttribute("aria-checked", on);
}

async function checkTargetVersion() {
    if (!versionStatus || !btnSwitch) return;

    const features = getActiveFeatures();

    const allOff =
        !features.dyslexia &&
        !features.captioned &&
        !features.subtitled &&
        !features.flicker;

    const unchanged =
        features.dyslexia === currentFeatures.dyslexia &&
        features.captioned === currentFeatures.captioned &&
        features.subtitled === currentFeatures.subtitled &&
        features.flicker === currentFeatures.flicker;

    if (allOff || unchanged) {
        versionStatus.textContent = "Current version";
        versionStatus.className = "version-status version-status--current";
        btnSwitch.style.display = "none";
        targetUrl = null;
        return;
    }

    const candidate = buildVersionUrl(currentPageUrl, features);

    if (!candidate) {
        versionStatus.textContent = "Cannot build version URL";
        versionStatus.className = "version-status version-status--error";
        btnSwitch.style.display = "none";
        targetUrl = null;
        return;
    }

    versionStatus.textContent = "Checking...";
    btnSwitch.style.display = "none";

    const exists = await urlExists(candidate);

    if (exists) {
        versionStatus.textContent = "Version available";
        versionStatus.className = "version-status version-status--available";
        btnSwitch.style.display = "block";
        targetUrl = candidate;
    } else {
        versionStatus.textContent = "Version not found";
        versionStatus.className = "version-status version-status--missing";
        btnSwitch.style.display = "none";
        targetUrl = null;
    }
}

[toggleDyslexia, toggleCaptioned, toggleSubtitled, toggleFlicker].forEach(el => {
    if (!el) return;

    el.addEventListener("click", () => {
        el.classList.toggle("toggle--on");
        el.setAttribute("aria-checked", el.classList.contains("toggle--on"));
        checkTargetVersion();
    });
});

if (btnSwitch) {
    btnSwitch.addEventListener("click", () => {
        if (targetUrl) {
            sendToContent("SWITCH_VERSION", { url: targetUrl }).catch(() => {});
        }
    });
}

if (btnOriginal) {
    btnOriginal.addEventListener("click", () => {
        if (!currentPageUrl) return;

        const originalUrl = getBaseUrl(currentPageUrl);
        sendToContent("SWITCH_VERSION", { url: originalUrl }).catch(() => {});
    });
}

document.addEventListener("DOMContentLoaded", async () => {
    const status = document.getElementById("status");

    try {
        const { enabled } = await sendToContent("CHECK_ENABLED");

        if (!enabled) {
            status.textContent = "Accessibility versions not available on this page.";
            return;
        }

        status.style.display = "none";

        const { url } = await sendToContent("GET_URL");
        currentPageUrl = url;

        currentFeatures = detectCurrentFeatures(url);

        setFeatureToggle(toggleDyslexia, currentFeatures.dyslexia);
        setFeatureToggle(toggleCaptioned, currentFeatures.captioned);
        setFeatureToggle(toggleSubtitled, currentFeatures.subtitled);
        setFeatureToggle(toggleFlicker, currentFeatures.flicker);

        try {
            const { enabled: ttsOn } = await sendToContent("GET_TTS_ENABLED");
            applyTTSToggle(ttsOn);
        } catch (_) {
            applyTTSToggle(true);
        }

        if (btnOriginal) {
            const baseUrl = getBaseUrl(currentPageUrl);
            if (baseUrl === currentPageUrl) {
                btnOriginal.style.display = "none";
            }
        }

        await checkTargetVersion();

    } catch (err) {
        status.textContent = "Could not connect to page.";
        console.error(err.message);
    }
});
