#!/bin/bash
S=/private/tmp/claude-501/-Users-hyun-Desktop-dddjango/d31bf8ef-f45e-4609-badc-3add1039bdb0/scratchpad/fr3
P='(dict|Dict|Mapping|MutableMapping)\[[^]]*, *(object|Any)\]'
for d in spring-c20f525 spring kkebi; do
  cd $S/$d
  roots=(framework application); [ -d spring_dream_server ] && roots+=(spring_dream_server); [ -d kkebi_server ] && roots+=(kkebi_server); [ -d web ] && roots+=(web)
  echo "=== $d roots=[${roots[*]}]"
  echo "-- broadened (non-test):"; grep -rnE --include='*.py' "$P" "${roots[@]}" | grep -v /test/ | wc -l
  echo "-- broadened by root:"; grep -rnE --include='*.py' "$P" "${roots[@]}" | grep -v /test/ | awk -F/ '{print $1}' | sort | uniq -c
  echo "-- broadened application BC:"; grep -rnE --include='*.py' "$P" application | grep -v /test/ | awk -F/ '{print $2}' | sort | uniq -c | sort -rn | tr '\n' ';'; echo
  echo "-- key not str (broadened minus str-key):"; grep -rnE --include='*.py' "$P" "${roots[@]}" | grep -v /test/ | grep -vE '(dict|Dict|Mapping|MutableMapping)\[str, *(object|Any)\]' | wc -l
  echo "-- key-not-str samples:"; grep -rnoE --include='*.py' "$P" "${roots[@]}" | grep -v /test/ | grep -vE '\[str, *(object|Any)\]' | awk -F: '{print $3}' | sort | uniq -c | sort -rn | head -12
  echo "-- nested list[dict[str, Any|object]]:"; grep -rnE --include='*.py' 'list\[(dict|Mapping)\[str, *(object|Any)\]\]' "${roots[@]}" | grep -v /test/ | wc -l
  echo "-- other containers nested:"; grep -rnE --include='*.py' '(Sequence|Iterable|Iterator|tuple|set|frozenset|Optional|Callable)\[[^]]*(dict|Mapping)\[str, *(object|Any)\]' "${roots[@]}" | grep -v /test/ | wc -l
  echo "-- object vs Any split (occurrences):"; grep -rnoE --include='*.py' "$P" "${roots[@]}" | grep -v /test/ | grep -oE '(object|Any)\]$' | sort | uniq -c
  echo "-- dict/Dict/Mapping/MutableMapping split (occurrences):"; grep -rnoE --include='*.py' "$P" "${roots[@]}" | grep -v /test/ | grep -oE ':(dict|Dict|Mapping|MutableMapping)\[' | sort | uniq -c
  echo "-- test-dir lines (for reference):"; grep -rnE --include='*.py' "$P" "${roots[@]}" | grep /test/ | wc -l
  echo "-- occurrences (not lines):"; grep -rnoE --include='*.py' "$P" "${roots[@]}" | grep -v /test/ | wc -l
  echo "-- reporter cmd but all roots:"; grep -rnE --include='*.py' '(dict|Mapping)\[str, (object|Any)\]' "${roots[@]}" | grep -v /test/ | wc -l
done
