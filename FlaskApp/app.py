import base64
from datetime import datetime
from io import BytesIO
from matplotlib.figure import Figure
import json
from flask import Flask
from flask import render_template, request, jsonify

import code.simulate as s

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


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


@app.route("/generate", methods=['POST'])
def genreate():
    # Generate the figure **without using pyplot**.
    data = request.json
    num_obstacles = data["num_obstacles"]
    convex = data['convex']
    radius = data['radius']
    # radius = 5
    # print(num_obstacles)
    start, end, polygons, obstacles, thick_polygons = s.setup_env(int(num_obstacles), int(radius), convex)
    # print(obstacles)
    # print(thick_polygons)
    path, obstacles, simplified_edges = s.simulate(start, end, polygons, obstacles, thick_polygons)
    result = [data, json.loads(obstacles), json.loads(simplified_edges), json.loads(path)]
    # print(result)
    return result


@app.route("/test/")
def test():
    # Generate the figure **without using pyplot**.
    return render_template("test.html")

@app.route("/test2/")
def test2():
    # Generate the figure **without using pyplot**.
    return render_template("test2.html")