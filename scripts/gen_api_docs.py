import json

from fastapi.openapi.utils import get_openapi
import mkdocs_gen_files

from tinymotion_backend.main import app


with mkdocs_gen_files.open("openapi.json", "w") as f:
    json.dump(get_openapi(
        title=app.title,
        version=app.version,
        openapi_version=app.openapi_version,
        description=app.description,
        routes=app.routes,
#        openapi_prefix=app.openapi_prefix,
    ), f)
