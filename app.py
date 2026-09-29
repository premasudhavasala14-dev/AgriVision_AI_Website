from flask import Flask, render_template, request, jsonify
from transformers import AutoModelForImageClassification
from PIL import Image
import torch
from torchvision import transforms

app = Flask(__name__)

# Path to the trained AI model
MODEL_PATH = "model/plant_disease"

# Load the AI model
model = AutoModelForImageClassification.from_pretrained(MODEL_PATH)
model.eval()

# Image preprocessing
image_transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():

    if "image" not in request.files:
        return jsonify({
            "success": False,
            "message": "No image was uploaded."
        })

    image_file = request.files["image"]

    if image_file.filename == "":
        return jsonify({
            "success": False,
            "message": "No image was selected."
        })

    try:
        # Open uploaded image
        image = Image.open(image_file).convert("RGB")

        # Preprocess image
        image_tensor = image_transform(image).unsqueeze(0)

        # Run AI model
        with torch.no_grad():
            outputs = model(pixel_values=image_tensor)

        # Convert logits to probabilities
        probabilities = torch.nn.functional.softmax(
            outputs.logits,
            dim=-1
        )

        # Get highest probability
        confidence, predicted_class = torch.max(
            probabilities,
            dim=-1
        )

        confidence_percent = float(confidence.item() * 100)

        # Get predicted disease
        class_id = predicted_class.item()
        disease_name = model.config.id2label[class_id]

        # Determine confidence level
        if confidence_percent >= 80:
            confidence_level = "High confidence"
        elif confidence_percent >= 60:
            confidence_level = "Moderate confidence"
        else:
            confidence_level = "Low confidence"

        # Create recommendation
        if "healthy" in disease_name.lower():

            action = (
                "The crop appears healthy. Continue regular monitoring "
                "and maintain proper irrigation and nutrition."
            )

        else:

            action = (
                "A possible disease was detected. Inspect the affected "
                "leaves carefully and consider getting expert agricultural "
                "advice before applying treatment."
            )

        # Extra warning for low-confidence predictions
        if confidence_percent < 60:

            action += (
                " The AI confidence is low, so try another clear image "
                "of the affected leaf for a more reliable result."
            )

        return jsonify({
            "success": True,
            "disease": disease_name,
            "confidence": round(confidence_percent, 2),
            "confidence_level": confidence_level,
            "action": action
        })

    except Exception as error:

        print("AI prediction error:", error)

        return jsonify({
            "success": False,
            "message": "Could not analyze the image."
        })


@app.route("/recommend", methods=["POST"])
def recommend():
    data = request.form

    n = float(data.get("n", 0))
    p = float(data.get("p", 0))
    k = float(data.get("k", 0))
    ph = float(data.get("ph", 0))
    temp = float(data.get("temp", 0))
    rain = float(data.get("rain", 0))

    # Simple agriculture recommendation logic
    if ph < 5.5 and rain < 100:
        crop = "Millet"
        score = 87
        reason = "Low soil pH and lower rainfall are more suitable for millet."

    elif temp < 20:
        crop = "Wheat"
        score = 89
        reason = "The temperature conditions are suitable for wheat."

    elif n > 110 and rain > 180:
        crop = "Maize"
        score = 90
        reason = "High nitrogen and rainfall conditions support maize."

    elif 6 <= ph <= 7.5 and k > 80:
        crop = "Potato"
        score = 88
        reason = "The soil pH and potassium levels are suitable for potato."

    else:
        crop = "Rice"
        score = 91
        reason = "The sample inputs indicate a warm, moisture-friendly crop profile."

    return jsonify({
        "success": True,
        "crop": crop,
        "score": score,
        "reason": reason
    })   

if __name__ == "__main__":
    app.run(debug=True)