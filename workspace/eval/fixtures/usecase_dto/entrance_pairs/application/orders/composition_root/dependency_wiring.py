from application.orders.application_layer.pricing.quote_price.quote_price_use_case import QuotePriceUseCase as Quote


def _quote() -> Quote:
    return Quote()


def build_quote_price_use_case() -> object:
    return _quote()
