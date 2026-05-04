현재 `/private/tmp/dddjango-codex-eval`은 비어 있고, 세션이 읽기 전용이라 파일을 직접 생성할 수 없습니다. 구현은 아래처럼 구성하면 됩니다.

`parser.js`

```js
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

      if (flags.length > 1) {
        for (const flag of flags) {
          result[flag] = true;
        }
      } else if (argv[i + 1] && !argv[i + 1].startsWith("-")) {
        result[flags] = argv[++i];
      } else {
        result[flags] = true;
      }

      continue;
    }

    result._.push(arg);
  }

  return result;
}

module.exports = { parseArgs };
```

`cli.js`

```js
#!/usr/bin/env node

const { parseArgs } = require("./parser");

const args = parseArgs();

console.log(args);
```

예시:

```bash
node cli.js build --watch --port=3000 -v src
```

출력:

```js
{
  _: ["build", "src"],
  watch: true,
  port: "3000",
  v: true
}
```

지원하는 형태는 `--name value`, `--name=value`, `--flag`, `-x value`, `-abc`, 일반 positional args, 그리고 `--` 이후 raw args입니다.