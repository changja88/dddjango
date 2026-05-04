현재 디렉터리가 비어 있고 읽기 전용이라 파일에는 반영하지 못했습니다. 아래는 의존성 없는 Rust `slugify` 함수입니다.

```rust
pub fn slugify(input: &str) -> String {
    let mut slug = String::new();
    let mut pending_dash = false;

    for ch in input.chars() {
        if ch.is_ascii_alphanumeric() {
            if pending_dash && !slug.is_empty() {
                slug.push('-');
            }
            slug.push(ch.to_ascii_lowercase());
            pending_dash = false;
        } else if !slug.is_empty() {
            pending_dash = true;
        }
    }

    slug
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn slugifies_basic_strings() {
        assert_eq!(slugify("Hello, World!"), "hello-world");
        assert_eq!(slugify("  Rust___Slugify  "), "rust-slugify");
        assert_eq!(slugify("A--B--C"), "a-b-c");
        assert_eq!(slugify("Already slugified"), "already-slugified");
    }

    #[test]
    fn skips_non_ascii_chars() {
        assert_eq!(slugify("안녕 Rust"), "rust");
        assert_eq!(slugify("café au lait"), "caf-au-lait");
    }
}
```

이 버전은 ASCII 영문/숫자만 남기고, 나머지 문자는 구분자로 취급해서 중복 `-`를 하나로 합칩니다. Unicode 음역이 필요하면 `deunicode` 같은 crate를 쓰는 쪽이 맞습니다.