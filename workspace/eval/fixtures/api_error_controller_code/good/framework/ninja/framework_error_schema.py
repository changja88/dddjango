from ninja import Schema


class FrameworkErrorSchema(Schema):
    code: str
    title: str
    status: int
    detail: str
