"""대소문자만 다른 같은 이름 패키지 — 대소문자를 완화하는 import 환경에서는 옆의 cased_module_amount.py 대신 이 패키지가 들어온다."""
from decimal import getcontext as CasedModuleAmount
