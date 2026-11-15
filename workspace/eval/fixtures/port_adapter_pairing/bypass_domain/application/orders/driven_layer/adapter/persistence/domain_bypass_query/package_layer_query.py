from application.orders import domain_layer


class DjangoPackageLayerDomainBypassQuery:
    def name(self) -> str:
        return domain_layer.__name__
