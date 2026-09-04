window.MukeusProgress = {
    pollTimer: null,

    startPolling(jobId) {
        if (this.pollTimer) clearInterval(this.pollTimer);
        
        this.pollStatus(jobId);
        this.pollTimer = setInterval(() => {
            this.pollStatus(jobId);
        }, 1000);
    },

    stopPolling() {
        if (this.pollTimer) {
            clearInterval(this.pollTimer);
            this.pollTimer = null;
        }
    },

    async pollStatus(jobId) {
        try {
            const res = await fetch(`/api/status/${jobId}`);
            if (!res.ok) return;

            const status = await res.json();
            this.updateProgressUI(status);

            if (status.status === "COMPLETED") {
                this.stopPolling();
                this.onJobCompleted(status);
            } else if (status.status === "FAILED") {
                this.stopPolling();
                this.onJobFailed(status);
            } else if (status.status === "CANCELLED") {
                this.stopPolling();
                this.onJobCancelled();
            }

        } catch (e) {
            console.warn("Status polling error:", e);
        }
    },

    updateProgressUI(status) {
        // Progress bar percentage
        const pct = Math.min(100, Math.max(0, status.progress || 0));
        document.getElementById("progressBarFill").style.width = `${pct}%`;
        document.getElementById("progressPctText").innerText = `${Math.round(pct)}%`;

        // Current Operation Text
        document.getElementById("progressDetailText").innerText = status.message || "Processing video...";

        // Stage Title
        if (status.stage === "AI_ENHANCEMENT" && status.total_frames > 0) {
            document.getElementById("progressStageTitle").innerText = `AI ENHANCING FRAMES (${status.current_frame} / ${status.total_frames})`;
        } else {
            document.getElementById("progressStageTitle").innerText = `PROCESSING: ${status.stage.replace('_', ' ')}`;
        }

        // Highlight active step item
        this.updateStepHighlight(status.stage);
    },

    updateStepHighlight(stage) {
        const steps = [
            { id: "stepAnalyzing", stages: ["ANALYZING"] },
            { id: "stepPreparing", stages: ["PREPARING"] },
            { id: "stepExtracting", stages: ["EXTRACTING"] },
            { id: "stepAi", stages: ["AI_ENHANCEMENT"] },
            { id: "stepEncoding", stages: ["ENCODING"] },
            { id: "stepFinalizing", stages: ["FINALIZING", "COMPLETED"] }
        ];

        let reachedCurrent = false;
        steps.forEach(s => {
            const el = document.getElementById(s.id);
            if (!el) return;

            if (s.stages.includes(stage)) {
                el.className = "step-item active";
                el.querySelector(".step-icon").innerText = "▶";
                reachedCurrent = true;
            } else if (!reachedCurrent) {
                el.className = "step-item completed";
                el.querySelector(".step-icon").innerText = "✓";
            } else {
                el.className = "step-item";
                el.querySelector(".step-icon").innerText = "○";
            }
        });
    },

    onJobCompleted(status) {
        document.getElementById("progressWorkspace").classList.add("hidden");
        document.getElementById("completionWorkspace").classList.remove("hidden");

        // Comparison Stats
        const orig = status.original_info || {};
        const enh = status.enhanced_info || {};

        document.getElementById("compOrigRes").innerText = `${orig.width || 0} × ${orig.height || 0}`;
        document.getElementById("compOrigDur").innerText = orig.duration_formatted || "--";
        document.getElementById("compOrigSize").innerText = orig.filesize_formatted || "--";

        document.getElementById("compEnhRes").innerText = `${enh.width || 0} × ${enh.height || 0}`;
        document.getElementById("compEnhDur").innerText = enh.duration_formatted || "--";
        document.getElementById("compEnhSize").innerText = enh.filesize_formatted || "--";

        // Setup Dual Video Players
        const playerOrig = document.getElementById("playerOriginal");
        const playerEnh = document.getElementById("playerEnhanced");

        if (orig.filename) {
            playerOrig.src = `/api/video-file/input/${encodeURIComponent(orig.filename)}`;
        }
        if (status.output_filename) {
            playerEnh.src = `/api/video-file/output/${encodeURIComponent(status.output_filename)}`;
            
            const downloadBtn = document.getElementById("downloadBtn");
            downloadBtn.href = `/api/download/${encodeURIComponent(status.output_filename)}`;
        }

        // Auto-open output folder if enabled in settings
        const openFolderPref = document.getElementById("settingOpenFolder").checked;
        if (openFolderPref) {
            fetch("/api/open-output-folder", { method: "POST" });
        }
    },

    onJobFailed(status) {
        document.getElementById("progressWorkspace").classList.add("hidden");
        document.getElementById("enhancerWorkspace").classList.remove("hidden");
        window.MukeusApp.showError("PROCESSING FAILED", status.error || status.message);
    },

    onJobCancelled() {
        document.getElementById("progressWorkspace").classList.add("hidden");
        document.getElementById("enhancerWorkspace").classList.remove("hidden");
        window.MukeusApp.showError("CANCELLED", "Enhancement job was cancelled.");
    }
};

document.addEventListener("DOMContentLoaded", () => {
    // Cancel Job Button
    const cancelBtn = document.getElementById("cancelJobBtn");
    cancelBtn.addEventListener("click", async () => {
        const jobId = window.MukeusApp.activeJobId;
        if (jobId) {
            try {
                await fetch(`/api/cancel/${jobId}`, { method: "POST" });
            } catch (e) {
                console.warn(e);
            }
        }
    });

    // Open Output Folder Button
    const openOutputBtn = document.getElementById("openOutputFolderBtn");
    openOutputBtn.addEventListener("click", () => {
        fetch("/api/open-output-folder", { method: "POST" });
    });

    // Enhance Another Button
    const enhanceAnotherBtn = document.getElementById("enhanceAnotherBtn");
    enhanceAnotherBtn.addEventListener("click", () => {
        document.getElementById("completionWorkspace").classList.add("hidden");
        document.getElementById("uploadZone").classList.remove("hidden");
        window.MukeusApp.currentVideoMeta = null;
        document.getElementById("fileInput").value = "";
    });
});
