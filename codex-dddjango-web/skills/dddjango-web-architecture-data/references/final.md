# 데이터 아키텍처 — Either 계약·실패의 단일 출구·계약 스냅샷

> **출처:** 제1 규약(dddart 표준 파일트리, 2026-06-11~12) §3.4·§6·§9·§10-5 · dddart 파이프라인 본설계(2026-06-12) §2·§4·§5·§9 · 백스톱 스크립트 설계(2026-06-12) §7 · HaffHaff-App 실물 대조(2026-06-12) · dddjango-web 2.0.0 대응 규약(dddart → web).
> 본문 속 `(규약 §N)`·`(본설계 §N)`·`(백스톱 설계 §N)`은 **출처 표기**이며 로드 대상이 아니다 — 규칙 자체는 본문에 자족적으로 서술된다. 로드 가능한 위임은 "스킬명 + §번호(또는 주제)"와 공유 reference(`undecidable.md`)뿐.

---

## 목차

- §1. infra_layer 지도 — 단일 진실 원천 Repo와 세 이웃
- §2. 실패의 단일 출구 — safe_api_call 전 예외 정규화
- §3. Repo Either 계약 — Right=성공, 전 실패 Either
- §4. DataSource — 도메인 엔티티 직접 반환 (DTO 없음)
- §5. 로컬 데이터 2층 — BC 캐시 vs 엔진·전역
- §6. infra service — 수동 SDK 어댑터
- §7. 계약 스냅샷 체계 — 동결·기계 절단·사용 규율
- §8. 계약 위험 행위 — tracer 앵커

---

## §1. infra_layer 지도 — 단일 진실 원천 Repo와 세 이웃

infra_layer는 종류 3폴더다 (규약 §3.4 — 폴더·명명 사실은 discipline-houserules §1·§4). 하위층은 없다(§5):

| 종류 | 역할 | 계약 |
|---|---|---|
| `data_source/` 원격 | in-process `ApiClient`로 백엔드 엔드포인트를 부르는 plain class — 엔드포인트 정의 | 도메인 엔티티 **직접 반환** (§4) |
| `repository/` | **구체 클래스 (인터페이스 없음** — 규약 §9-1**)**. DataSource를 감싸는 **단일 진실 원천** | `safe_api_call`로 감싸 `Either[BadRequestResponse, T]` 반환 (§2·§3) |
| `service/` | 수동 SDK 어댑터 — 호출당하는 쪽 | §6 |

호출 방향: UseCase → Repo·infra service → DataSource·SDK. Repo·DataSource는 무상태 plain class이며 사용처가 직접 생성한다(DI 없음 — 규약 §9-13). **생성자에 의존성을 선택 키워드 인자+`or Default()` 폴백으로 받는 DI seam은 두지 않는다** — 위치 인자로 클라이언트를 넘기는 `ChannelDataSource(ApiClient())`(§3)는 정당한 직접 생성이다. 테스트는 api_client 목(`monkeypatch`)·VM 직접 생성으로 한다(implementation-test §2).

**이 스킬과 architecture-state의 경계** (본설계 §8 — 한 주제 한 소유자): data(이 스킬) = 데이터가 web 바깥(백엔드 API)과 어떻게 오가는가 / state = 들어온 데이터가 web 안에서 화면들 사이에 어떻게 살아 있는가. 판례 ① **캐싱**: 디스크 캐시 층은 web에 없다(§5), 세션·프로세스 수명 보관 = architecture-state §9. ② **에러**: 서버 에러가 오는 모양(Either 계약·정규화 — §2·§3) = 이 스킬, 그 에러를 State에 담아 표시·소비하는 방식 = architecture-state §4.

## §2. 실패의 단일 출구 — safe_api_call 전 예외 정규화

`safe_api_call`은 api_client의 상태코드 실패만이 아니라 **모든 예외**(JSON 파싱·필드 누락·타입 불일치)를 잡아 `BadRequestResponse`로 정규화한다 (규약 §3.4 — §10-5 ① 확정). Repo·infra service는 어떤 실패도 raise로 탈출시키지 않는다 — **전 실패 = Either**.

- *왜* — HaffHaff 실측: 기존 safeApiCall은 네트워크 예외만 잡아 파싱 실패가 그물 밖으로 탈출해 미정의 동작(크래시·무한 로딩)이 됐고, 타임아웃은 `isShow:false`로 무음, 좋아요류 에러는 Either 통째 폐기 — **실패의 절반이 사용자에게 도달하지 못했다.**
- 서버가 에러 바디를 주면 `BadRequestResponse.from_json`으로 그대로 싣고(서버가 보낸 `is_show`를 그대로 존중 — `from_json`은 원시 필드를 `json_field(data, "is_show", bool)`처럼 읽으므로 `is_show="false"` 같은 계약 타입 불일치는 `TypeError`가 되어 아래 가드가 정규화한다 — architecture-ddd §3), web에서 생긴 실패는 `error_type`으로 기인을 구분해 생성한다 — 어휘는 `parse`·`unknown`(in-process 호출이라 네트워크 타임아웃이 없다 — `timeout`은 생기지 않는다).
- `BadRequestResponse`의 **역할 계약** = 정규화된 에러(기인 `error_type` + 메시지 `msg` + 표시여부 `is_show`). **web 생성 에러는 `is_show=True`로 만든다** — 위 *왜*가 "타임아웃은 isShow:false로 무음"을 고장으로 진단했으므로, 정규화가 그 무음을 재생산하지 않는다(표시·소비 정책 자체는 architecture-state §4 소유). `BadRequestResponse`는 조회 실패 채널에서 그대로 raise되므로 `Exception`을 잇는다(architecture-state §4). **필드 철자(`error_type`/`msg`/`is_show`)는 HaffHaff 봉투 *예시*다** — 대상 서버 에러 봉투가 다르면(예: `{code, message}`·RFC7807 `{type, title, status, detail}`) 그 스키마로 `BadRequestResponse`를 모델링하고 `from_json`을 맞춘다(기존 서버에 확립된 봉투 우선 — `§3` Either 방향 규약과 평행).

표준 골격 — 계약의 직역이다(아래 코드의 `error_type`/`msg`/`is_show`는 **HaffHaff 봉투 기준 예시**·대상 서버 봉투에 맞춰 `from_json`·필드 조정; api_client 표기법 상세는 implementation-django §4 소유):

```python
# common/network/safe_api_call.py — 파일명 = 주 선언명 snake_case. Right=성공 (§3)
T = TypeVar("T")


def safe_api_call(api_call: Callable[[], T]) -> Either[BadRequestResponse, T]:
    try:
        return Right(value=api_call())
    except ApiStatusError as e:  # api_client가 2xx 밖 응답에서 raise — 상태코드 실패
        if isinstance(e.body, dict):
            try:
                return Left(value=BadRequestResponse.from_json(e.body))  # 서버 에러 바디 그대로 — is_show도 서버 값
            except Exception:
                # 정규화기 자신이 raise(봉투 스키마 불일치) — 이 raise는 이미 진입한 except ApiStatusError 절 내부라
                # 형제 except TypeError(아래)도 말미 catch-all(맨 끝 except Exception)도 못 잡는다(전부 같은 try의 형제).
                # 그래서 여기서 직접 단일출구로 수렴시킨다.
                return Left(value=BadRequestResponse(error_type="unknown", msg="unexpected error body", is_show=True))
        return Left(value=BadRequestResponse(
            error_type="unknown",
            msg=f"status {e.status_code}",
            is_show=True,  # web 생성 에러 — 무음 재생산 금지
        ))
    except (ValueError, KeyError) as e:  # JSON 파싱(JSONDecodeError는 ValueError)·필드 누락·값 불일치
        return Left(value=BadRequestResponse(error_type="parse", msg=str(e), is_show=True))
    except TypeError as e:  # 타입 불일치
        return Left(value=BadRequestResponse(error_type="parse", msg=str(e), is_show=True))
    except Exception as e:
        return Left(value=BadRequestResponse(error_type="unknown", msg=str(e), is_show=True))
```

> **에러바디 정규화기(`from_json`)도 raise할 수 있다** — 대상 서버 봉투가 골든 가정과 다르면(필수 필드 누락 등) `from_json`이 `KeyError`·`TypeError`를 던진다. 그 호출은 *이미 `except ApiStatusError` 절 내부*라 **형제 `except TypeError`는 물론 맨 끝 `except Exception` catch-all도 못 잡는다**(Python: 진입한 except 절 내부의 새 예외는 같은 try의 다른 except 절로 가지 않고 바깥으로 전파) → `safe_api_call` 밖으로 샌다 = 단일출구 누수. 그래서 `from_json` 호출만 try/except Exception으로 감싸 그 raise도 `Left`로 수렴시킨다. (위 "대상 서버 봉투에 맞춰 `from_json` 조정"은 *설계 시점* 대응이고, 이 가드는 *런타임 raise* 대응 — 둘은 보완.)

## §3. Repo Either 계약 — Right=성공, 전 실패 Either

Repo의 공개 메서드는 `Either[BadRequestResponse, T]`를 반환하며 **Right=성공**이다 (규약 §3.4 — 통용 관례로 2026-06-12 확정. HaffHaff 실물은 Left=성공이었으나 dddjango-web 표준은 통용 방향. **기존 프로젝트에 확립된 Either 방향이 있으면 그것 우선**).

```python
# infra_layer/repository/channel_repo.py
class ChannelRepo:
    def __init__(self) -> None:
        self._remote: ChannelDataSource = ChannelDataSource(ApiClient())

    def get_channels(self) -> Either[BadRequestResponse, list[Channel]]:
        return safe_api_call(lambda: self._remote.get_channels())
```

- **UseCase는 Repo의 Either를 통과·조합하며 새 raise를 만들지 않는다** — 조회 실패를 오류 분기로 넘기는 raise는 VM의 일이다(architecture-state §4). UseCase 자체의 규율(도메인 개념 명명·판정 소유)은 architecture-ddd §8 소유.
- Either를 받아서 실패 쪽을 버리는 코드(성공만 분해하고 에러 무시)는 금지 — HaffHaff 실측 drift(좋아요류 에러 통째 폐기)의 재발이다. 에러를 표시하지 않는 결정조차 State의 error 필드를 거쳐 명시적으로 한다(architecture-state §4).

## §4. DataSource — 도메인 엔티티 직접 반환 (DTO 없음)

원격 DataSource는 in-process `ApiClient`로 엔드포인트를 부르는 plain class이고 **도메인 엔티티를 직접 반환한다** — `dto/` 계층이 없다 (규약 §3.4·§9-2). 서버 JSON은 도메인 엔티티(frozen dataclass + `from_json` — 원시 필드는 `json_field`로 타입 확인, architecture-ddd §3)가 직접 파싱한다.

```python
# infra_layer/data_source/channel_data_source.py
class ChannelDataSource:
    def __init__(self, client: ApiClient) -> None:
        self._client: ApiClient = client

    def get_channels(self) -> list[Channel]:
        data: object = self._client.get("/api/v1/channels")  # URL 근거: server-contract.json
        return [Channel.from_json(item) for item in json_field(data, "channels", list)]  # 응답 모양이 다르면 TypeError·KeyError → safe_api_call
```

- 엔티티의 모델링(entity/value_object 구분은 architecture-ddd §3·애그리거트 경계는 §4)은 architecture-ddd 소유 — 이 스킬은 "유입 경로에 변환 계층을 두지 않는다"는 계약만 소유한다.
- 도메인 엔티티를 저장 모델로 만들지 않는다 — Django ORM `Model`을 잇거나 저장 표지를 붙이지 않는다(web에는 로컬 저장 층이 없다 — §5).
- api_client·DataSource 호출 표기법은 implementation-django §4 소유.

## §5. 로컬 데이터 2층 — BC 캐시 vs 엔진·전역

web에는 해당 없음 — web은 매 요청 서버에서 렌더하므로 BC 데이터를 로컬에 쌓는 캐시 층을 두지 않는다(데이터는 매 요청 in-process API 재조회, 화면 간 공유 값은 architecture-state §5 SharedState·세션).

## §6. infra service — 수동 SDK 어댑터

`infra_layer/service/`는 **수동** SDK 어댑터다 — 호출당하는 쪽, 상태 없음, UseCase를 모름. Repo의 자매(백엔드 API 대신 외부 SDK·라이브러리를 감쌈)다 (규약 §3.4).

- **능동이면 application, 수동이면 infra** (규약 §3.3·§3.4): 상태를 보유하고 비화면 이벤트에 반응하며 UseCase를 호출하면 `application_layer/service/`(architecture-state §6)다. HaffHaff drift 실례: `permission_service`(keepAlive Notifier·App 호출·상태 노출)가 infra에 있었다 — 성격상 application 물건.
- SDK 호출의 실패도 §2와 같은 정신으로 Either로 정규화해 반환한다 — infra service는 어떤 실패도 raise로 탈출시키지 않는다.

## §7. 계약 스냅샷 체계 — 동결·기계 절단·사용 규율

서버 계약은 추측이 아니라 **동결된 스냅샷**이 사실의 출처다 (본설계 §2·§4·§5). 기능 산출물 폴더 `.dddjango-web/<생성일>-<기능-slug>/`에 2종이 산다:

| 산출물 | 생성 시점 | 내용 | 독자 |
|---|---|---|---|
| `openapi-full.json` | G0(스코프 게이트) 승인 직후 동결 | OpenAPI 원본 **전체** — "관련 엔드포인트 절단"을 여기서 하지 않는다('관련' 판별은 LLM 재량이고 G0엔 명세가 없다) | architect · **data 리뷰어**(명세가 인용한 부분 대조 — G1 리뷰 시점엔 경량본이 아직 없다) |
| `server-contract.json` | G1(설계 게이트) 승인 직후 기계 절단 | 명세가 인용한 paths + `$ref` 전이 폐쇄 — LLM 손절단의 dangling `$ref` 차단 | coder · G2(구현 게이트) 검증 |

절단 도구는 `extract_contract.py`다 (백스톱 설계 §7 — 도구 사양의 단일 근거. 게이트 도구가 아니라 파이프라인 도구):

```
python3 "${CLAUDE_PLUGIN_ROOT}"/scripts/extract_contract.py \
  <openapi-full.json> --paths <paths-file> --out server-contract.json
```

- paths-file은 한 줄에 `GET /api/v1/members/{id}` — 명세가 인용한 엔드포인트 목록(Coordinator가 기계 추출). 인용 path가 동결본에 없으면 exit 1 + 누락 목록 + 근사 후보 병기 — **이것 자체가 발견이다**(존재하지 않는 엔드포인트 인용 = architect 임의 가정 → 설계 반송).

**에이전트별 사용 규율**:

- **architect**: 필요한 엔드포인트가 동결본에 없으면 **임의 가정하지 말고 보고**한다 (본설계 §5-1). 명세에는 인용 엔드포인트를 기계 추출 가능하게 적는다.
- **coder·G2**: **경량본(`server-contract.json`)만 본다** — full본 재해석 금지.
- **data 리뷰어**: 명세가 인용한 스냅샷(`openapi-full.json`의 해당 부분)을 직접 대조한다(타 노트·코드 안 봄) — 인용과 스냅샷의 불일치, 스냅샷 밖 가정(§8) 탐지가 일이다.
- 출처(OpenAPI 위치 — 주소·파일 경로·이 프로젝트 안 path) 해소·재동결 절차는 Coordinator 소유(커맨드 정의) — 에이전트는 받은 스냅샷을 사실로 쓰되 **갱신하지 않는다**.

## §8. 계약 위험 행위 — tracer 앵커

스냅샷·기존 DataSource 패턴으로 **확인 불가한 의미 가정**이 걸린 행위는 명세에 `계약 위험`으로 표기한다 (본설계 §5-2·§9) — 예: 문서에 없는 필드 의미 추정, 페이지네이션 방식 가정, 에러 코드 의미 가정.

- 이 표기는 **tracer**(가장 위험한 경로의 종단 1줄기 선행 구현) 발동의 기계 앵커다 — 위험 가정을 가장 싸게, 가장 먼저 실물로 검증한다.
- 판정 기준·검증 절차(누락·과잉 탐지)는 공유 reference `undecidable.md` §12 소유다(`${CLAUDE_PLUGIN_ROOT}/skills/discipline-houserules/references/undecidable.md` — 1차 결정자 architect와 검증자 data 리뷰어가 같은 파일을 적재한다). 한 줄 요지: "이 행위가 틀렸다는 것을 컴파일·백스톱·스냅샷 대조 중 무엇도 못 잡는가?" — 그렇다면 계약 위험.
- 이 스킬의 §7 사용 규율과 한 몸이다: 스냅샷이 사실의 출처이므로, **스냅샷 밖 가정은 숨기지 말고 표기**한다 — 표기가 tracer·미니 게이트(사용자 눈 확인)로 이어져 가정이 조기 검증된다.
