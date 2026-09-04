document.addEventListener("DOMContentLoaded", () => {
    // Mode Card Click Handlers
    const modeCards = document.querySelectorAll(".mode-card");
    modeCards.forEach(card => {
        card.addEventListener("click", () => {
            modeCards.forEach(c => c.classList.remove("active"));
            card.classList.add("active");
            window.MukeusApp.selectedMode = card.getAttribute("data-mode");
        });
    });

    // Resolution Button Click Handlers
    const resBtns = document.querySelectorAll(".res-btn");
    resBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            resBtns.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            window.MukeusApp.selectedResolution = btn.getAttribute("data-res");
        });
    });

    // ENHANCE VIDEO Button Click Handler
    const enhanceBtn = document.getElementById("enhanceVideoBtn");
    enhanceBtn.addEventListener("click", async () => {
        const meta = window.MukeusApp.currentVideoMeta;
        if (!meta) {
            window.MukeusApp.showError("NO VIDEO SELECTED", "Please select a gaming video clip first.");
            return;
        }

        const autoDelete = document.getElementById("settingAutoDelete").checked;
        const preserveAudio = document.getElementById("settingPreserveAudio").checked;

        const payload = {
            job_id: meta.filename,
            mode: window.MukeusApp.selectedMode,
            resolution: window.MukeusApp.selectedResolution,
            preserve_audio: preserveAudio,
            auto_delete_temp: autoDelete
        };

        try {
            const res = await fetch("/api/enhance", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.detail || "Failed to trigger enhancement.");
            }

            const data = await res.json();
            window.MukeusApp.activeJobId = data.job_id;

            // Switch UI to Progress Workspace
            document.getElementById("enhancerWorkspace").classList.add("hidden");
            document.getElementById("progressWorkspace").classList.remove("hidden");

            // Start Job Progress Polling
            if (window.MukeusProgress) {
                window.MukeusProgress.startPolling(data.job_id);
            }

        } catch (e) {
            window.MukeusApp.showError("ENHANCEMENT ERROR", e.message);
        }
    });
});
