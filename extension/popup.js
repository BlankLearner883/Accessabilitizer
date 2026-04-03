async function getActiveTab() {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    return tab;
}

function sendToContent(type, payload = {}) {
    return new Promise((resolve, reject) => {
        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
            console.log("Tabs:", tabs);

            const tab = tabs[0];

            if (!tab || !tab.id) {
                reject(new Error("No active tab"));
                return;
            }

            console.log("Sending message to tab:", tab.id);

            chrome.tabs.sendMessage(tab.id, { type, ...payload }, (response) => {
                if (chrome.runtime.lastError) {
                    console.error("Runtime error:", chrome.runtime.lastError.message);
                    reject(chrome.runtime.lastError);
                } else {
                    console.log("Response:", response);
                    resolve(response);
                }
            });
        });
    });
}

function buildVersions(url) {
    try {
        const u = new URL(url);

        const path = u.pathname;

        const parts = path.split(".");
        if (parts.length < 2) return null;

        const ext = parts.pop();
        const base = parts.join(".");

        return {
            default: url,
            dyslexia: `${u.origin}${base}.dyslexia.${ext}`,
            "high-contrast": `${u.origin}${base}.contrast.${ext}`,
            "large-text": `${u.origin}${base}.large.${ext}`
        };
    } catch (e) {
        console.error("Invalid URL:", url, e);
        return null;
    }
}

function createButtons(versions) {
    const container = document.getElementById("controls");
    container.innerHTML = "";

    Object.entries(versions).forEach(([mode, url]) => {
        const btn = document.createElement("button");
        btn.textContent = mode;

        btn.addEventListener("click", async () => {
            await sendToContent("SWITCH_VERSION", { url });
        });

        container.appendChild(btn);
    });
}

document.addEventListener("DOMContentLoaded", async () => {
    const status = document.getElementById("status");
    const controls = document.getElementById("controls");

    try {
    const { enabled } = await sendToContent("CHECK_ENABLED");
    if (!enabled) {
        status.textContent = "Not supported on this site";
        return;
    }
    const { url } = await sendToContent("GET_URL");
    const versions = buildVersions(url);
    if (!versions) {
        status.textContent = "Unsupported file type";
        return;
    }
    createButtons(versions);
    status.style.display = "none";
    controls.style.display = "block";
} catch (err) {
    status.textContent = "Error";
    console.error(err);
}
});