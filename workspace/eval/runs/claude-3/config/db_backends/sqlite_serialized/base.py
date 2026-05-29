"""직렬화 SQLite 백엔드 (명세 §3.3·§4.3).

개발/테스트 SQLite 의 동시성 데드락(`database is locked`)을 회피하기 위해
명세 §3.3 이 결정한 연결 설정을 집행한다(값·모드는 명세가 결정, 구체 코드만 여기서):

- busy_timeout 하한 5000ms(5초): 쓰기 락 경합 시 즉시 실패하지 않고 대기.
- begin 모드 IMMEDIATE: 쓰기 트랜잭션 시작 시 즉시 RESERVED lock 을 잡아
  DEFERRED 의 SELECT→UPDATE 락 승격 데드락을 회피한다.

Django 4.2 의 기본 sqlite3 백엔드는 DEFERRED `BEGIN` 을 쓰고 transaction_mode
OPTION(5.1+)이 없으므로, 백엔드를 서브클래싱해 두 설정을 적용한다.
"""
from django.db.backends.sqlite3 import base as sqlite3_base

_BUSY_TIMEOUT_MS = 5000


class DatabaseWrapper(sqlite3_base.DatabaseWrapper):
    def get_new_connection(self, conn_params: dict) -> object:
        conn = super().get_new_connection(conn_params)
        conn.execute(f"PRAGMA busy_timeout = {_BUSY_TIMEOUT_MS}")
        return conn

    def _start_transaction_under_autocommit(self) -> None:
        """쓰기 트랜잭션을 IMMEDIATE 모드로 시작한다(즉시 RESERVED lock)."""
        self.cursor().execute("BEGIN IMMEDIATE")
