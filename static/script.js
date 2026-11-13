
// ========================================
// AI RESEARCH CONTENT GENERATOR
// Complete Frontend JavaScript
// SQLite Persistence Integrated
// ========================================


// ========================================
// HTML ELEMENTS
// ========================================

const fileInput = document.getElementById("fileInput");
const browseBtn = document.getElementById("browseBtn");
const uploadBtn = document.getElementById("uploadBtn");
const dropArea = document.getElementById("dropArea");

const selectedFilesContainer = document.getElementById("selectedFiles");
const selectedCount = document.getElementById("selectedCount");

const documentCount = document.getElementById("documentCount");
const contentCount = document.getElementById("contentCount");

const topicInput = document.getElementById("topicInput");
const contentType = document.getElementById("contentType");
const generateBtn = document.getElementById("generateBtn");

const contentPreview = document.getElementById("contentPreview");
const references = document.getElementById("references");
const verificationResult = document.getElementById("verificationResult");

const libraryList = document.getElementById("libraryList");
const historyList = document.getElementById("historyList");


// ========================================
// APPLICATION DATA
// ========================================

let pendingFiles = [];
let uploadedFiles = [];
let generationHistory = [];

const allowedExtensions = ["pdf", "docx", "pptx", "txt"];


// ========================================
// FILE VALIDATION
// ========================================

function isValidFile(file) {

    const extension = file.name.split(".").pop().toLowerCase();

    if (!allowedExtensions.includes(extension)) {

        alert("Unsupported file format: " + file.name);

        return false;
    }

    if (file.size > 20 * 1024 * 1024) {

        alert(file.name + " exceeds the 20 MB limit.");

        return false;
    }

    return true;
}


// ========================================
// FILE SELECTION
// ========================================

function addFiles(files) {

    const selectedFiles = Array.from(files);

    selectedFiles.forEach(file => {

        if (!isValidFile(file)) {
            return;
        }

        const alreadyExists = pendingFiles.some(
            item => item.name === file.name &&
                    item.size === file.size
        );

        const alreadyUploaded = uploadedFiles.some(
            item => item.name === file.name &&
                    item.size === file.size
        );

        if (!alreadyExists && !alreadyUploaded) {

            pendingFiles.push(file);
        }

    });

    renderSelectedFiles();

}


// Browse Files Button

browseBtn.addEventListener("click", () => {

    fileInput.click();

});


// File Input Change

fileInput.addEventListener("change", (event) => {

    addFiles(event.target.files);

    fileInput.value = "";

});


// ========================================
// DRAG AND DROP
// ========================================

dropArea.addEventListener("dragover", (event) => {

    event.preventDefault();

    dropArea.classList.add("drag-over");

});


dropArea.addEventListener("dragleave", () => {

    dropArea.classList.remove("drag-over");

});


dropArea.addEventListener("drop", (event) => {

    event.preventDefault();

    dropArea.classList.remove("drag-over");

    addFiles(event.dataTransfer.files);

});


// ========================================
// DISPLAY SELECTED FILES
// ========================================

function renderSelectedFiles() {

    selectedFilesContainer.innerHTML = "";

    if (pendingFiles.length === 0) {

        selectedFilesContainer.innerHTML =
            '<p class="empty-message">Your selected files will appear here.</p>';

        selectedCount.textContent = "No files selected";

        return;
    }

    selectedCount.textContent =
        pendingFiles.length + " file(s) selected";

    pendingFiles.forEach((file, index) => {

        const fileItem = document.createElement("div");

        fileItem.className = "file-item";

        const fileName = document.createElement("span");

        fileName.className = "file-name";

        fileName.textContent = file.name;

        const removeButton = document.createElement("button");

        removeButton.className = "file-remove";

        removeButton.textContent = "×";

        removeButton.type = "button";

        removeButton.title = "Remove file";

        removeButton.addEventListener("click", () => {

            pendingFiles.splice(index, 1);

            renderSelectedFiles();

        });

        fileItem.appendChild(fileName);

        fileItem.appendChild(removeButton);

        selectedFilesContainer.appendChild(fileItem);

    });

}


// ========================================
// LOAD DOCUMENTS FROM SQLITE DATABASE
// ========================================

async function loadDocumentsFromDatabase() {

    try {

        const response = await fetch("/documents");

        const result = await response.json();

        if (!response.ok) {

            throw new Error(
                result.error || "Unable to load documents."
            );

        }

        uploadedFiles = (result.documents || []).map(document => ({

            name: document.filename,

            size: 0,

            status: "Uploaded successfully",

            id: document.id,

            uploadedAt: document.uploaded_at,

            chunksStored: document.chunks_stored

        }));

        documentCount.textContent = uploadedFiles.length;

        renderLibrary();

    }

    catch (error) {

        console.error("Database document loading error:", error);

        libraryList.textContent =
            "Unable to load research documents.";

    }

}


// ========================================
// LOAD GENERATION HISTORY FROM SQLITE
// ========================================

async function loadHistoryFromDatabase() {

    try {

        const response = await fetch("/history");

        const result = await response.json();

        if (!response.ok) {

            throw new Error(
                result.error || "Unable to load generation history."
            );

        }

        generationHistory = (result.history || []).map(item => ({

            id: item.id,

            topic: item.topic,

            type: item.content_type,

            content: item.generated_content,

            date: item.created_at,

            status: "Generated successfully"

        }));

        contentCount.textContent = generationHistory.length;

        renderHistory();

    }

    catch (error) {

        console.error("Database history loading error:", error);

        historyList.textContent =
            "Unable to load generation history.";

    }

}


// ========================================
// LOAD ALL SAVED DASHBOARD DATA
// ========================================

async function loadDashboardData() {

    await Promise.all([

        loadDocumentsFromDatabase(),

        loadHistoryFromDatabase()

    ]);

}


// ========================================
// UPLOAD DOCUMENTS TO FLASK BACKEND
// ========================================

uploadBtn.addEventListener("click", async () => {

    if (pendingFiles.length === 0) {

        alert("Please select at least one document before uploading.");

        return;
    }

    const filesBeingUploaded = [...pendingFiles];

    const formData = new FormData();

    filesBeingUploaded.forEach(file => {

        formData.append("files", file);

    });

    uploadBtn.disabled = true;

    uploadBtn.textContent = "Uploading...";

    try {

        const response = await fetch("/upload", {

            method: "POST",

            body: formData

        });

        const result = await response.json();

        if (!response.ok) {

            throw new Error(
                result.error ||
                result.message ||
                "Upload failed."
            );

        }

        const serverFiles = result.files || [];

        const successfulFiles = [];

        const duplicateFiles = [];

        serverFiles.forEach(serverFile => {

            if (serverFile.status === "Uploaded successfully") {

                successfulFiles.push(serverFile.filename);

            }

            else if (
                serverFile.status === "Duplicate document detected"
            ) {

                duplicateFiles.push(serverFile.filename);

            }

        });

        // Clear processed files
        pendingFiles = [];

        renderSelectedFiles();

        // Reload saved documents from SQLite
        await loadDocumentsFromDatabase();

        // Prepare upload result message
        let message = "";

        if (successfulFiles.length > 0) {

            message += successfulFiles.length +
                " document(s) uploaded successfully.\n";

        }

        if (duplicateFiles.length > 0) {

            message += "\nDuplicate document(s) detected:\n";

            duplicateFiles.forEach(filename => {

                message += "• " + filename + "\n";

            });

            message += "\nDuplicate documents were not stored again.";

        }

        if (message === "") {

            message = result.message || "Document processing completed.";

        }

        alert(message);

    }

    catch (error) {

        console.error("Upload error:", error);

        alert("Upload failed: " + error.message);

    }

    finally {

        uploadBtn.disabled = false;

        uploadBtn.textContent = "Upload Documents";

    }

});


// ========================================
// RESEARCH LIBRARY
// ========================================

function renderLibrary() {

    libraryList.innerHTML = "";

    if (uploadedFiles.length === 0) {

        libraryList.innerHTML = `
            <div class="empty-state">
                <span>▤</span>
                <p>No research documents added yet.</p>
            </div>
        `;

        return;
    }

    uploadedFiles.forEach(file => {

        const libraryItem = document.createElement("div");

        libraryItem.className = "library-item";

        const name = document.createElement("span");

        name.className = "file-name";

        name.textContent = file.name;

        const status = document.createElement("span");

        status.className = "item-meta";

        status.textContent = "Uploaded";

        libraryItem.appendChild(name);

        libraryItem.appendChild(status);

        libraryList.appendChild(libraryItem);

    });

}


// ========================================
// DISPLAY SUPPORTING REFERENCES
// ========================================

function renderReferences(sourceList) {

    references.innerHTML = "";

    if (!sourceList || sourceList.length === 0) {

        references.innerHTML = `
            <div class="reference-placeholder">
                <span>▤</span>
                <p>No supporting references were returned.</p>
            </div>
        `;

        return;
    }

    sourceList.forEach((item, index) => {

        const referenceItem = document.createElement("div");

        referenceItem.className = "reference-item";

        const title = document.createElement("strong");

        title.textContent =
            "Source " + (index + 1) + ": " +
            (item.source || "Research Document");

        const chunk = document.createElement("p");

        chunk.className = "item-meta";

        chunk.textContent =
            "Chunk Number: " +
            (item.chunk_number ?? "Not available");

        const content = document.createElement("p");

        content.textContent =
            item.content || item.text || "Source content unavailable.";

        referenceItem.appendChild(title);

        referenceItem.appendChild(chunk);

        referenceItem.appendChild(content);

        references.appendChild(referenceItem);

    });

}


// ========================================
// DISPLAY AI VERIFICATION REPORT
// ========================================

function renderVerification(data) {

    verificationResult.innerHTML = "";

    if (!data) {

        verificationResult.textContent =
            "Verification information is unavailable.";

        return;
    }

    const status = document.createElement("h3");

    status.textContent =
        "Status: " + (data.overall_status || "Not available");

    verificationResult.appendChild(status);


    const summary = document.createElement("p");

    summary.textContent =
        data.summary || "No verification summary available.";

    verificationResult.appendChild(summary);


    const sections = [

        ["Verified Claims", data.verified_claims],

        ["Unsupported Claims", data.unsupported_claims],

        ["Contradictions", data.contradictions],

        ["Suggested Corrections", data.suggested_corrections]

    ];


    sections.forEach(([heading, items]) => {

        const title = document.createElement("h4");

        title.textContent = heading;

        verificationResult.appendChild(title);


        if (!Array.isArray(items) || items.length === 0) {

            const empty = document.createElement("p");

            empty.textContent = "None reported.";

            verificationResult.appendChild(empty);

            return;
        }


        const list = document.createElement("ul");

        items.forEach(item => {

            const listItem = document.createElement("li");

            listItem.textContent = item;

            list.appendChild(listItem);

        });

        verificationResult.appendChild(list);

    });

}


// ========================================
// GENERATE CONTENT USING GEMINI AI
// ========================================

generateBtn.addEventListener("click", async () => {

    const topic = topicInput.value.trim();

    const type = contentType.value;


    // Validate uploaded documents

    if (uploadedFiles.length === 0) {

        alert("Please upload at least one research document first.");

        return;
    }


    // Validate topic

    if (topic === "") {

        alert("Please enter a research topic.");

        topicInput.focus();

        return;
    }


    // Validate content type

    if (type === "") {

        alert("Please select a content type.");

        contentType.focus();

        return;
    }


    generateBtn.disabled = true;

    generateBtn.textContent = "Generating with Gemini...";


    contentPreview.textContent =
        "Your AI agents are researching and generating content. Please wait...";


    references.innerHTML = `
        <div class="reference-placeholder">
            <span>▤</span>
            <p>Retrieving supporting research references...</p>
        </div>
    `;


    verificationResult.textContent =
        "Verification is in progress...";


    try {

        const response = await fetch("/generate", {

            method: "POST",

            headers: {

                "Content-Type": "application/json"

            },

            body: JSON.stringify({

                topic: topic,

                content_type: type

            })

        });


        const result = await response.json();


        if (!response.ok || result.status === "error") {

            throw new Error(
                result.error ||
                result.message ||
                "Content generation failed."
            );

        }


        if (!result.generated_content) {

            throw new Error("Gemini returned empty content.");

        }


        // Display generated content

        contentPreview.textContent = result.generated_content;


        // Display references

        renderReferences(result.sources || []);


        // Display verification

        renderVerification(result.verification);


        // Reload saved generation history from SQLite

        await loadHistoryFromDatabase();


        alert("AI content generated and verification completed!");

    }

    catch (error) {

        console.error("Generation error:", error);

        contentPreview.textContent =
            "Content generation failed.\n\n" + error.message;


        references.innerHTML = `
            <div class="reference-placeholder">
                <span>!</span>
                <p>References could not be loaded.</p>
            </div>
        `;


        verificationResult.textContent =
            "Verification could not be completed because content generation failed.";


        alert("Generation failed: " + error.message);

    }

    finally {

        generateBtn.disabled = false;

        generateBtn.textContent = "✧ Generate Content";

    }

});


// ========================================
// GENERATION HISTORY
// ========================================

function renderHistory() {

    historyList.innerHTML = "";

    if (generationHistory.length === 0) {

        historyList.innerHTML = `
            <div class="empty-state">
                <span>◷</span>
                <p>No generation history available.</p>
            </div>
        `;

        return;
    }

    generationHistory.forEach(item => {

        const historyItem = document.createElement("div");

        historyItem.className = "history-item";

        const details = document.createElement("div");

        const topic = document.createElement("strong");

        topic.textContent = item.topic;

        const type = document.createElement("p");

        type.className = "item-meta";

        type.textContent =
            item.type + " | " +
            item.date + " | " +
            (item.status || "Generated");

        details.appendChild(topic);

        details.appendChild(type);

        historyItem.appendChild(details);

        historyList.appendChild(historyItem);

    });

}


// ========================================
// INITIAL PAGE SETUP
// ========================================

document.addEventListener("DOMContentLoaded", async () => {

    renderSelectedFiles();

    // Load saved records from SQLite
    await loadDashboardData();

});
