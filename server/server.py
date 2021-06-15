import os

from logic.get_xml_file import get_xml_file
from logic.bpmn_builder import DataColumns
from flask import Flask, request, flash, url_for, json
from werkzeug.utils import redirect, secure_filename

UPLOAD_FOLDER = "./file_uploads"
ALLOWED_EXTENSIONS = {"csv", "xes"}
app = Flask(__name__, static_url_path="")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def hello_world():
    return app.send_static_file("index.html")


@app.route("/api/upload", methods=["POST"])
def upload_file():
    if request.method == "POST":
        print(request.files)
        if "file" not in request.files:
            return {"error": "No file part"}, 400

        file = request.files["file"]

        if file.filename == "":
            return {"error": "No selected file"}, 400
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            print(file_path)
            file.save(file_path)
            dataColumns = DataColumns(
                id_col=request.form["idColumn"]
                if request.form["idColumn"]
                and len(request.form["idColumn"].strip()) != 0
                else "Case ID",
                datetime_col=request.form["timestampColumn"]
                if request.form["timestampColumn"]
                and len(request.form["timestampColumn"]) != 0
                else "Start Timestamp",
                activity_col=request.form["activityColumn"]
                if request.form["activityColumn"]
                and len(request.form["activityColumn"]) != 0
                else "Activity",
            )
            xml_file_content = get_xml_file(file_path, dataColumns)
            return {"xml_content": xml_file_content}, 200
        return
