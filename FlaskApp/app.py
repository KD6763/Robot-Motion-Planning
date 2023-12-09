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