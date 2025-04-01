from flask import Flask, request, jsonify, send_from_directory
from pydub import AudioSegment
import os
import uuid

app = Flask(__name__)
CHUNK_DIR = "chunks"
os.makedirs(CHUNK_DIR, exist_ok=True)

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

@app.route("/split", methods=["POST"])
def split_audio():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    audio_file = request.files["file"]
    filename = f"{uuid.uuid4()}.mp3"
    filepath = os.path.join(CHUNK_DIR, filename)
    audio_file.save(filepath)

    try:
        audio = AudioSegment.from_file(filepath)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    chunk_length_ms = 10 * 60 * 1000  # 10 minutes
    chunks = []

    for i, start in enumerate(range(0, len(audio), chunk_length_ms)):
        end = min(len(audio), start + chunk_length_ms)
        chunk = audio[start:end]
        chunk_filename = f"{filename}_part{i}.mp3"
        chunk_path = os.path.join(CHUNK_DIR, chunk_filename)
        chunk.export(chunk_path, format="mp3")
        chunks.append(f"/chunks/{chunk_filename}")

    return jsonify({"chunks": chunks})

@app.route("/chunks/<filename>")
def serve_chunk(filename):
    return send_from_directory(CHUNK_DIR, filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
