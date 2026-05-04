표준 라이브러리만 쓰는 간단한 ASCII slugify 함수입니다. 공백/구두점은 `-`로 합치고, 앞뒤 `-`는 제거하며, 영문은 소문자로 바꿉니다.

```rust
pub fn slugify(input: &str) -> String {
    let mut slug = String::new();
    let mut last_was_dash = false;

    for ch in input.chars() {
        if ch.is_ascii_alphanumeric() {
            slug.push(ch.to_ascii_lowercase());
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
    fn collapses_multiple_separators() {
        assert_eq!(slugify("Rust   slugify___test"), "rust-slugify-test");
    }

    #[test]
    fn trims_leading_and_trailing_separators() {
        assert_eq!(slugify("  --Hello Rust!--  "), "hello-rust");
    }

    #[test]
    fn keeps_numbers() {
        assert_eq!(slugify("Post 123: Rust 2026"), "post-123-rust-2026");
    }

    #[test]
    fn drops_non_ascii_characters() {
        assert_eq!(slugify("안녕 Rust"), "rust");
    }
}
```

사용 예:

```rust
fn main() {
    let slug = slugify("Hello, Rust World!");
    println!("{slug}"); // hello-rust-world
}
```

한글이나 악센트 문자를 `annyeong`, `cafe`처럼 변환해야 한다면 표준 라이브러리만으로는 부족하고 `deunicode` 같은 crate를 붙이는 쪽이 낫습니다.