const fileInput = document.getElementById("cropImage");
const uploadArea = document.getElementById("uploadArea");
const preview = document.getElementById("preview");
const analyzeBtn = document.getElementById("analyzeBtn");

uploadArea.addEventListener("click", (e) => {
  if (!e.target.closest("button")) fileInput.click();
});

fileInput.addEventListener("change", showPreview);

uploadArea.addEventListener("dragover", (e) => {
  e.preventDefault();
  uploadArea.style.background = "#f3f8ee";
});

uploadArea.addEventListener("dragleave", () => {
  uploadArea.style.background = "#fff";
});

uploadArea.addEventListener("drop", (e) => {
  e.preventDefault();
  uploadArea.style.background = "#fff";
  if (e.dataTransfer.files.length) {
    fileInput.files = e.dataTransfer.files;
    showPreview();
  }
});

function showPreview() {
  const file = fileInput.files[0];
  if (!file) return;
  const url = URL.createObjectURL(file);
  preview.src = url;
  preview.style.display = "block";
}

analyzeBtn.addEventListener("click", async () => {
    const file = fileInput.files[0];

    if (!file) {
        alert("Please choose a crop image first.");
        return;
    }

    analyzeBtn.textContent = "Analyzing with AI...";
    analyzeBtn.disabled = true;

    const formData = new FormData();
    formData.append("image", file);

    try {
        const response = await fetch("/analyze", {
            method: "POST",
            body: formData
        });

        const result = await response.json();

        if (result.success) {

            document.getElementById("confidence").textContent =
                Math.round(result.confidence) + "%";

            const cleanDisease = result.disease
    .replace(/___/g, " — ")
    .replace(/_/g, " ");

document.getElementById("condition").textContent =
    cleanDisease;

            document.getElementById("conditionText").textContent =
    `AI analysis completed successfully. Confidence level: ${result.confidence_level}.`;

            document.getElementById("action").textContent =
                result.action;

            analyzeBtn.textContent = "AI Analysis Complete ✓";

        } else {

            alert(result.message);

            analyzeBtn.textContent = "Run AI Analysis →";
            analyzeBtn.disabled = false;
        }

    } catch (error) {

        console.error(error);

        alert("Could not connect to the Flask AI server.");

        analyzeBtn.textContent = "Run AI Analysis →";
        analyzeBtn.disabled = false;
    }
}); 

async function recommendCrop() {
    const n = Number(document.getElementById("n").value);
    const p = Number(document.getElementById("p").value);
    const k = Number(document.getElementById("k").value);
    const ph = Number(document.getElementById("ph").value);
    const temp = Number(document.getElementById("temp").value);
    const rain = Number(document.getElementById("rain").value);

    try {
        const formData = new FormData();

        formData.append("n", n);
        formData.append("p", p);
        formData.append("k", k);
        formData.append("ph", ph);
        formData.append("temp", temp);
        formData.append("rain", rain);

        const response = await fetch("/recommend", {
            method: "POST",
            body: formData
        });

        const result = await response.json();

        if (result.success) {
            document.getElementById("cropName").textContent = result.crop;
            document.getElementById("suitability").textContent =
                result.score + "%";

            document.getElementById("suitabilityBar").style.width =
                result.score + "%";

            document.getElementById("cropReason").textContent =
                result.reason;
        } else {
            alert(result.message || "Could not generate recommendation.");
        }

    } catch (error) {
        console.error(error);
        alert("Could not connect to the Flask recommendation server.");
    }
}

function toggleMenu() {
  const links = document.querySelector(".nav-links");
  if (links.style.display === "flex") {
    links.style.display = "";
  } else {
    links.style.display = "flex";
    links.style.position = "absolute";
    links.style.top = "76px";
    links.style.left = "0";
    links.style.right = "0";
    links.style.padding = "20px";
    links.style.background = "#fff";
    links.style.flexDirection = "column";
    links.style.borderBottom = "1px solid #dce3d9";
  }
}
