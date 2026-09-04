document.addEventListener("DOMContentLoaded", () => {
    const fileInput = document.getElementById("fileInput");
    const browseBtn = document.getElementById("browseBtn");
    const dropArea = document.getElementById("dropArea");
    const changeVideoBtn = document.getElementById("changeVideoBtn");

    browseBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        fileInput.click();
    });

    dropArea.addEventListener("click", () => {
        fileInput.click();
    });

    fileInput.addEventListener("change", (e) => {
        if (fileInput.files.length > 0) {
            handleFileSelection(fileInput.files[0]);
        }
    });

    // Drag & Drop handlers
    ['dragenter', 'dragover'].forEach(eventName => {
        dropArea.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropArea.classList.add("drag-over");
        }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropArea.classList.remove("drag-over");
        }, false);
    });

    dropArea.addEventListener("drop", (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files.length > 0) {
            handleFileSelection(files[0]);
        }
    });

    changeVideoBtn.addEventListener("click", () => {
        document.getElementById("enhancerWorkspace").classList.add("hidden");
        document.getElementById("uploadZone").classList.remove("hidden");
        window.MukeusApp.currentVideoMeta = null;
        fileInput.value = "";
    });
});

async function handleFileSelection(file) {
    // Client side size validation (500 MB)
    const MAX_SIZE = 500 * 1024 * 1024;
    if (file.size > MAX_SIZE) {
        window.MukeusApp.showError("FILE TOO LARGE", "Maximum input size is 500 MB. Please select a smaller gaming clip.");
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    // Show loading state
    const headline = document.querySelector(".upload-headline");
    const subtext = document.querySelector(".upload-subtext");
    const origHeadline = headline.innerText;
    headline.innerText = "ANALYZING VIDEO...";
    subtext.innerText = "Extracting video metadata with FFprobe...";

    try {
        const res = await fetch("/api/upload", {
            method: "POST",
            body: formData
        });

        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || "Failed to analyze video.");
        }

        const meta = await res.json();
        window.MukeusApp.currentVideoMeta = meta;
        renderMetadataUI(meta);

    } catch (e) {
        window.MukeusApp.showError("UPLOAD ERROR", e.message);
    } finally {
        headline.innerText = origHeadline;
        subtext.innerText = "Drag & Drop your gaming clip here or click browse";
    }
}

function renderMetadataUI(meta) {
    document.getElementById("uploadZone").classList.add("hidden");
    document.getElementById("enhancerWorkspace").classList.remove("hidden");

    document.getElementById("metaFilename").innerText = meta.filename;
    document.getElementById("metaFileSize").innerText = meta.filesize_formatted;
    document.getElementById("metaResolution").innerText = `${meta.width} × ${meta.height}`;
    document.getElementById("metaFps").innerText = `${meta.fps} FPS`;
    document.getElementById("metaDuration").innerText = meta.duration_formatted;
    document.getElementById("metaCodecs").innerText = `${meta.video_codec} / ${meta.audio_codec}`;

    const portraitBadge = document.getElementById("portraitBadge");
    if (meta.is_portrait) {
        portraitBadge.classList.remove("hidden");
    } else {
        portraitBadge.classList.add("hidden");
    }
}
