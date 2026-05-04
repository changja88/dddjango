현재 작업 디렉터리가 비어 있고, 세션이 `read-only`라 파일 생성은 차단됐습니다. 아래 내용을 `cli-args.js`로 두면 바로 실행 가능한 간단한 Node.js CLI argument parser입니다.

```js
#!/usr/bin/env node
'use strict';

function parseArgs(argv = process.argv.slice(2)) {
  const result = { _: [] };

  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];

    if (arg === '--') {
      result._.push(...argv.slice(i + 1));
      break;
    }

    if (arg.startsWith('--')) {
      const raw = arg.slice(2);
      const equalIndex = raw.indexOf('=');

      if (equalIndex !== -1) {
        setValue(result, raw.slice(0, equalIndex), raw.slice(equalIndex + 1));
        continue;
      }

      const next = argv[i + 1];
      if (next !== undefined && !next.startsWith('-')) {
        setValue(result, raw, next);
        i += 1;
      } else {
        setValue(result, raw, true);
      }
      continue;
    }

    if (arg.startsWith('-') && arg.length > 1) {
      for (const flag of arg.slice(1)) setValue(result, flag, true);
      continue;
    }

    result._.push(arg);
  }

  return result;
}

function setValue(target, key, value) {
  if (!key) return;

  if (target[key] === undefined) {
    target[key] = value;
  } else if (Array.isArray(target[key])) {
    target[key].push(value);
  } else {
    target[key] = [target[key], value];
  }
}

if (require.main === module) {
  console.log(JSON.stringify(parseArgs(), null, 2));
}

module.exports = parseArgs;
```

사용 예:

```bash
node cli-args.js --name kim --count=3 -abc file.txt -- --literal
```

결과:

```json
{
  "_": ["file.txt", "--literal"],
  "name": "kim",
  "count": "3",
  "a": true,
  "b": true,
  "c": true
}
```