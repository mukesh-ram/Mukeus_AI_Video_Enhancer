// Global State Application Object
window.MukeusApp = {
    currentVideoMeta: null,
    selectedMode: "NATURAL",
    selectedResolution: "1080p",
    activeJobId: null,
    pollInterval: null,
    gpuInfo: null,

    init() {
        this.bindNavigation();
        this.fetchGpuInfo();
        this.fetchSettings();
    },

    bindNavigation() {
        const navItems = document.querySelectorAll(".nav-item");
        navItems.forEach(item => {
            item.addEventListener("click", () => {
                const targetView = item.getAttribute("data-view");
                this.switchView(targetView);
            });
        });
    },

    switchView(viewName) {
        // Update nav item active states
        document.querySelectorAll(".nav-item").forEach(el => {
            if (el.getAttribute("data-view") === viewName) {
                el.classList.add("active");
            } else {
                el.classList.remove("active");
            }
        });

        // Hide all view sections
        document.querySelectorAll(".view-section").forEach(sec => sec.classList.add("hidden"));

        // Show target section
        if (viewName === "enhancer") {
            document.getElementById("viewEnhancer").classList.remove("hidden");
            document.getElementById("pageTitle").innerText = "MUKEUS VIDEO ENHANCER";
        } else if (viewName === "history") {
            document.getElementById("viewHistory").classList.remove("hidden");
            document.getElementById("pageTitle").innerText = "ENHANCEMENT HISTORY";
            if (window.MukeusHistory) window.MukeusHistory.loadHistory();
        } else if (viewName === "settings") {
            document.getElementById("viewSettings").classList.remove("hidden");
            document.getElementById("pageTitle").innerText = "SYSTEM SETTINGS";
        }
    },

    async fetchGpuInfo() {
        try {
            const res = await fetch("/api/gpu");
            if (res.ok) {
                const data = await res.json();
                this.gpuInfo = data;
                this.updateGpuUI(data);
            }
        } catch (e) {
            console.warn("Could not fetch GPU info:", e);
        }
    },

    updateGpuUI(gpu) {
        // Sidebar badge
        const gpuNameEl = document.getElementById("sidebarGpuName");
        const vramEl = document.getElementById("sidebarVram");
        const cudaTag = document.getElementById("sidebarCudaTag");

        if (gpuNameEl) gpuNameEl.innerText = gpu.gpu_name;
        if (vramEl) vramEl.innerText = `${Math.round(gpu.vram_total_mb / 1024)} GB`;

        if (!gpu.cuda_available) {
            if (cudaTag) {
                cudaTag.innerText = "CPU FALLBACK";
                cudaTag.style.background = "rgba(255, 152, 0, 0.2)";
                cudaTag.style.color = "#ff9800";
            }
        }

        // Settings page
        const settingsGpu = document.getElementById("settingsGpuName");
        const settingsCuda = document.getElementById("settingsCudaStatus");
        const settingsVram = document.getElementById("settingsVram");

        if (settingsGpu) settingsGpu.innerText = gpu.gpu_name;
        if (settingsCuda) {
            settingsCuda.innerText = gpu.cuda_available ? "Available" : "CUDA Unavailable (Using CPU)";
            settingsCuda.className = gpu.cuda_available ? "setting-value green-text" : "setting-value yellow-text";
        }
        if (settingsVram) settingsVram.innerText = `${Math.round(gpu.vram_total_mb / 1024)} GB`;
    },

    async fetchSettings() {
        try {
            const res = await fetch("/api/settings");
            if (res.ok) {
                const settings = await res.json();
                document.getElementById("settingAutoDelete").checked = settings.auto_delete_temp;
                document.getElementById("settingPreserveAudio").checked = settings.preserve_audio;
                document.getElementById("settingOpenFolder").checked = settings.open_output_folder;
                document.getElementById("settingsOutputDir").innerText = settings.output_folder;
            }
        } catch (e) {
            console.warn("Could not fetch settings:", e);
        }
    },

    showError(title, message) {
        document.getElementById("errorModalTitle").innerText = title;
        document.getElementById("errorModalBody").innerText = message;
        document.getElementById("errorModal").classList.remove("hidden");
    }
};

document.addEventListener("DOMContentLoaded", () => {
    window.MukeusApp.init();

    // Modal Close
    document.getElementById("errorModalClose").addEventListener("click", () => {
        document.getElementById("errorModal").classList.add("hidden");
    });
});
