from ninja import Status
from common import Resp, Base, C1


def op(flag: bool) -> Status[Resp | Base]:
    if flag:
        return Status(400, C1())
    return Status(200, Resp(id=1))
