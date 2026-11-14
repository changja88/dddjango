from framework.pure.base_model import TimestampedModel


class StampedMirror(TimestampedModel):
    status: str = "open"
