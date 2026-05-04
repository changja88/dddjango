현재 `/private/tmp/dddjango-codex-eval` 저장소가 비어 있고 `config.toml`도 없어서 파일에 직접 추가할 위치가 없습니다. 대신 바로 사용할 수 있는 Rust `slugify` 함수는 아래처럼 작성하면 됩니다.

```rust
pub fn slugify(input: &str) -> String {
    let mut slug = String::new();
    let mut last_was_dash = false;

    for ch in input.chars().flat_map(|c| c.to_lowercase()) {
        if ch.is_ascii_alphanumeric() {
            slug.push(ch);
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
```

테스트 예시:

```rust
#[cfg(test)]
mod tests {
    use super::slugify;

    #[test]
    fn slugifies_basic_text() {
        assert_eq!(slugify("Hello, World!"), "hello-world");
    }

    #[test]
    fn collapses_separators() {
        assert_eq!(slugify(" Rust --- slugify___test "), "rust-slugify-test");
    }

    #[test]
    fn removes_non_ascii_symbols() {
        assert_eq!(slugify("Hello @#$ World"), "hello-world");
    }
}
```

주의: 이 버전은 ASCII 중심입니다. `한글`, `é`, `ü` 같은 비ASCII 문자를 보존하거나 음역하려면 `unicode-normalization` 같은 크레이트를 쓰는 방식으로 확장해야 합니다.