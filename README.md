# Lemur API - Dictionnaire Lémuriens Madagascar

## Overview
This repository contains a Flask-based REST API that serves as a dictionary and recognition service for Madagascar's lemurs. It provides endpoints to search for lemurs by common or scientific names, view detailed information (habitat, IUCN status, diet, and images), and classify images of lemurs using a deep learning model based on TensorFlow and Keras (Inception V3).

## Features
- **Lemur Dictionary**: Search for lemur species by name, view their status, habitat, and descriptions.
- **Image Recognition**: Upload an image of a lemur and let the AI predict the species using a pre-trained image classification model.
- **Swagger Documentation**: An integrated Swagger UI is available to explore and test the API endpoints effortlessly.
- **SQLite Database**: A local database stores comprehensive information about the different lemur species and their habitats.

## Tech Stack
- **Framework**: Flask, Flask-RESTX
- **Database**: SQLite3
- **Machine Learning**: TensorFlow, Keras, TensorFlow Hub (Inception V3)
- **Other Libraries**: NumPy, Pillow, Werkzeug

## Getting Started

### Prerequisites
Make sure you have Python 3.8+ installed. You can set up a virtual environment and install the required dependencies:

```bash
# Create a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

# Install the dependencies
pip install -r requirements.txt
```

### Dataset and Model Setup
1. Ensure that the database file `database/database.db` is present.
2. The AI model weights are loaded from `model/model.weights.h5`. Ensure this file is placed in the designated directory.
3. Reference images are stored in `static/dataset_lemuriens_reduce`.

### Running the Application
Start the Flask development server:

```bash
python app.py
```

The server will start by default on `http://127.0.0.1:5000/`.

## API Documentation (Swagger)
The API provides an interactive Swagger UI for testing. Once the server is running, you can access the documentation at:
- **`http://127.0.0.1:5000/swagger`**

### Endpoints
- `GET /lemurs` : List all lemurs or search using `?q=nome_ou_scientifique`
- `GET /lemurs/{lemur_id}` : Get detailed information about a specific lemur species.
- `POST /lemurs/predict` : Upload an image file (using the key `lemur`) to identify the species via the AI model.

## Folder Structure
```text
.
├── database/            # SQLite database files
├── model/               # Model weights and related files for TensorFlow
├── static/              # Image datasets, uploaded files, and static assets
├── app.py               # Main Flask application and API configuration
├── function.py          # ML prediction logic, file handling, and database queries
├── static.py            # Configuration variables and paths
├── requirements.txt     # Python project dependencies
└── TrainingImageLemur.ipynb  # Jupyter notebook for training the CNN model
```

## AI Model Details
The AI component is built using Transfer Learning on top of Google's Inception V3 architecture, specializing via `iNaturalist` feature vectors. The top classifier is trained to distinct various Madagascar lemur classes. Images are preprocessed and augmented (e.g., resizing to 299x299, contrast, rotation) before being fed to the model.
