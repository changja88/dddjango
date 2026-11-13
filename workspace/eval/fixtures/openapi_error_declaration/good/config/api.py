from ninja.openapi.schema import OpenAPISchema
from ninja_extra import NinjaExtraAPI

from framework.ninja.pre_route_responses import add_pre_route_responses


class DocumentedAPI(NinjaExtraAPI):
    def get_openapi_schema(
        self, *, path_prefix: str | None = None, path_params: dict[str, object] | None = None
    ) -> OpenAPISchema:
        return add_pre_route_responses(self, super().get_openapi_schema(path_prefix=path_prefix, path_params=path_params))


api: DocumentedAPI = DocumentedAPI(urls_namespace="api")
