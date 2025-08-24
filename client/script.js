class VideoSubtitleApp {
    constructor() {
        this.apiUrl = "http://localhost:8000"; // URL de votre backend
        this.selectedFile = null;
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        const fileInput = document.getElementById("fileInput");
        const uploadSection = document.getElementById("uploadSection");
        const processBtn = document.getElementById("processBtn");

        // Upload de fichier
        fileInput.addEventListener("change", (e) =>
            this.handleFileSelect(e.target.files[0])
        );

        // Drag & Drop
        uploadSection.addEventListener("dragover", (e) => {
            e.preventDefault();
            uploadSection.classList.add("dragover");
        });

        uploadSection.addEventListener("dragleave", () => {
            uploadSection.classList.remove("dragover");
        });

        uploadSection.addEventListener("drop", (e) => {
            e.preventDefault();
            uploadSection.classList.remove("dragover");
            const file = e.dataTransfer.files[0];
            if (file) this.handleFileSelect(file);
        });

        // Bouton de traitement
        processBtn.addEventListener("click", () => this.processVideo());
    }

    handleFileSelect(file) {
        if (!file) return;

        // Vérifier le format
        const validFormats = ["mp4", "avi", "mov", "mkv"];
        const fileExtension = file.name.split(".").pop().toLowerCase();

        if (!validFormats.includes(fileExtension)) {
            this.showError(
                "Format de fichier non supporté. Utilisez MP4, AVI, MOV ou MKV."
            );
            return;
        }

        this.selectedFile = file;
        this.showFileInfo(file);
        document.getElementById("processBtn").disabled = false;
    }

    showFileInfo(file) {
        const fileInfo = document.getElementById("fileInfo");
        const fileDetails = document.getElementById("fileDetails");

        const sizeInMB = (file.size / (1024 * 1024)).toFixed(2);

        fileDetails.innerHTML = `
                    <div class="info-row">
                        <span><strong>Nom:</strong></span>
                        <span>${file.name}</span>
                    </div>
                    <div class="info-row">
                        <span><strong>Taille:</strong></span>
                        <span>${sizeInMB} MB</span>
                    </div>
                    <div class="info-row">
                        <span><strong>Type:</strong></span>
                        <span>${file.type || "N/A"}</span>
                    </div>
                `;

        fileInfo.style.display = "block";
    }

    async processVideo() {
        if (!this.selectedFile) return;

        const processBtn = document.getElementById("processBtn");
        const progressSection = document.getElementById("progressSection");

        processBtn.disabled = true;
        progressSection.style.display = "block";

        // Réinitialiser les sections
        document.getElementById("resultsSection").style.display = "none";
        document.getElementById("errorSection").style.display = "none";

        try {
            await this.uploadAndTranslate();
        } catch (error) {
            this.showError(
                error.message || "Une erreur est survenue lors du traitement"
            );
        } finally {
            processBtn.disabled = false;
        }
    }

    async uploadAndTranslate() {
        const formData = new FormData();
        formData.append("file", this.selectedFile);
        formData.append(
            "source_lang",
            document.getElementById("sourceLang").value
        );
        formData.append(
            "target_lang",
            document.getElementById("targetLang").value
        );

        // Simulation du progrès
        this.updateProgress(0, "Préparation du fichier...");
        this.updateStatus("uploadStatus", "active");

        await this.delay(1000);
        this.updateProgress(20, "Upload en cours...");

        try {
            const response = await fetch(
                `${this.apiUrl}/upload-and-translate`,
                {
                    method: "POST",
                    body: formData,
                }
            );

            if (!response.ok) {
                throw new Error(`Erreur serveur: ${response.status}`);
            }

            this.updateProgress(40, "Extraction de l'audio...");
            this.updateStatus("uploadStatus", "completed");
            this.updateStatus("extractStatus", "active");

            await this.delay(2000);
            this.updateProgress(60, "Transcription avec Whisper...");
            this.updateStatus("extractStatus", "completed");
            this.updateStatus("transcribeStatus", "active");

            await this.delay(3000);
            this.updateProgress(80, "Traduction des segments...");
            this.updateStatus("transcribeStatus", "completed");
            this.updateStatus("translateStatus", "active");

            await this.delay(2000);
            this.updateProgress(95, "Génération des sous-titres...");
            this.updateStatus("translateStatus", "completed");
            this.updateStatus("generateStatus", "active");

            const result = await response.json();

            await this.delay(1000);
            this.updateProgress(100, "Traitement terminé!");
            this.updateStatus("generateStatus", "completed");

            this.showResults(result);
        } catch (error) {
            throw new Error(
                `Erreur de communication avec le serveur: ${error.message}`
            );
        }
    }

    updateProgress(percent, text) {
        document.getElementById("progressBar").style.width = `${percent}%`;
        document.getElementById("progressText").textContent = text;
    }

    updateStatus(statusId, state) {
        const statusItem = document.getElementById(statusId);
        const icon = statusItem.querySelector(".status-icon");

        statusItem.classList.remove("active", "completed");

        if (state === "active") {
            statusItem.classList.add("active");
            icon.innerHTML = '<div class="spinner"></div>';
        } else if (state === "completed") {
            statusItem.classList.add("completed");
            icon.textContent = "✅";
        }
    }

    showResults(result) {
        const resultsSection = document.getElementById("resultsSection");
        const downloadBtn = document.getElementById("downloadBtn");

        // Configuration du bouton de téléchargement
        const filename = result.srt_file_path.split("/").pop();
        downloadBtn.href = `${this.apiUrl}/download-srt/${filename}`;
        downloadBtn.download = "subtitles.srt";

        // Affichage des informations
        const segmentCount = result.segments_count || "N/A";
        resultsSection.querySelector("p").innerHTML = `
                    Vos sous-titres ont été générés avec succès.<br>
                    <strong>${segmentCount}</strong> segments traduits.
                `;

        resultsSection.style.display = "block";

        // Masquer la section de progression
        document.getElementById("progressSection").style.display = "none";
    }

    showError(message) {
        const errorSection = document.getElementById("errorSection");
        const errorMessage = document.getElementById("errorMessage");

        errorMessage.textContent = message;
        errorSection.style.display = "block";

        // Masquer les autres sections
        document.getElementById("progressSection").style.display = "none";
        document.getElementById("resultsSection").style.display = "none";
    }

    delay(ms) {
        return new Promise((resolve) => setTimeout(resolve, ms));
    }
}

// Initialiser l'application
document.addEventListener("DOMContentLoaded", () => {
    new VideoSubtitleApp();
});
