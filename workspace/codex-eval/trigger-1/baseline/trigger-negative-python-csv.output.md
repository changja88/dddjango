현재 디렉터리에 `config.toml`이나 기존 파일이 없고, 세션이 읽기 전용이라 파일 생성은 못 했습니다. 아래 내용을 `find_duplicate_emails.py`로 저장해서 쓰면 됩니다.

```python
#!/usr/bin/env python3
import argparse
import csv
from collections import defaultdict


def normalize_email(email: str) -> str:
    return email.strip().lower()


def find_duplicates(csv_path: str, email_column: str):
    emails = defaultdict(list)

    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        if email_column not in reader.fieldnames:
            raise ValueError(f"CSV에 '{email_column}' 컬럼이 없습니다. 컬럼: {reader.fieldnames}")

        for row_number, row in enumerate(reader, start=2):
            email = normalize_email(row.get(email_column, ""))

            if email:
                emails[email].append(row_number)

    return {email: rows for email, rows in emails.items() if len(rows) > 1}


def main():
    parser = argparse.ArgumentParser(description="CSV 파일에서 중복 이메일을 찾습니다.")
    parser.add_argument("csv_file", help="읽을 CSV 파일 경로")
    parser.add_argument(
        "-c",
        "--column",
        default="email",
        help="이메일 컬럼명. 기본값: email",
    )

    args = parser.parse_args()

    duplicates = find_duplicates(args.csv_file, args.column)

    if not duplicates:
        print("중복 이메일이 없습니다.")
        return

    print("중복 이메일:")
    for email, rows in sorted(duplicates.items()):
        print(f"- {email}: 행 {', '.join(map(str, rows))}")


if __name__ == "__main__":
    main()
```

사용 예시:

```bash
python find_duplicate_emails.py users.csv
python find_duplicate_emails.py users.csv --column Email
```

이메일은 앞뒤 공백을 제거하고 대소문자를 구분하지 않도록 소문자로 비교합니다.