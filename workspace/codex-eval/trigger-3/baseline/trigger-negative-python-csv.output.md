아래는 CSV 파일에서 중복 이메일을 찾는 독립 실행형 Python 스크립트입니다.

```python
#!/usr/bin/env python3
import argparse
import csv
from collections import defaultdict


def normalize_email(email: str) -> str:
    return email.strip().lower()


def find_duplicate_emails(csv_path: str, email_column: str):
    emails = defaultdict(list)

    with open(csv_path, newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        if email_column not in reader.fieldnames:
            raise ValueError(f"CSV에 '{email_column}' 컬럼이 없습니다.")

        for row_number, row in enumerate(reader, start=2):
            email = normalize_email(row.get(email_column, ""))

            if email:
                emails[email].append(row_number)

    return {
        email: rows
        for email, rows in emails.items()
        if len(rows) > 1
    }


def main():
    parser = argparse.ArgumentParser(
        description="CSV 파일에서 중복 이메일을 찾습니다."
    )
    parser.add_argument("csv_file", help="읽을 CSV 파일 경로")
    parser.add_argument(
        "--column",
        default="email",
        help="이메일 컬럼명. 기본값: email",
    )

    args = parser.parse_args()

    duplicates = find_duplicate_emails(args.csv_file, args.column)

    if not duplicates:
        print("중복 이메일이 없습니다.")
        return

    print("중복 이메일:")
    for email, rows in duplicates.items():
        print(f"- {email}: rows {', '.join(map(str, rows))}")


if __name__ == "__main__":
    main()
```

사용 예시:

```bash
python find_duplicates.py users.csv
python find_duplicates.py users.csv --column Email
```

이메일은 앞뒤 공백을 제거하고 소문자로 바꿔 비교합니다. 예를 들어 `Test@Example.com`과 `test@example.com`은 같은 이메일로 처리됩니다.