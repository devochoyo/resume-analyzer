// Home page: show the chosen file name and a "Analyzing..." button.
const fileInput = document.getElementById("resumeFile");
const uploadBox = document.getElementById("uploadBox");
const uploadTitle = document.getElementById("uploadTitle");
const uploadSub = document.getElementById("uploadSub");
const form = document.getElementById("analyzeForm");
const button = document.getElementById("analyzeBtn");

fileInput.addEventListener("change", function () {
    const chosen = fileInput.files[0];
    if (chosen) {
        uploadTitle.textContent = chosen.name;
        uploadSub.textContent = "Tap to choose a different file";
        uploadBox.classList.add("has-file");
    } else {
        uploadTitle.textContent = "Tap to choose a file";
        uploadSub.textContent = "PDF or TXT";
        uploadBox.classList.remove("has-file");
    }
});

form.addEventListener("submit", function () {
    button.disabled = true;
    button.textContent = "Analyzing...";
});
