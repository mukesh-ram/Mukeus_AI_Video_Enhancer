window.MukeusHistory = {
    async loadHistory() {
        try {
            const res = await fetch("/api/history");
            if (!res.ok) return;

            const items = await res.json();
            this.renderHistoryTable(items);
        } catch (e) {
            console.warn("Could not load history:", e);
        }
    },

    renderHistoryTable(items) {
        const tbody = document.getElementById("historyTableBody");
        const emptyState = document.getElementById("emptyHistory");

        tbody.innerHTML = "";

        if (!items || items.length === 0) {
            emptyState.classList.remove("hidden");
            return;
        }

        emptyState.classList.add("hidden");

        items.forEach(item => {
            const tr = document.createElement("tr");

            tr.innerHTML = `
                <td><strong>${item.filename || 'Clip'}</strong></td>
                <td>${item.date || '--'}</td>
                <td>${item.resolution || '--'}</td>
                <td><span class="yellow-text">${item.enhancement_mode || 'NATURAL'}</span></td>
                <td>${item.processing_time || '--'}</td>
                <td>${item.filesize || '--'}</td>
                <td><span class="status-badge-completed">${item.status || 'Completed'}</span></td>
                <td>
                    ${item.output_filename ? `
                        <a href="/api/download/${encodeURIComponent(item.output_filename)}" download class="btn-text">Download</a>
                    ` : '--'}
                </td>
            `;

            tbody.appendChild(tr);
        });
    }
};

document.addEventListener("DOMContentLoaded", () => {
    // Clear History Button
    const clearBtn = document.getElementById("clearHistoryBtn");
    clearBtn.addEventListener("click", async () => {
        if (confirm("Are you sure you want to clear local enhancement history?")) {
            try {
                await fetch("/api/history", { method: "DELETE" });
                window.MukeusHistory.loadHistory();
            } catch (e) {
                console.warn(e);
            }
        }
    });

    // Settings Toggle Handlers
    const saveSettingsFunc = async () => {
        const autoDelete = document.getElementById("settingAutoDelete").checked;
        const preserveAudio = document.getElementById("settingPreserveAudio").checked;
        const openFolder = document.getElementById("settingOpenFolder").checked;

        try {
            await fetch("/api/settings", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    auto_delete_temp: autoDelete,
                    preserve_audio: preserveAudio,
                    open_output_folder: openFolder,
                    output_folder: ""
                })
            });
        } catch (e) {
            console.warn("Failed saving settings:", e);
        }
    };

    document.getElementById("settingAutoDelete").addEventListener("change", saveSettingsFunc);
    document.getElementById("settingPreserveAudio").addEventListener("change", saveSettingsFunc);
    document.getElementById("settingOpenFolder").addEventListener("change", saveSettingsFunc);

    // Settings Open Folder Button
    const settingsOpenBtn = document.getElementById("settingsOpenFolderBtn");
    if (settingsOpenBtn) {
        settingsOpenBtn.addEventListener("click", () => {
            fetch("/api/open-output-folder", { method: "POST" });
        });
    }
});
