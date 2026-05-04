현재 디렉터리에 Rust 프로젝트 파일이 없고, 세션 권한도 읽기 전용이라 파일을 직접 만들지는 못했습니다. 아래는 바로 붙여 쓸 수 있는 Rust `slugify` 함수입니다.

```rust
pub fn slugify(input: &str) -> String {
    let mut slug = String::new();
    let mut last_was_dash = false;

    for ch in input.chars() {
        if ch.is_ascii_alphanumeric() {
            slug.push(ch.to_ascii_lowercase());
            last_was_dash = false;
        } else if ch.is_whitespace() || ch == '-' || ch == '_' {
            if !slug.is_empty() && !last_was_dash {
                slug.push('-');
                last_was_dash = true;
            }
        }
    }

    if slug.ends_with('-') {
        slug.pop();
    }

    slug
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn slugifies_basic_text() {
        assert_eq!(slugify("Hello, World!"), "hello-world");
    }

    #[test]
    fn collapses_separators() {
        assert_eq!(slugify("  Rust___Slug---Test  "), "rust-slug-test");
    }

    #[test]
    fn removes_non_ascii_chars() {
        assert_eq!(slugify("Café déjà vu!"), "caf-dj-vu");
    }

    #[test]
    fn handles_empty_result() {
        assert_eq!(slugify("!!!"), "");
    }
}
```

이 버전은 ASCII 기준입니다. 한글/악센트 문자를 음역해서 `안녕 세상` → `annyeong-sesang` 같은 결과를 원하면 `deunicode` 같은 크레이트를 쓰는 구현이 더 적합합니다.