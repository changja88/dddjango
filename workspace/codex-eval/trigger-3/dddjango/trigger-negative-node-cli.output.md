현재 세션이 read-only라 파일 생성은 차단되었습니다. 아래 내용을 `cli-parser.js`로 만들면 바로 실행할 수 있습니다.

```js
#!/usr/bin/env node

function parseArgs(argv = process.argv.slice(2)) {
  const options = {};
  const positionals = [];

  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];

    if (arg === '--') {
      positionals.push(...argv.slice(i + 1));
      break;
    }

    if (arg.startsWith('--')) {
      const [name, inlineValue] = arg.slice(2).split(/=(.*)/s, 2);

      if (!name) throw new Error(`Invalid option: ${arg}`);

      if (inlineValue !== undefined) {
        options[name] = coerceValue(inlineValue);
      } else if (argv[i + 1] !== undefined && !argv[i + 1].startsWith('-')) {
        options[name] = coerceValue(argv[i + 1]);
        i += 1;
      } else {
        options[name] = true;
      }

      continue;
    }

    if (arg.startsWith('-') && arg.length > 1) {
      const flags = arg.slice(1);

      if (flags.length > 1) {
        for (const flag of flags) options[flag] = true;
      } else if (argv[i + 1] !== undefined && !argv[i + 1].startsWith('-')) {
        options[flags] = coerceValue(argv[i + 1]);
        i += 1;
      } else {
        options[flags] = true;
      }

      continue;
    }

    positionals.push(arg);
  }

  return { options, positionals };
}

function coerceValue(value) {
  if (value === 'true') return true;
  if (value === 'false') return false;
  if (value !== '' && Number.isFinite(Number(value))) return Number(value);
  return value;
}

if (require.main === module) {
  console.log(JSON.stringify(parseArgs(), null, 2));
}

module.exports = { parseArgs };
```

사용 예:

```bash
node cli-parser.js build --env=prod --watch -abc --port 3000 src
```

출력:

```json
{
  "options": {
    "env": "prod",
    "watch": true,
    "a": true,
    "b": true,
    "c": true,
    "port": 3000
  },
  "positionals": ["build", "src"]
}
```