"""orders 결선 재료 반례 — 반례마다 한 행 · 그 행에 #652 하나(설계 D17 v7 §4.3)."""
from __future__ import annotations

from django.conf import settings

from application.orders.domain_layer.order.value_object.amount import Amount
from application.orders.domain_layer.order.value_object.compaction_thresholds import CompactionThresholds
from application.orders.domain_layer.order.value_object.language_code import LanguageCode
from application.orders.driven_layer.adapter.persistence.repository.django_order_repository import DjangoOrderRepository  # 기대: #652 M-adapter-import — F2 허용 import 셋 밖(어댑터) ⟪밖이다(F2)⟫
from application.orders.domain_layer.order.value_object.settlement_amount import InvalidSettlementAmount  # 기대: #652 M-r3-reexport — r3 재수출 예외 이름(V2 클래스 아님) ⟪V2 모듈의 클래스는 `SettlementAmount` 이고 import 한 `InvalidSettlementAmount` 이 아니다⟫
from application.orders.domain_layer.order.value_object.settlement_amount import Context  # 기대: #652 M-r3-context — r3 getcontext as Context(V1 지킬 이름 별칭) ⟪V1 지킬 이름을 묶는 import 별칭⟫
from application.orders.domain_layer.order.value_object.replaced_amount import ReplacedAmount  # 기대: #652 VO-r4-replace — r4 @_replace(V1 최상단 def) ⟪V1 최상단 `FunctionDef` 문⟫
from application.orders.domain_layer.order.value_object.redefined_create_amount import RedefinedCreateAmount  # 기대: #652 VO-r4-create — r4 create 재정의(V3 @staticmethod) ⟪V3 `create` 의 데코레이터는 `@classmethod` 하나뿐이다⟫
from application.orders.domain_layer.order.value_object.shadowed_dataclass_amount import ShadowedDataclassAmount  # 기대: #652 VO-r4-dataclass — r4 dataclass 가림(V1 최상단 def) ⟪V1 최상단 `FunctionDef` 문⟫
from application.orders.domain_layer.order.value_object.staticmethod_alias_amount import StaticmethodAliasAmount  # 기대: #652 VO-r4-classmethod — r4 classmethod = staticmethod(V1′ 지킬 이름 대입) ⟪V1′ 최상단 대입 `classmethod`⟫
from application.orders.domain_layer.order.value_object.hidden_class_amount import HiddenClassAmount  # 기대: #652 VO-r4-if — r4 if True 속 클래스(V1 최상단 If) ⟪V1 최상단 `If` 문⟫
from application.orders.domain_layer.order.value_object.tuple_constant_amount import TupleConstantAmount  # 기대: #652 VO-B-constant — 표 B V1′ 밖 최상단 상수(튜플) ⟪V1′ 상수 `_ALLOWED_SCALES` 의 값이⟫
from application.orders.domain_layer.order.value_object.new_amount import NewAmount  # 기대: #652 VO-B-new — 표 B __new__(V3′) ⟪V3′ dunder 정의 `__new__`⟫
from application.orders.domain_layer.order.value_object.property_amount import PropertyAmount  # 기대: #652 VO-B-decorator — 표 B 메서드 데코레이터(V3) ⟪V3 메서드 `doubled` 에 데코레이터가 있다⟫
from application.orders.domain_layer.order.value_object.field_default_amount import FieldDefaultAmount  # 기대: #652 VO-B-default — 표 B 비상수 기본값(V3 field(...)) ⟪V3 필드 `value` 의 기본값이 V-상수가 아니다⟫
from application.orders.domain_layer.order.value_object.star_import_amount import StarImportAmount  # 기대: #652 VO-B-star — 표 B * import(V1) ⟪V1 `*` import⟫
from application.orders.domain_layer.order.value_object.no_future_amount import NoFutureAmount  # 기대: #652 VO-B-future — 표 B from __future__ 없음(V1) ⟪V1 `from __future__ import annotations` 가 없다⟫
from application.orders.domain_layer.order.value_object.late_constant_amount import LateConstantAmount  # 기대: #652 VO-V1p-late — V1′ ClassDef 뒤 상수 ⟪V1′ 최상단 상수 `_SCALE` 이 클래스 뒤에 있다⟫
from application.orders.domain_layer.order.value_object.public_constant_amount import PublicConstantAmount  # 기대: #652 VO-V1p-public — V1′ 공개 상수 ⟪V1′ 최상단 대입 `SCALE`⟫
from application.orders.domain_layer.order.value_object.variable_pattern_amount import VariablePatternAmount  # 기대: #652 VO-V1p-variable — V1′ re.compile(<변수>) ⟪V1′ 상수 `_AMOUNT_PATTERN` 의 값이⟫
from application.orders.domain_layer.order.value_object.rebound_re_amount import ReboundReAmount  # 기대: #652 VO-V1p-rebound-re — V1′ re = … 재결속 ⟪V1′ 최상단 대입 `re`⟫
from application.orders.domain_layer.order.value_object.setattr_constant_amount import SetattrConstantAmount  # 기대: #652 VO-V1p-setattr — V1′ 임의 호출 _X = setattr(…) ⟪V1′ 상수 `_PATCHED` 의 값이⟫
from application.orders.domain_layer.order.value_object.annotate_field_slots_amount import AnnotateFieldSlotsAmount  # 기대: #652 VO-V3p-1 — V3′ __annotate__ · 필드 있음(+ __annotations__ 덮기 · r5 원형) · slots=True — 실행 표본 + 탈락 사유 조각 단언(변이에서는 __annotations__ 가 또 잡아 계속 red) ⟪V3′ dunder 정의 `__annotate__`⟫
from application.orders.domain_layer.order.value_object.annotate_field_plain_amount import AnnotateFieldPlainAmount  # 기대: #652 VO-V3p-2 — V3′ __annotate__ · 필드 있음(+ __annotations__ 덮기 · r5 원형) · slots=False — 실행 표본 + 탈락 사유 조각 단언(변이에서는 __annotations__ 가 또 잡아 계속 red) ⟪V3′ dunder 정의 `__annotate__`⟫
from application.orders.domain_layer.order.value_object.annotate_bare_slots_amount import AnnotateBareSlotsAmount  # 기대: #652 VO-V3p-3 — V3′ __annotate__ · 필드 없음 · slots=True — 실행 표본 + 콜백 이름 검사의 변이 격리 ⟪V3′ dunder 정의 `__annotate__`⟫
from application.orders.domain_layer.order.value_object.annotate_bare_plain_amount import AnnotateBarePlainAmount  # 기대: #652 VO-V3p-4 — V3′ __annotate__ · 필드 없음 · slots=False — 실행 표본 + 콜백 이름 검사의 변이 격리 ⟪V3′ dunder 정의 `__annotate__`⟫
from application.orders.domain_layer.order.value_object.annotate_func_field_slots_amount import AnnotateFuncFieldSlotsAmount  # 기대: #652 VO-V3p-5 — V3′ __annotate_func__ · 필드 있음(+ __annotations__ 덮기 · r5 원형) · slots=True — 실행 표본 + 탈락 사유 조각 단언(변이에서는 __annotations__ 가 또 잡아 계속 red) ⟪V3′ dunder 정의 `__annotate_func__`⟫
from application.orders.domain_layer.order.value_object.annotate_func_field_plain_amount import AnnotateFuncFieldPlainAmount  # 기대: #652 VO-V3p-6 — V3′ __annotate_func__ · 필드 있음(+ __annotations__ 덮기 · r5 원형) · slots=False — 실행 표본 + 탈락 사유 조각 단언(변이에서는 __annotations__ 가 또 잡아 계속 red) ⟪V3′ dunder 정의 `__annotate_func__`⟫
from application.orders.domain_layer.order.value_object.annotate_func_bare_slots_amount import AnnotateFuncBareSlotsAmount  # 기대: #652 VO-V3p-7 — V3′ __annotate_func__ · 필드 없음 · slots=True — 실행 표본 + 콜백 이름 검사의 변이 격리 ⟪V3′ dunder 정의 `__annotate_func__`⟫
from application.orders.domain_layer.order.value_object.annotate_func_bare_plain_amount import AnnotateFuncBarePlainAmount  # 기대: #652 VO-V3p-8 — V3′ __annotate_func__ · 필드 없음 · slots=False — 실행 표본 + 콜백 이름 검사의 변이 격리 ⟪V3′ dunder 정의 `__annotate_func__`⟫
from application.orders.domain_layer.order.value_object.init_subclass_amount import InitSubclassAmount  # 기대: #652 VO-V3p-9 — V3′ __init_subclass__ 정의 ⟪V3′ dunder 정의 `__init_subclass__`⟫
from application.orders.domain_layer.order.value_object.set_name_amount import SetNameAmount  # 기대: #652 VO-V3p-10 — V3′ __set_name__ 정의 ⟪V3′ dunder 정의 `__set_name__`⟫
from application.orders.domain_layer.order.value_object.double_create_amount import DoubleCreateAmount  # 기대: #652 VO-I5-double-create — V4 create 두 번 묶임(둘 다 @classmethod — V3 통과 · 격리) ⟪V4 `create` 이 2번 묶인다⟫
from application.orders.domain_layer.order.value_object.double_decorator_amount import DoubleDecoratorAmount  # 기대: #652 VO-I5-double-decorator — V2 겹 데코레이터(최상단 def 없음 · 격리) ⟪V2 클래스 데코레이터가 정확히 하나가 아니다(2개)⟫
from application.orders.domain_layer.order.value_object.rebound_dataclass_amount import ReboundDataclassAmount  # 기대: #652 VO-I5-rebound-dataclass — V4 dataclass 메서드 본문 재결속(V1 · V3 통과 · 격리) ⟪V4 `dataclass` 이 2번 묶인다⟫
from application.orders.domain_layer.order.value_object.rebound_classmethod_amount import ReboundClassmethodAmount  # 기대: #652 VO-I5-rebound-classmethod — V4 classmethod 메서드 본문 재결속(V1 · V3 통과 · 격리) ⟪V4 `classmethod` 이 1번 묶인다⟫
from application.orders.domain_layer.order.value_object.annotations_method_amount import AnnotationsMethodAmount  # 기대: #652 VO-I5-annotations-method — V3′ __annotations__ 메서드(독립 모듈 — __annotations__ 이름의 변이 격리) ⟪V3′ dunder 정의 `__annotations__`⟫
from application.orders.domain_layer.order.value_object.shadowed_module_amount import ShadowedModuleAmount  # 기대: #652 VO-I2-package — F2 직접 모듈 파일 옆 같은 이름 패키지(T10 I2) ⟪직접 모듈 파일 옆에 같은 이름의 패키지 · 확장 모듈이 있다⟫
from application.orders.domain_layer.order.value_object.cased_module_amount import CasedModuleAmount  # 기대: #652 VO-J1-case-package — F2 직접 모듈 파일 옆 대소문자만 다른 같은 이름 패키지(T10 r2 J1 — 대소문자 접어 대조) ⟪직접 모듈 파일 옆에 같은 이름의 패키지 · 확장 모듈이 있다⟫

DEFAULT_CURRENCY = settings.ORDERS_DEFAULT_CURRENCY  # 기대: #652 M-module-assign — 모듈 대입(F1) ⟪최상단 `Assign` 문(F1⟫


def repository_state(state=[object()]) -> str:  # 기대: #652 M-r1-mutable-default — r1 가변 기본 인자(F3 매개변수) ⟪`repository_state` 에 매개변수가 있다(F3⟫
    return state[0]


def repository_maker(make=(lambda x=object(): lambda: x)()) -> str:  # 기대: #652 M-r1-closure-default — r1 기본값 클로저(F3 매개변수) ⟪`repository_maker` 에 매개변수가 있다(F3⟫
    return make()


def global_instance() -> str:  # 기대: #652 M-r1-global — r1 global 보관(F3 본문) ⟪`global_instance` 의 본문이 docstring 과 `return <생성식>` 한 문장이 아니다(F3)⟫
    global instance
    try:
        return instance
    except NameError:
        instance = settings.ORDERS_INSTANCE
        return instance


def attribute_instance() -> str:  # 기대: #652 M-r1-function-attribute — r1 함수 속성 보관(F3 본문) ⟪`attribute_instance` 의 본문이 docstring 과 `return <생성식>` 한 문장이 아니다(F3)⟫
    attribute_instance.instance = settings.ORDERS_INSTANCE
    return attribute_instance.instance


def unit_price() -> str:  # 기대: #652 M-r2-dict-setdefault — r2 amount.__dict__.setdefault 지역 호출(F3 본문) ⟪`unit_price` 의 본문이 docstring 과 `return <생성식>` 한 문장이 아니다(F3)⟫
    remember = unit_price.__dict__.setdefault
    return remember("instance", settings.UNIT_PRICE)


def decimal_context() -> str:  # 기대: #652 M-r2-getcontext — r2 getcontext()(생성식 밖) ⟪`getcontext` 은 허용 import(F2 · 값 객체 모듈 V1~V4)로 들인 값 객체 클래스가 아니다⟫
    return getcontext()


def customer_tiers() -> str:  # 기대: #652 M-r2-tuple — r2 tuple(settings.X)(생성식 밖) ⟪`tuple` 은 허용 import(F2 · 값 객체 모듈 V1~V4)로 들인 값 객체 클래스가 아니다⟫
    return tuple(settings.CUSTOMER_TIERS)


def discount_percent() -> int:  # 기대: #652 M-r2-settings-get — r2 settings.DISCOUNT_BY_TIER.get(…)(생성식 밖) ⟪호출이 `<값 객체 클래스>(…)` · `<값 객체 클래스>.create(…)` 가 아니다⟫
    return settings.DISCOUNT_BY_TIER.get(settings.CUSTOMER_TIER, 0)


def total_price() -> str:  # 기대: #652 M-r2-decimal-mul — r2 Decimal.__mul__(…)(생성식 밖 · create 아닌 메서드) ⟪호출이 `<값 객체 클래스>(…)` · `<값 객체 클래스>.create(…)` 가 아니다⟫
    return Decimal.__mul__(Decimal(settings.UNIT_PRICE), Decimal(settings.QUANTITY))


def checkout_enabled() -> bool:  # 기대: #652 M-r3-bool — r3 bool(settings.X)(생성식 밖 · 설정 값 변환) ⟪`bool` 은 허용 import(F2 · 값 객체 모듈 V1~V4)로 들인 값 객체 클래스가 아니다⟫
    return bool(settings.CHECKOUT_POLICY)


def compaction_limits() -> CompactionThresholds:  # 기대: #652 M-int-create — int(settings.X) 인자 create((라) 인자) ⟪인자가 (가) 설정 이름 · 닫힌 상수⟫
    return CompactionThresholds.create(trigger=int(settings.ORDERS_TRIGGER), force=int(settings.ORDERS_FORCE))


def nested_currency() -> str:  # 기대: #652 M-settings-nested — settings.X.Y((가) 한 단계 밖) ⟪생성식이 (가) `settings.<대문자 이름>` · (다) 값 객체 생성 · (라) 값 객체 `create` 셋 중 하나가 아니다⟫
    return settings.ORDERS.CURRENCY


def splat_limits() -> CompactionThresholds:  # 기대: #652 M-double-star — ** 펼침 인자((라)) ⟪`**` 펼침 인자⟫
    return CompactionThresholds.create(**settings.ORDERS_THRESHOLDS)


def bytes_limits() -> CompactionThresholds:  # 기대: #652 M-bytes-argument — b"…" 상수 인자((라) 닫힌 상수 밖) ⟪인자가 (가) 설정 이름 · 닫힌 상수⟫
    return CompactionThresholds.create(trigger=b"10", force=20)


@cache
def cached_language() -> str:  # 기대: #652 M-cache — @cache 데코레이터(F3) ⟪`cached_language` 에 데코레이터가 있다(F3)⟫
    return settings.LANGUAGE_CODE


def matched_discount() -> int:  # 기대: #652 M-match — match 분기(F3 본문) ⟪`matched_discount` 의 본문이 docstring 과 `return <생성식>` 한 문장이 아니다(F3)⟫
    match settings.CUSTOMER_TIER:
        case "vip":
            return 20
        case _:
            return 0


def build_language() -> str:  # 기대: #652 M-build-name — build_ 이름(F3) ⟪재료 이름 `build_language` 이 `_` · `build_` 로 시작한다(F3)⟫
    return settings.LANGUAGE_CODE


def limits_from_settings() -> CompactionThresholds:  # 기대: #652 M-non-create — create 아닌 생성 메서드((라)) ⟪호출이 `<값 객체 클래스>(…)` · `<값 객체 클래스>.create(…)` 가 아니다⟫
    return CompactionThresholds.from_settings(settings.ORDERS_THRESHOLDS)


def Amount() -> Amount:  # 기대: #652 M-r4-shadow — r4 재료 def Amount() 가림(F3 결속) ⟪`Amount` 이 파일에서 두 번 이상 묶인다(F3 결속⟫
    return settings.ORDERS_AMOUNT


def created_language() -> LanguageCode:  # 기대: #652 M-lead-c-no-create — (라) 인데 값 객체 모듈에 @classmethod def create 없음(V4) ⟪`LanguageCode` 의 값 객체 모듈에 `@classmethod def create` 가 없다((라) · V4)⟫
    return LanguageCode.create(settings.PARLER_DEFAULT_LANGUAGE_CODE)
