from .controller import CatalogController

def register_catalog_api(api):
    api.register_controllers(CatalogController)
