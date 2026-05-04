현재 `/private/tmp/dddjango-codex-eval`에는 Rust 프로젝트 파일이 없고, `config.toml`도 해당 경로에 없습니다. 바로 쓸 수 있는 Rust `slugify` 함수는 아래처럼 작성하면 됩니다.

```rust
pub fn slugify(input: &str) -> String {
    let mut slug = String::new();
    let mut last_was_dash = false;

    for ch in input.chars().flat_map(|c| c.to_lowercase()) {
        if ch.is_ascii_alphanumeric() {
            slug.push(ch);
            last_was_dash = false;
        } else if !last_was_dash && !slug.is_empty() {
            slug.push('-');
            last_was_dash = true;
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
        assert_eq!(slugify(" Rust --- Slugify "), "rust-slugify");
    }

    #[test]
    fn keeps_ascii_numbers() {
        assert_eq!(slugify("Post #123: Rust 2026"), "post-123-rust-2026");
    }

    #[test]
    fn drops_non_ascii_characters() {
        assert_eq!(slugify("Café déjà vu"), "caf-dj-vu");
    }
}
```

이 버전은 ASCII 알파벳/숫자만 남기고, 공백과 특수문자는 `-`로 합치며, 앞뒤 `-`를 제거합니다. Unicode 문자를 `é -> e`처럼 음역까지 처리해야 하면 `deunicode` 같은 크레이트를 쓰는 방식이 더 적합합니다.