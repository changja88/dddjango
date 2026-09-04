from ninja import Status
from common import Resp, Base, C1


def op(flag: bool) -> Resp | Status[Base]:
    if flag:
        return Status(404, C1())
    return Resp(id=1)
