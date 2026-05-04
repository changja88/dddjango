로그 파일에서 `ERROR`가 들어간 라인만 보려면:

```bash
grep 'ERROR' app.log
```

대소문자 구분 없이 찾으려면:

```bash
grep -i 'ERROR' app.log
```

결과를 파일로 저장하려면:

```bash
grep 'ERROR' app.log > errors.log
```