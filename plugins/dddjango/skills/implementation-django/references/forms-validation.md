# 폼과 유효성 검증

## 폼 유효성 검증 순서 [DDoc]

Django 폼 유효성 검증은 다음 순서로 실행된다:

1. **Field.clean()** -- 각 필드의 내장 검증 + 커스텀 validators (to_python → validate → run_validators)
2. **Form.clean_\<fieldname\>()** -- 필드별 커스텀 검증
3. **Form.clean()** -- 교차 필드 검증

```python
class RegistrationForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput)

    def clean_email(self):
        """필드별 커스텀 검증."""
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email=email).exists():
            raise ValidationError("이미 등록된 이메일입니다.")
        return email

    def clean(self):
        """교차 필드 검증."""
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")
        if password and password_confirm and password != password_confirm:
            raise ValidationError("비밀번호가 일치하지 않습니다.")
        return cleaned_data
```

## ModelForm 활용 [DDoc]

```python
# 좋은 예: ModelForm으로 중복 제거
class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ["title", "body", "category"]
        # exclude 대신 fields를 명시 -- 새 필드 추가 시 실수 방지

    def clean_title(self):
        title = self.cleaned_data["title"]
        if "spam" in title.lower():
            raise ValidationError("제목에 금지어가 포함되어 있습니다.")
        return title

# 나쁜 예: fields = "__all__" 또는 exclude 사용
class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = "__all__"  # 의도치 않은 필드 노출 위험
```

- `fields`를 **명시적으로** 나열한다 -- `"__all__"`이나 `exclude`는 새 필드 추가 시 의도치 않은 노출 위험이 있다. [TSD]

## 커스텀 Validator 재사용 [DDoc]

```python
# validators.py
from django.core.validators import RegexValidator

phone_validator = RegexValidator(
    regex=r"^\+?1?\d{9,15}$",
    message="올바른 전화번호 형식이 아닙니다.",
)

# models.py
class Contact(models.Model):
    phone = models.CharField(max_length=17, validators=[phone_validator])

# forms.py -- 같은 validator 재사용
class ContactForm(forms.Form):
    phone = forms.CharField(validators=[phone_validator])
```
