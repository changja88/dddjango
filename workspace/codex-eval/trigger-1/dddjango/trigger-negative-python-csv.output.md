## [주요 내용]

현재 작업공간이 read-only라 파일을 직접 만들지는 않고, 바로 사용할 수 있는 독립 실행 스크립트로 제공합니다. 기본 이메일 컬럼명은 `email`이고, 대소문자와 앞뒤 공백은 무시해서 중복을 찾습니다.

```python
#!/usr/bin/env python3
"""CSV 파일에서 중복 이메일을 찾아 출력하는 CLI 스크립트."""

import argparse
import csv
from collections import defaultdict
from pathlib import Path


type DuplicateEmailRows = dict[str, list[int]]


class DuplicateEmailFinderError(Exception):
    """중복 이메일 탐색 중 발생하는 최상위 예외."""


class EmailColumnNotFoundError(DuplicateEmailFinderError):
    """CSV 파일에 이메일 컬럼이 없을 때 발생하는 예외."""


def normalize_email(email: str) -> str:
    """비교 가능한 이메일 문자열로 정규화한다."""
    return email.strip().lower()


def find_duplicate_emails(csv_path: Path, email_column: str = "email") -> DuplicateEmailRows:
    """CSV 파일에서 중복 이메일과 해당 행 번호를 반환한다.

    행 번호는 헤더를 1행으로 보았을 때의 CSV 파일 실제 행 번호다.

    Raises:
        EmailColumnNotFoundError: 이메일 컬럼이 CSV 헤더에 없을 때.
    """
    email_rows: dict[str, list[int]] = defaultdict(list)

    with csv_path.open(newline="", encoding="utf-8-sig") as csv_file:
        reader = csv.DictReader(csv_file)

        if reader.fieldnames is None or email_column not in reader.fieldnames:
            raise EmailColumnNotFoundError(f"CSV에 '{email_column}' 컬럼이 없습니다.")

        for row_number, row in enumerate(reader, start=2):
            email = normalize_email(row.get(email_column, ""))
            if email:
                email_rows[email].append(row_number)

    return {
        email: rows
        for email, rows in email_rows.items()
        if len(rows) > 1
    }


def print_duplicate_emails(duplicate_emails: DuplicateEmailRows) -> None:
    """중복 이메일 목록을 표준 출력에 표시한다."""
    if not duplicate_emails:
        print("중복 이메일이 없습니다.")
        return

    for email, rows in sorted(duplicate_emails.items()):
        row_text = ", ".join(str(row) for row in rows)
        print(f"{email}: rows {row_text}")


def parse_args() -> argparse.Namespace:
    """CLI 인자를 파싱한다."""
    parser = argparse.ArgumentParser(description="CSV 파일에서 중복 이메일을 찾습니다.")
    parser.add_argument("csv_path", type=Path, help="검사할 CSV 파일 경로")
    parser.add_argument(
        "--email-column",
        default="email",
        help="이메일 컬럼명. 기본값: email",
    )
    return parser.parse_args()


def main() -> None:
    """중복 이메일 탐색 CLI를 실행한다."""
    args = parse_args()

    try:
        duplicate_emails = find_duplicate_emails(
            csv_path=args.csv_path,
            email_column=args.email_column,
        )
    except DuplicateEmailFinderError as error:
        raise SystemExit(f"오류: {error}") from error

    print_duplicate_emails(duplicate_emails)


if __name__ == "__main__":
    main()
```

실행 예시는 다음과 같습니다.

```bash
python find_duplicate_emails.py users.csv
python find_duplicate_emails.py users.csv --email-column Email
```

Python 3.12+ 기준으로 `type DuplicateEmailRows = ...` 타입 별칭 문법을 사용했습니다. Python 3.11 이하에서 실행해야 한다면 그 줄을 `DuplicateEmailRows = dict[str, list[int]]`로 바꾸면 됩니다.

## [관련 스킬 참조]

---
> **관련 스킬 참조:**
> - Python 스크립트 작성 관례 → **implementation-python** 스킬
> - 함수 분리와 네이밍 → **implementation-cleancode** 스킬