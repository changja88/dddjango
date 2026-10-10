import application.orders.composition_root.dependency_wiring as w


class OrderController:
    def default_language(self) -> object:
        return w.wiring_material.default_language()  # 기대: #653 R-driving-attribute — driving 파일의 w.wiring_material.x()
