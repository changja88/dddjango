현재 워크스페이스가 `read-only`라서 파일을 직접 생성할 수는 없습니다. 아래 내용을 예를 들어 `find_duplicate_emails.py`로 저장해서 사용하면 됩니다.

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
            raise ValueError(f"CSV에 '{email_column}' 컬럼이 없습니다. 사용 가능 컬럼: {reader.fieldnames}")

        for row_number, row in enumerate(reader, start=2):
            email = normalize_email(row.get(email_column, ""))

            if email:
                emails[email].append(row_number)

    return {email: rows for email, rows in emails.items() if len(rows) > 1}


def main():
    parser = argparse.ArgumentParser(description="CSV 파일에서 중복 이메일을 찾습니다.")
    parser.add_argument("csv_file", help="읽을 CSV 파일 경로")
    parser.add_argument(
        "--email-column",
        default="email",
        help="이메일 컬럼명. 기본값: email",
    )

    args = parser.parse_args()

    duplicates = find_duplicate_emails(args.csv_file, args.email_column)

    if not duplicates:
        print("중복 이메일이 없습니다.")
        return

    print("중복 이메일:")
    for email, rows in duplicates.items():
        print(f"- {email}: rows {', '.join(map(str, rows))}")


if __name__ == "__main__":
    main()
```

실행 예시:

```bash
python find_duplicate_emails.py users.csv
python find_duplicate_emails.py users.csv --email-column Email
```

이메일은 앞뒤 공백을 제거하고 대소문자를 구분하지 않도록 비교합니다.