"""void_cycle 서비스."""
from typing import Optional
from application.orbit.domain_layer.shared_value_object.void.void_branch import VoidBranch
from .cycle_step import next_step


def void_cycle() -> Optional[VoidBranch]:
    raise NotImplementedError
