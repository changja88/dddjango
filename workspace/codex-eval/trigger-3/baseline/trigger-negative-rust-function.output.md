작업 디렉터리가 비어 있고 현재 세션이 `read-only`라 파일 생성은 못 했습니다. 아래 Rust 함수로 쓰면 됩니다.

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
    fn slugifies_basic_strings() {
        assert_eq!(slugify("Hello, World!"), "hello-world");
        assert_eq!(slugify("  Rust   is great  "), "rust-is-great");
        assert_eq!(slugify("foo_bar baz"), "foo-bar-baz");
        assert_eq!(slugify("Already-Slugified"), "already-slugified");
        assert_eq!(slugify("!!!"), "");
    }
}
```

이 버전은 ASCII 영문/숫자만 남기고, 나머지 문자는 `-`로 합치며 앞뒤 `-`를 제거합니다.