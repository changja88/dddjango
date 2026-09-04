from ninja import Status
from common import Resp, C1


def op(flag: bool) -> Resp | Status[C1]:
    if flag:
        error = C1()
        return Status(404, error)
    return Resp(id=1)
