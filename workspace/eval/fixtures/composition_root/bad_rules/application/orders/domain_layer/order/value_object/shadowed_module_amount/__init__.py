"""같은 이름 패키지 — import 는 옆의 shadowed_module_amount.py 가 아니라 이 패키지를 들인다."""
from decimal import getcontext as ShadowedModuleAmount
