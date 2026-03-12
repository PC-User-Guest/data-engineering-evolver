import random
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def generate_pyspark_change():
    path = os.path.join(BASE_DIR, "data_pipelines", "etl.py")
    snippet = "\n# added transformation '{}'%".format(random.choice(["log revenue", "filter low quantity", "add discount"]))
    with open(path, "a") as f:
        f.write(snippet)
    return path


def generate_ge_change():
    path = os.path.join(BASE_DIR, "quality", "great_expectations", "expectations", "sales_suite.json")
    # simplistic: append a fake expectation
    with open(path, "r+") as f:
        content = f.read()
        if content.endswith("}"):
            content = content[:-1] + ",\n    {\n      \"expectation_type\": \"expect_column_values_to_not_be_null\",\n      \"kwargs\": {\"column\": \"new_field\"}\n    }\n}"
            f.seek(0)
            f.write(content)
            f.truncate()
    return path


def generate_fastapi_change():
    path = os.path.join(BASE_DIR, "api", "main.py")
    snippet = "\n@app.get('/status')\ndef status():\n    return {'status': 'ok'}\n"
    with open(path, "a") as f:
        f.write(snippet)
    return path


def generate_streamlit_change():
    path = os.path.join(BASE_DIR, "dashboard", "app.py")
    snippet = "\n# added new chart placeholder\n"
    with open(path, "a") as f:
        f.write(snippet)
    return path


def generate_terraform_change():
    path = os.path.join(BASE_DIR, "infra", "main.tf")
    snippet = "\n# added redis resource placeholder\n"
    with open(path, "a") as f:
        f.write(snippet)
    return path
