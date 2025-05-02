import yaml
import subprocess
import tempfile
import os
'''
convert swagger 2.0 to openapi 3.0
pip install pyyaml
npm install -g swagger2openapi
'''
def filter_swagger(input_file, output_file, include_paths_methods):
    """
    include_paths_methods: dict of {"/path": ["get", "post", ...]}
    """
    with open(input_file, 'r') as f:
        swagger = yaml.safe_load(f)

    filtered_paths = {}
    for path, methods in swagger.get('paths', {}).items():
        if path in include_paths_methods:
            filtered_methods = {
                method: op
                for method, op in methods.items()
                if method.lower() in [m.lower() for m in include_paths_methods[path]]
            }
            if filtered_methods:
                filtered_paths[path] = filtered_methods

    swagger['paths'] = filtered_paths

    # Save filtered swagger to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.yaml') as tmp:
        yaml.dump(swagger, tmp)
        tmp_input_file = tmp.name

    # Call swagger2openapi to convert to OpenAPI 3
    subprocess.run([
        'swagger2openapi',
        tmp_input_file,
        '-o', output_file
    ], check=True)

    os.remove(tmp_input_file)
    print(f"Converted OpenAPI 3.0 spec written to: {output_file}")


# Example usage
if __name__ == "__main__":
    input_swagger_file = 'swagger_2.yaml'
    output_openapi_file = 'openapi_3.yaml'

    # Choose which paths and methods to include
    include = {
        "/users": ["get", "post"],
        "/orders": ["get"]
    }

    filter_swagger(input_swagger_file, output_openapi_file, include)