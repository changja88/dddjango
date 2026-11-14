from ninja import NinjaAPI

api: NinjaAPI = NinjaAPI()
api.add_router("/ops", "cross_context.backoffice.suspension.feature.ops_api.router")
