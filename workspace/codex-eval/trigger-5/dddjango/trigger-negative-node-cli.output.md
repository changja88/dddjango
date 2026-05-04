현재 `/private/tmp/dddjango-codex-eval` 디렉터리가 비어 있고, 세션이 읽기 전용이라 파일을 직접 생성할 수는 없습니다. 아래 내용을 `cli-parser.js`로 만들면 바로 사용할 수 있습니다.

```js
#!/usr/bin/env node

function parseArgs(argv = process.argv.slice(2)) {
  const result = {
    _: [],
  };

  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i];

    if (arg === "--") {
      result._.push(...argv.slice(i + 1));
      break;
    }

    if (arg.startsWith("--")) {
      const [key, inlineValue] = arg.slice(2).split("=", 2);

      if (!key) continue;

      if (inlineValue !== undefined) {
        result[key] = inlineValue;
      } else if (argv[i + 1] && !argv[i + 1].startsWith("-")) {
        result[key] = argv[++i];
      } else {
        result[key] = true;
      }

      continue;
    }

    if (arg.startsWith("-") && arg.length > 1) {
      const flags = arg.slice(1);

      for (const flag of flags) {
        result[flag] = true;
      }

      continue;
    }

    result._.push(arg);
  }

  return result;
}

if (require.main === module) {
  console.log(parseArgs());
}

module.exports = { parseArgs };
```

사용 예:

```bash
node cli-parser.js --name Jane --port=3000 -abc file.txt
```

출력:

```js
{
  _: ["file.txt"],
  name: "Jane",
  port: "3000",
  a: true,
  b: true,
  c: true
}
```

지원하는 형태는 `--key value`, `--key=value`, boolean flag, short flag 묶음(`-abc`), positional argument입니다.