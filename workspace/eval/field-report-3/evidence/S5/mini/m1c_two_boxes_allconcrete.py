from ninja import Status
from common import Resp, C1, C2


def op(flag: int) -> Status[Resp] | Status[C1] | Status[C2]:
    if flag == 1:
        return Status(400, C1())
    if flag == 2:
        return Status(409, C2())
    return Status(200, Resp(id=1))
