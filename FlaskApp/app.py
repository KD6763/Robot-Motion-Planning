import base64
from datetime import datetime
from io import BytesIO
from flask import Flask
from matplotlib.figure import Figure
from flask import render_template

import code.simulate as s

app = Flask(__name__)


@app.route("/")
def home():
    return "Hello, Flask!"


@app.route("/hello/")
@app.route("/hello/<name>")
def hello(name = None):
    return render_template(
        "hello.html",
        name = name,
        date = datetime.now()
    )


@app.route("/plot/")
def plot():
    # Generate the figure **without using pyplot**.
    fig = Figure()
    ax = fig.subplots()
    ax.plot([1, 2])
    # Save it to a temporary buffer.
    buf = BytesIO()
    fig.savefig(buf, format="png")
    # Embed the result in the html output.
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    return f"<img src='data:image/png;base64,{data}'/>"


@app.route("/sim/")
def sim():
    # Generate the figure **without using pyplot**.
    path = s.simulate()
    return str(path)

@app.route("/generate/")
def sim():
    # Generate the figure **without using pyplot**.
    path = s.simulate()
    return str(path)


@app.route("/test/")
def test():
    # Generate the figure **without using pyplot**.
    path = s.simulate()
    return render_template("test.html")