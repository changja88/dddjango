```bash
grep 'ERROR' /path/to/app.log
```

대소문자를 무시하려면:

```bash
grep -i 'ERROR' /path/to/app.log
```

실시간 로그에서 ERROR만 보려면:

```bash
tail -f /path/to/app.log | grep 'ERROR'
```