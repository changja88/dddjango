아래 스크립트를 `find_duplicate_emails.py`로 저장해서 쓰면 됩니다.

```python
#!/usr/bin/env python3
import argparse
import csv
from collections import defaultdict


def find_duplicate_emails(csv_path, email_column):
    emails = defaultdict(list)

    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        if email_column not in reader.fieldnames:
            raise ValueError(f"CSV에 '{email_column}' 컬럼이 없습니다. 사용 가능한 컬럼: {reader.fieldnames}")

        for row_number, row in enumerate(reader, start=2):
            email = (row.get(email_column) or "").strip().lower()
            if email:
                emails[email].append(row_number)

    return {email: rows for email, rows in emails.items() if len(rows) > 1}


def main():
    parser = argparse.ArgumentParser(description="CSV 파일에서 중복 이메일을 찾습니다.")
    parser.add_argument("csv_file", help="검사할 CSV 파일 경로")
    parser.add_argument("--column", default="email", help="이메일 컬럼명. 기본값: email")
    args = parser.parse_args()

    duplicates = find_duplicate_emails(args.csv_file, args.column)

    if not duplicates:
        print("중복 이메일이 없습니다.")
        return

    print("중복 이메일:")
    for email, rows in duplicates.items():
        print(f"- {email}: {len(rows)}회, 행 번호 {rows}")


if __name__ == "__main__":
    main()
```

실행 예시:

```bash
python find_duplicate_emails.py users.csv
python find_duplicate_emails.py users.csv --column 이메일
```

현재 환경이 읽기 전용이라 파일은 직접 생성하지 못했습니다.