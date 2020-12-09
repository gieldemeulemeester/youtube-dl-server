import os
from flask import Flask, render_template, request, url_for, redirect, flash, jsonify
from werkzeug.utils import secure_filename
from model.clients import ContainerClient, DownloadClient

app = Flask(__name__)
container = ContainerClient.ContainerClient()
downloader = DownloadClient.DownloadClient()

@app.route("/", methods=['GET'])
def index():
    return render_template("index.html")

@app.route("/favicon.ico")
def favicon():
    return redirect(url_for("static", filename="favicon.ico"))

@app.route("/get-flashes")
def get_flashes():
    return render_template("_flashes.html")

@app.route("/enqueue-url", methods = ["POST"])
def enqueue_url():
    url = request.form.get("url")
    options = { "format": request.form.get("format") }

    if not url:
        flash(f"{url_for('enqueue_url')} called without a 'url' query parameter", "warning")
        return redirect(url_for("index"))
    
    downloader.download_url(url, options, download_url_callback)
    flash(f"Added '{url}' to the download queue", "info")
    return redirect(url_for("index"))

@app.route("/upload-file", methods=["POST"])
def upload_file():
    files = request.files.getlist('file')
    options = { "format": request.form.get("format") }
    filepaths = []

    if not files:
        flash(f"{url_for('upload_file')} called without a 'file' query parameter", "warning")
        return redirect(url_for("index"))

    for file in files:
        if file and validate_file(file.filename):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
            file.save(filepath)
            filepaths.append(filepath)

    if len(filepaths) > 0: flash(f"{len(filepaths)} file(s) successfully uploaded", "success")
    if len(filepaths) < len(files): flash(f"{len(files) - len(filepaths)} file(s) are not valid", "warning")
    for filepath in filepaths: downloader.download_webloc(filepath, options, download_webloc_callback)
    if len(filepaths) > 0: flash(f"Added {len(filepaths)} url(s) to download queue", "info")
    return redirect(url_for("index"))

@app.route("/jobs")
def list_jobs():
    return render_template("jobs.html", jobs = downloader.jobs)

@app.route("/jobs/clear")
def clear_jobs():
    downloader.clear_jobs()
    return redirect(url_for("list_jobs"))

@app.route("/api/jobs/get-status", methods=["POST"])
def get_job_status():
    return { "status": downloader.get_job_status(request.json["id"]) }

@app.route("/api/jobs/cancel", methods=["POST"])
def cancel_job():
    return { "cancelled": downloader.cancel_job(request.json["id"]) }

def validate_file(filename):
    return True
    #return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['UPLOAD_EXTENSIONS']

def download_url_callback(success, url, filepath = None):
    if success:
        flash(f"Successfully downloaded '{url}'", "success")
    else:
        flash(f"Failed to download '{url}'", "error")

def download_webloc_callback(success, url, filepath):
    if success:
        #flash(f"Successfully downloaded '{url}'", "success")
        path = os.path.join(app.config['UPLOAD_FOLDER'], "archive")
    else:
        #flash(f"Failed to download '{url}'", "error")
        path = os.path.join(app.config['UPLOAD_FOLDER'], "invalid")            
    if not os.path.isdir(path):
        os.mkdir(path)
    os.rename(filepath, os.path.join(path, os.path.basename(filepath)))

if __name__ == '__main__':
    app.secret_key = "secret key"
    app.config['UPLOAD_FOLDER'] = "/youtube-dl/weblocs"
    app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024
    app.config['UPLOAD_EXTENSIONS'] = ['.webloc']

    if not os.path.isdir(app.config['UPLOAD_FOLDER']):
        os.mkdir(app.config['UPLOAD_FOLDER'])

    app.run(debug=False, host='0.0.0.0')
    