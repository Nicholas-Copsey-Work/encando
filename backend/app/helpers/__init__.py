import os
from importlib import util
from flask import request, jsonify

def validate_request_body(func, expected_body):
    def wrapper(*args, **kwargs):
        if not expected_body:
            return func(*args, **kwargs)
        if not request.is_json:
            return jsonify({"error": "Request body must be JSON"}), 400
        body = request.get_json()
        def check_keys(expected, actual, path=""):
            missing = []
            for key, value in expected.items():
                current_path = f"{path}.{key}" if path else key
                if key not in actual:
                    missing.append(current_path)
                elif isinstance(value, dict) and isinstance(actual[key], dict):
                    missing.extend(check_keys(value, actual[key], current_path))
            return missing

        missing_keys = check_keys(expected_body, body)
        # missing_keys = [key for key in expected_body if key not in body]
        if missing_keys:
            return jsonify({"error": f"Missing keys in request body: {missing_keys}"}), 400
        return func(*args, **kwargs)
    return wrapper

def RegisterRoutes(app, api_path, version, sub_path = ""):
    def getDirContents(path):
        return os.scandir(path)

    def importModuleFromPath(filepath, attribute = "handler"):
        module_name = os.path.splitext(os.path.basename(filepath))[0]
        spec = util.spec_from_file_location(module_name, filepath)
        if spec is None:
            raise ImportError(f"Could not load spec for {filepath}")
        module = util.module_from_spec(spec)
        spec.loader.exec_module(module)
        func = getattr(module, attribute, None)
        if not callable(func) and attribute == "handler":
            raise AttributeError(f"No callable '{attribute}' function in {filepath}")
        return func

    def getEndpointPath(method, route_path):
        return f"{method}_{route_path}"
    acceptable_methods = ['get', 'put', 'post', 'patch', 'delete']
    for child in getDirContents(os.path.join(api_path)):
        if child.is_dir():
            if child.name.startswith("_"):
                sub_path = f"{sub_path}/<{child.name.removeprefix("_")}>"
            else:
                sub_path = f"{sub_path}/{child.name}"
            RegisterRoutes(app, os.path.join(api_path, child.name), version, sub_path)
            continue
        method = child.name.removesuffix('.py')
        if method in acceptable_methods:
            print(f"Adding {method.upper()} {version}{sub_path}")
            func = importModuleFromPath(child.path)
            expected_body = False
            try:
                expected_body = importModuleFromPath(child.path, "expected_body")
            except ImportError:
                pass
            else:
                print("Adding request body validator.")
            app.route(f"{version}{sub_path}", endpoint=getEndpointPath(method, sub_path), methods=[method])(validate_request_body(func, expected_body))
