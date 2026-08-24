from __future__ import annotations

from abc import ABC, abstractmethod

from application.orders.domain_layer.audit_trail.audit_trail import AuditTrail


class AuditTrailRepository(ABC):
    @abstractmethod
    def get(self, audit_trail_id: str) -> AuditTrail: ...

    @abstractmethod
    def save(self, audit_trail: AuditTrail) -> None: ...
