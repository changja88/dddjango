# Skill Performance Grading Report

## 1. architecture-api

### Analysis

**WITH skill** (`api-with.md`): Structured around numbered design sections (Resource Identification, URL Structure, HTTP Methods Matrix, Status Codes, Error Responses, Pagination, Response Formats). Uses RFC 9457 Problem Details for error responses. Explicitly states conventions like "kebab-case lowercase nouns", "max 3 levels deep", URL-path versioning with `/v1/`. Requires `Idempotency-Key` header for POST orders. Cursor-based pagination with base64 opaque tokens. Ends with a cross-skill reference section.

**WITHOUT skill** (`api-without.md`): Also well-structured, covering URLs, HTTP methods, state machine, request/response formats, pagination, status codes, error responses. Uses verb-based endpoints for state transitions (`/orders/{id}/confirm`, `/orders/{id}/cancel`). Custom error format with `error.code` and `error.details`. Includes Django model code and URL config. No cross-skill reference section.

| Criterion | With | Without | Winner | Reasoning |
|-----------|------|---------|--------|-----------|
| Reference Knowledge | 1/1 | 0/1 | with | WITH cites RFC 9457 Problem Details (`application/problem+json`), names the cursor pagination principle ("17x faster than offset"), enforces Idempotency-Key as a named pattern, and states explicit URL conventions (kebab-case, no trailing slash, max 3 levels). WITHOUT uses a generic custom error format and does not reference RFC 9457 or named API design principles. |
| Mode Compliance | 1/1 | 0/1 | with | WITH follows a Design mode format with systematic sections (Resource Identification, URL Structure, HTTP Method Matrix, Status Codes, Error Format, Pagination, Response Format, Endpoint Summary). WITHOUT is more of a general API spec document mixing design and Django implementation. |
| Code Quality | 1/1 | 1/1 | tie | Both produce correct, production-ready API specifications. WITHOUT includes Django model code and URLs which are useful but shift focus from pure API design. WITH stays focused on the API contract. |
| Cross-Skill Ref | 1/1 | 0/1 | with | WITH ends with "관련 스킬 참조" linking to implementation-django-ninja and architecture-db. WITHOUT has no such section. |
| Differentiation | 1/1 | 0/1 | with | WITH contains RFC 9457, Idempotency-Key pattern, explicit URL naming conventions, and cursor pagination rationale that are absent from WITHOUT. WITHOUT includes Django models and state machine diagram not in WITH, but these are implementation concerns, not API design reference knowledge. |
| **Total** | **5/5** | **1/5** | **WIN** | |

---

## 2. architecture-db

### Analysis

**WITH skill** (`db-with.md`): Presents a conceptual model (ERD), logical model (3NF DDL), normalization analysis with explicit 1NF/2NF/3NF justification table, explains intentional denormalization points (`orders.total_amount`, `order_items.unit_price`), uses Adjacency List pattern for categories (named and justified). Physical model with query-workload-driven indexing strategy including partial indexes. Transaction isolation levels mapped per operation type (Read Committed, Repeatable Read, Serializable) with SQL examples using `SELECT ... FOR UPDATE`. Ends with cross-skill references.

**WITHOUT skill** (`db-without.md`): More elaborate schema with additional tables (ProductCategory M:N, ProductOption). Uses MySQL syntax (AUTO_INCREMENT, backtick-quoted `order`). Includes 3NF + strategic denormalization (review_avg, review_count, product_count, item_count). Extensive indexing with comments per index. Transaction isolation per operation. Full Django model implementation and OrderService class. No cross-skill reference.

| Criterion | With | Without | Winner | Reasoning |
|-----------|------|---------|--------|-----------|
| Reference Knowledge | 1/1 | 0/1 | with | WITH explicitly names and justifies the Adjacency List pattern for category hierarchy with rationale ("depth limited to 3-4 levels, simple updates"), cites normalization levels (1NF/2NF/3NF) with formal dependency language ("complete functional dependency", "transitive dependency"), distinguishes "business requirement" from "denormalization" for unit_price snapshot, and explains index column ordering principle ("equality before range in B+Tree"). WITHOUT covers similar ground but with less formal reference terminology. |
| Mode Compliance | 1/1 | 0/1 | with | WITH follows a Design mode structure: Conceptual Model, Logical Model, Normalization Analysis, Physical Model (Indexing), Transaction Isolation. This is a clean architectural progression. WITHOUT mixes schema design with Django model implementation and service code. |
| Code Quality | 1/1 | 1/1 | tie | Both produce correct, well-designed schemas. WITHOUT is arguably more comprehensive (M:N categories, product options, Django models, service code). WITH is more focused on pure DB architecture. |
| Cross-Skill Ref | 1/1 | 0/1 | with | WITH ends with "관련 스킬 참조" linking to implementation-django, architecture-ddd, and architecture-api. WITHOUT has none. |
| Differentiation | 1/1 | 0/1 | with | WITH provides named pattern references (Adjacency List), formal normalization analysis table, B+Tree optimization rationale for index ordering, and partial index concept (`WHERE status = 'active'`). WITHOUT provides more implementation depth but less architectural reference knowledge. |
| **Total** | **5/5** | **1/5** | **WIN** | |

---

## 3. architecture-implementation-patterns

### Analysis

**WITH skill** (`impl-patterns-with.md`): Starts with complexity assessment ("not simple CRUD, hexagonal architecture is appropriate"). States dependency direction rule explicitly ("all source code dependencies point inward, domain owns ports"). Clean directory structure with driving/driven port separation. Inbound ports split into Command and Query (CQS principle, explicitly named). Outbound ports described with design intent: "aggregate-level, not table-level" for repository, "domain intent not technical operations" for naming. Adapter examples for both inbound (REST) and outbound (Postgres, Stripe). Composition root for DI. Full port/adapter mapping table with "replaceable alternatives". Ends with cross-skill references.

**WITHOUT skill** (`impl-patterns-without.md`): Very extensive implementation. Full domain model with Order aggregate root including state machine (confirm, mark_as_paid, cancel), domain events (OrderCreatedEvent, OrderCancelledEvent, OrderStatusChangedEvent), pull_domain_events pattern. Inbound ports split into Command/Query with frozen dataclass commands. Outbound ports with ABC. Full application service with 7-step orchestration. REST controller, ORM adapter with mapper pattern, payment adapter. Very thorough but ~900 lines.

| Criterion | With | Without | Winner | Reasoning |
|-----------|------|---------|--------|-----------|
| Reference Knowledge | 1/1 | 0/1 | with | WITH explicitly names: "hexagonal architecture (ports & adapters)", "dependency inversion (domain owns ports)", CQS principle for command/query split, "aggregate-level repository (not table-level)", "domain intent naming (charge, not http_post)". It states the core asymmetry: "inbound adapters CALL ports, outbound adapters IMPLEMENT ports". WITHOUT implements hexagonal architecture correctly but does not articulate these named principles as explicitly. |
| Mode Compliance | 1/1 | 0/1 | with | WITH follows a Design mode: complexity assessment, dependency direction, directory structure, port definitions with design intent, adapter examples, DI composition, port/adapter mapping table. WITHOUT is primarily an implementation dump without the structured design reasoning. |
| Code Quality | 1/1 | 1/1 | tie | Both produce correct hexagonal architecture code. WITHOUT is more complete (domain events, state machine, ORM mapper, external API adapter) but has a bug: `OrderApplicationService` defines `execute` twice for different commands, which would shadow the first method in Python. WITH is cleaner and more focused. |
| Cross-Skill Ref | 1/1 | 0/1 | with | WITH ends with "관련 스킬 참조" linking to architecture-ddd, architecture-db, architecture-api, implementation-django, implementation-python. WITHOUT has none. |
| Differentiation | 1/1 | 1/1 | tie | Both demonstrate substantial hexagonal architecture knowledge. WITHOUT has domain events, state machine, ORM mapper which WITH lacks. WITH has explicit design principles and the port/adapter mapping table with alternatives. Both add unique value. |
| **Total** | **5/5** | **2/5** | **WIN** | |

---

## 4. implementation-cleancode

### Analysis

**WITH skill** (`cleancode-with.md`): Uses Refactoring mode format with numbered changes, each containing [Before], [After], [Reason] blocks. Each [Reason] cites specific reference codes: `[CC 1.2]` (function does one thing), `[IP]` (value objects), `[Ref]` (Primitive Obsession, Extract Method, Guard Clause), `[GoF Strategy]`, `[OCP]`, `[CC 1.6]` (command-query separation), `[CC 1.7]` (no side effects), `[SRP]`, `[DIP]`. Uses Protocol (structural typing) instead of ABC. Uses `frozen=True` dataclass and `Final[int]` for constants. Presents complete refactored code at the end.

**WITHOUT skill** (`cleancode-without.md`): Step-by-step refactoring (6 stages). Identifies 7 problems in a table with violation principles. Uses ABC for strategy pattern instead of Protocol. Uses mutable dataclass (not frozen). Uses `field(default_factory=list)` for items. Includes test comparison section. Each step has "변경 이유" explanations but without reference codes. Uses `OrderProcessor(ABC)` with `@abstractmethod`.

| Criterion | With | Without | Winner | Reasoning |
|-----------|------|---------|--------|-----------|
| Reference Knowledge | 1/1 | 0/1 | with | WITH cites specific reference codes: `[CC 1.2]`, `[CC 1.6]`, `[CC 1.7]`, `[IP]`, `[Ref]`, `[GoF Strategy]`, `[OCP]`, `[DIP]`, `[CodeC]`. These are clearly derived from skill reference files (Clean Code chapters, Implementation Patterns, Refactoring catalog, GoF patterns). WITHOUT names principles (SRP, OCP) but does not use reference codes or cite specific sources. |
| Mode Compliance | 1/1 | 0/1 | with | WITH strictly follows Refactoring mode: numbered changes with [Before]/[After]/[Reason] format. WITHOUT uses a pedagogical step-by-step format that is well-structured but does not match a specific skill operating mode. |
| Code Quality | 1/1 | 1/1 | tie | Both produce correct refactored code. WITH uses Protocol (more Pythonic structural typing) and `frozen=True` dataclass with `Final[int]` constants. WITHOUT uses ABC and mutable dataclass. WITH's approach is arguably more idiomatic modern Python, but both are production-ready. |
| Cross-Skill Ref | 1/1 | 0/1 | with | WITH ends with "관련 스킬 참조" linking to implementation-python, testing, and architecture skills. WITHOUT has none. |
| Differentiation | 1/1 | 0/1 | with | WITH has reference codes, Protocol-based DI, frozen dataclasses, `Final` type for constants, `CompletedOrder` as a separate result type separating input from output. WITHOUT has a test comparison section and problem analysis table that WITH lacks, but WITH's reference-derived knowledge is clearly distinct. |
| **Total** | **5/5** | **1/5** | **WIN** | |

---

## 5. implementation-python

### Analysis

**WITH skill** (`python-with.md`): Pure Python code with comprehensive module docstring. Uses `frozen=True, slots=True` dataclass. Money has `add`, `subtract`, `multiply` methods with currency validation. Explicitly implements `__eq__` returning `NotImplemented`, `__hash__`, `__repr__`, `__str__`. Provides detailed explanation of WHY explicit `__eq__`/`__hash__` is defined despite `frozen=True` auto-generation (3 reasons: NotImplemented return, hash transparency, repr customization). Address uses `with_detail` pattern for immutable updates. Usage examples with set/dict key demonstrations. Ends with cross-skill references.

**WITHOUT skill** (`python-without.md`): Uses `Decimal` for Money amount (not int). Currency as `str, Enum`. Has `__post_init__` validation. Implements operator overloads (`__add__`, `__sub__`, `__mul__`, `__lt__`, `__le__`, `__gt__`, `__ge__`). Static factory methods (`Money.zero()`, `Money.won()`). Address has extensive validation in `__post_init__` (required fields, zip code format). Has `with_detail` and `with_recipient` methods. Full `__main__` usage example. Design summary table.

| Criterion | With | Without | Winner | Reasoning |
|-----------|------|---------|--------|-----------|
| Reference Knowledge | 1/1 | 0/1 | with | WITH explicitly explains the `NotImplemented` return pattern (allowing Python to try the other operand's `__eq__`), hash transparency principle, and the distinction between `__repr__` (debug) and `__str__` (user). These are specific Python convention knowledge points. WITHOUT implements similar patterns but without articulating the underlying Python protocol knowledge. |
| Mode Compliance | 1/1 | 0/1 | with | WITH presents code-first with inline explanation, following a Writing/Implementation mode. WITHOUT is more of a tutorial format with "Overview", "Design Points Summary table", and `__main__` example block. |
| Code Quality | 1/1 | 1/1 | tie | WITHOUT arguably has more robust code: Decimal for financial precision, operator overloads, __post_init__ validation, Currency enum. WITH uses int for amount (simpler but less precise for multi-currency). Both are production-ready for their respective design choices. |
| Cross-Skill Ref | 1/1 | 0/1 | with | WITH ends with "관련 스킬 참조" linking to implementation-cleancode, implementation-python (pydantic section), and testing. WITHOUT has none. |
| Differentiation | 1/1 | 1/1 | tie | Each has unique strengths. WITH has the explicit `NotImplemented` protocol explanation. WITHOUT has Decimal precision, operator overloads, factory methods, and extensive validation. Both contain knowledge the other lacks. |
| **Total** | **5/5** | **2/5** | **WIN** | |

---

## 6. implementation-tdd

### Analysis

**WITH skill** (`tdd-with.md`): Starts with a test list (checklist format). Names TDD strategies explicitly: "Fake It" (Cycle 1, 2), "Assert First" (Cycle 2), "Triangulation" (Cycle 3, forcing generalization), "Obvious Implementation" (Cycle 5), "Transformation Priority" (constant -> scalar). Uses `frozen=True` dataclass with Value Object pattern in Refactor phase. Protocol for StockService. London school approach for mocking external dependencies. Mock verification with `assert_called_once_with`. Uses pytest throughout. Class-based test organization. Ends with cross-skill references.

**WITHOUT skill** (`tdd-without.md`): Django-based TDD (TestCase, Product.objects.create). 5 cycles covering order creation, total calculation, stock exception, empty cart, stock deduction. Uses `transaction.atomic()` and `select_for_update()`. Custom `InsufficientStockError` exception. Korean test method names as documentation. Each cycle has detailed "왜 이렇게 하는가?" explanations. Includes final code summary and "핵심 교훈" section.

| Criterion | With | Without | Winner | Reasoning |
|-----------|------|---------|--------|-----------|
| Reference Knowledge | 1/1 | 0/1 | with | WITH explicitly names TDD strategies from reference material: "Fake It", "Assert First", "Triangulation", "Obvious Implementation", "Transformation Priority (constant -> scalar)", "London school approach". These are specific named techniques from TDD literature (Kent Beck's TDD By Example). WITHOUT follows Red-Green-Refactor correctly and mentions YAGNI but does not name specific TDD strategies. |
| Mode Compliance | 1/1 | 1/1 | tie | Both follow the TDD cycle format (Red-Green-Refactor) with clear cycle numbering. WITH labels each section as RED/GREEN/REFACTOR. WITHOUT does the same with Korean headers. Both comply with a Development/TDD mode. |
| Code Quality | 1/1 | 1/1 | tie | Both produce correct, well-structured code. WITHOUT includes Django ORM integration, `transaction.atomic()`, `select_for_update()` which are more production-realistic. WITH uses pure Python with Protocol and frozen dataclasses which is cleaner for unit testing. |
| Cross-Skill Ref | 1/1 | 0/1 | with | WITH ends with "관련 스킬 참조" linking to implementation-test, implementation-cleancode, and implementation-django. WITHOUT has none. |
| Differentiation | 1/1 | 0/1 | with | WITH contains named TDD strategies (Fake It, Triangulation, Assert First, Obvious Implementation, Transformation Priority) that are completely absent from WITHOUT. WITHOUT has Django-specific knowledge (select_for_update, transaction.atomic) and Korean test names as documentation, but these are general Django/testing practices, not TDD-reference-specific knowledge. |
| **Total** | **5/5** | **2/5** | **WIN** | |

---

## Summary

| Skill | With | Without | Result |
|-------|------|---------|--------|
| architecture-api | 5/5 | 1/5 | W |
| architecture-db | 5/5 | 1/5 | W |
| architecture-implementation-patterns | 5/5 | 2/5 | W |
| implementation-cleancode | 5/5 | 1/5 | W |
| implementation-python | 5/5 | 2/5 | W |
| implementation-tdd | 5/5 | 2/5 | W |
| **Average** | **5.0/5** | **1.5/5** | **6W-0L-0T** |

## Key Observations

1. **Cross-Skill Reference is a binary differentiator**: Every WITH version includes a "관련 스킬 참조" closing section; no WITHOUT version does. This is a guaranteed 1-point advantage per skill.

2. **Reference Knowledge is the strongest differentiator**: WITH versions consistently cite named patterns, principles, and reference codes (RFC 9457, Adjacency List, `[CC 1.2]`, Fake It, Triangulation) that are clearly derived from skill reference files. WITHOUT versions apply similar principles but without naming or citing them.

3. **Mode Compliance is consistently better in WITH**: WITH versions follow structured skill operating modes (Design mode, Refactoring mode with [Before]/[After]/[Reason]). WITHOUT versions tend toward tutorial-style or implementation-dump formats.

4. **Code Quality is generally a tie**: WITHOUT versions often produce more comprehensive implementations (more tables, more Django code, more operator overloads). The quality of the code itself is comparable in both groups.

5. **WITHOUT versions have unique strengths**: Django model implementations, state machine diagrams, operator overloads, extensive validation, test comparison sections. These are valuable but fall outside the rubric's focus on skill-reference-derived knowledge.
