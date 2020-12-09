import yaml
from sanic.response import file
from sanic_openapi import swagger_blueprint, doc


swagger_bp = swagger_blueprint


@swagger_bp.route("/swagger.yaml")
@doc.exclude(True)
def spec(request):
    with open('swagger.yaml', 'w') as f:
        f.write(yaml.dump(swagger_bp._spec.as_dict))
    return file('swagger.yaml')
