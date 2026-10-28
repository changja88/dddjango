"""bad_cron_job_imports_part_forms — 부품 모듈을 `import <경로>` 꼴과 `from <패키지> import <부품 모듈>` 꼴로 가져와도 같다(#662 두 줄)."""
from __future__ import annotations

import application.orders.application_layer.order.ship_parcel.ship_parcel_use_case.parcel_dispatch
from application.orders.application_layer.order.ship_parcel.ship_parcel_use_case import ship_parcel_frame
