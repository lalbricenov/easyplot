# -*- coding: utf-8 -*-
import re
from flask import Flask, abort, redirect, render_template, request, send_file
from html import escape
from io import BytesIO
import base64 #library to encode bynary strings to base64
from werkzeug.exceptions import default_exceptions, HTTPException
# from werkzeug.utils import secure_filename
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt

from math import sqrt, floor


# Web app
app = Flask(__name__)

numHist = 0

# This is a comment to test git
@app.after_request
def after_request(response):
    """Disable caching"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
def index():
    """Handle requests for / via GET (and POST)"""
    return render_template("index.html")


@app.route("/histogram", methods=["POST", "GET"])
def histogram():
    """Handle requests for /histogram via POST"""

    # Messages to the user. The first string is related to errors, the second to warnings, the third to successes, and the fourth to general info
    messages = {"Error":[], "Warning":[], "Success":[], "Info":[]}

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Read files
        # if request.files['fileName'].filename == '':
        #     abort(400, "Archivo faltante")
        try:
            data = request.files["fileName"].read().decode("utf-8-sig")
            #print("Here")
        except Exception:
            messages["Error"].append(f"Archivo no válido.")
            return render_template("histogram.html", histFile = "static/histograms/placeholder.png", messages = messages)
            # abort(400, "Archivo no válido")

        global numHist
        # dataFileName = f"static/dataFiles/data{numHist}.dat"
        # saveData(data, dataFileName)
        try:
            data = data.split('\n')
            data = list(map(float, data))
        except Exception:
            messages["Error"].append(f"Archivo no válido.")
            return render_template("histogram.html", histFile = "static/histograms/placeholder.png", messages = messages)

        messages["Success"].append(f"{len(data)} datos importados con éxito.")
        # Set number of intervals
        idealN = floor(sqrt(len(data)))
        if not request.form.get("nIntervals"):
            nIntervals = idealN
            messages["Info"].append(f"Número de intervalos seleccionado: {nIntervals}")
        else:
            nIntervals = int(request.form.get("nIntervals"))


        if nIntervals < 1 or nIntervals >= 5 * idealN:
            messages["Error"].append(f"ERROR: para este conjunto de datos debe usar un número de intervalos mayor a cero y menor a {5*idealN}")
            # Leave program
            return render_template("histogram.html", histFile = "static/histograms/placeholder.png", messages = messages)

        if nIntervals < int(0.7*idealN) or nIntervals > int(1.3 * idealN):
            messages["Warning"].append(f"ADVERTENCIA: para este conjunto de datos se recomienda usar un número de intervalos entre {int(0.7*idealN)} y {int(1.3 * idealN)}")

        if not request.form.get("xLabel"):
            xLabel = ""
        else:
            xLabel = request.form.get("xLabel")
        if not request.form.get("yLabel"):
            yLabel = ""
        else:
            yLabel = request.form.get("yLabel")

        histFileName = f"static/histograms/Histograma{numHist}.png"
        histogramData = plotHistogram(data, nIntervals, histFileName, xLabel, yLabel)
        
        # return render_template("index.html")
        # # message += "\n Histograma creado con éxito"
        # # Add one to the histograms counter
        # numHist = numHist + 1

        # # Output histogram
        return render_template("histogram.html", histFile = histogramData, messages = messages)
    # If user reached route via GET
    else:
        return render_template("histogram.html", histFile = "static/histograms/placeholder.png", messages = messages)

def plotHistogram(data, nIntervals, fileName, xLabel, yLabel):
    plt.hist(data, bins=nIntervals)  # arguments are passed to np.histogram

    plt.xlabel(xLabel)
    plt.ylabel(yLabel)
    # plt.savefig(fileName)
    bytesStream = BytesIO()
    # f = open("myfile.png", "wb")
    plt.savefig(bytesStream, format='png')
    # print(bytesStream.getvalue())
    ############################################## Debugging here #####################################
    # print("Here")
    # bytesStream.close()
    plt.close()
    base64Histogram = "data:image/png;base64," + base64.b64encode(bytesStream.getvalue()).decode()
    # print(base64Histogram)
    return base64Histogram



def saveData(data, fileName):
    # Determine the type of endline used in the text file
    # windows = \r\n  mac = \r  linux = \n

    # If \r\n is found, it means windows
    if data.find('\r\n') != -1:
        data = data.replace('\r\n','\n')
    # If only '\r' is found it is mac
    elif data.find('\r') != -1:
        data = data.replace('\r','\n')
    # If none of those is found, it is linux

    dataFile = open(fileName, "w")
    dataFile.write(data)
    dataFile.close()


def importData(fileName):
    dataFile = open(fileName, 'r')
    # Storing data in a list as floating point numbers
    data = dataFile.read().split('\n')
    dataFile.close()
    data = list(map(float, data))
    return data


@app.errorhandler(HTTPException)
def errorhandler(error):
    """Handle errors"""
    return render_template("error.html", error=error), error.code

@app.before_request
def before_request():
    if not request.is_secure and app.env != "development":
        url = request.url.replace("http://", "https://", 1)
        code = 301
        return redirect(url, code=code)


# https://github.com/pallets/flask/pull/2314
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    
    # ssl_context = 'adhoc' is used to serve the application over https
    # without having to mess with certificates. Requires the installation of
    # pyopenssl
    # app.run(host='127.0.0.1', port=8080, debug=True, ssl_context='adhoc')
    app.run(host='127.0.0.1', port=8080, debug=True)
