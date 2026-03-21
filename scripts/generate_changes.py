import random
import os
import json

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def generate_pyspark_change():
    path = os.path.join(BASE_DIR, "data_pipelines", "etl.py")
    snippet = "\n# added transformation '{}'".format(random.choice(["log revenue", "filter low quantity", "add discount"]))
    with open(path, "a") as f:
        f.write(snippet)
    return path


def generate_ge_change():
    path = os.path.join(BASE_DIR, "quality", "great_expectations", "expectations", "sales_suite.json")
    with open(path, "r") as f:
        data = json.load(f)

    new_expectation = {
        "expectation_type": "expect_column_values_to_not_be_null",
        "kwargs": {"column": f"new_field_{random.randint(1, 1000)}"}
    }
    data["expectations"].append(new_expectation)

    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    return path


def generate_fastapi_change():
    path = os.path.join(BASE_DIR, "api", "main.py")
    snippet = "\n@app.get('/status_{}')\ndef status_{}():\n    return {{'status': 'ok'}}\n".format(random.randint(1, 1000), random.randint(1, 1000))
    with open(path, "a") as f:
        f.write(snippet)
    return path


def generate_streamlit_change():
    path = os.path.join(BASE_DIR, "dashboard", "app.py")
    snippet = "\n# added new chart placeholder {}\n".format(random.randint(1, 1000))
    with open(path, "a") as f:
        f.write(snippet)
    return path


def generate_terraform_change():
    path = os.path.join(BASE_DIR, "infra", "main.tf")
    snippet = "\n# added redis resource placeholder {}\n".format(random.randint(1, 1000))
    with open(path, "a") as f:
        f.write(snippet)
    return path
