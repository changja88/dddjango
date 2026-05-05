.PHONY: release test-release

# 플러그인 버전을 올리고, 검증/커밋/태그 생성 후 현재 브랜치와 태그를 origin에 push한다.
release:
	python3 scripts/release.py

# 릴리즈 자동화와 스킬 mirror 동기화 회귀 테스트를 실행한다.
test-release:
	python3 -m unittest discover -s tests
