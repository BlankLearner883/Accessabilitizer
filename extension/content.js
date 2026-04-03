(() => {
    function checkMarker() {
        for (const node of document.childNodes) {
            if (node.nodeType === Node.COMMENT_NODE) {
                const text = node.nodeValue.trim().toLowerCase();
                if (text.startsWith("enable accessabilitizer")) {
                    return true;
                }
            }

            // Stop once we hit <html>
            if (node.nodeType === Node.ELEMENT_NODE) {
                break;
            }
        }
        return false;
    }

    const enabled = checkMarker();

    console.log("Content script loaded");

    chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
        if (msg.type === "CHECK_ENABLED") {
            sendResponse({ enabled: checkMarker() });
            return true;
        }

        if (msg.type === "GET_URL") {
            sendResponse({ url: window.location.href });
            return true;
        }

        if (msg.type === "SWITCH_VERSION") {
            window.location.href = msg.url;
            return true;
        }
    });
})();