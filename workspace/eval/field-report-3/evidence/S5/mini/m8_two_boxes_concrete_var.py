from ninja import Status
from common import Resp, Base, C1


def op(flag: bool) -> Status[Resp] | Status[Base]:
    if flag:
        e: C1 = C1()
        return Status(400, e)
    return Status(200, Resp(id=1))
