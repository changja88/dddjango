#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("extract_subagent_trace.py")


def load_extractor():
    spec = importlib.util.spec_from_file_location("extract_subagent_trace", MODULE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ExtractSubagentTraceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.extractor = load_extractor()
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.run_dir = Path(self.tmp.name) / "run"
        self.raw = self.run_dir / "raw"
        self.raw.mkdir(parents=True)

    def write_variant(
        self,
        *,
        response: str,
        events: str = "",
        case_id: str = "case-workflow-one",
        variant: str = "with-dddjango",
    ) -> tuple[Path, Path]:
        response_path = self.raw / f"{case_id}-{variant}.txt"
        event_path = self.raw / f"{case_id}-{variant}-events.jsonl"
        response_path.write_text(response, encoding="utf-8")
        event_path.write_text(events, encoding="utf-8")
        return response_path, event_path

    def test_detect_source_kind_distinguishes_structured_events_from_transcript(self) -> None:
        event_path = self.raw / "structured.jsonl"
        event_path.write_text(
            json.dumps({"type": "tool_call", "name": "spawn_agent"}) + "\n",
            encoding="utf-8",
        )
        transcript_path = self.raw / "stdout.txt"
        transcript_path.write_text("plain stdout transcript\n", encoding="utf-8")

        self.assertEqual(self.extractor.detect_source_kind(event_path), "structured-events")
        self.assertEqual(self.extractor.detect_source_kind(transcript_path), "stdout-transcript")
        self.assertEqual(self.extractor.detect_source_kind(self.raw / "missing.jsonl"), "unavailable")

    def test_reasoning_text_mentioning_spawn_agent_is_not_structured_event(self) -> None:
        response_path, event_path = self.write_variant(
            response="실제 subagent 실행이나 파일 수정은 하지 않았습니다.\n",
            events=json.dumps(
                {
                    "type": "item.completed",
                    "item": {
                        "type": "reasoning",
                        "text": "I considered whether to call spawn_agent but decided not to.",
                    },
                }
            )
            + "\n",
        )

        summary = self.extractor.build_trace_summary(
            case_id="case-workflow-one",
            variant="with-dddjango",
            run_dir=self.run_dir,
            response_path=response_path,
            event_path=event_path,
        )

        self.assertEqual(summary["sourceKind"], "stdout-transcript")
        self.assertEqual(summary["spawnEventCount"], 0)
        self.assertEqual(summary["resultEventCount"], 0)
        self.assertEqual(summary["traceStatus"], "fallback-stated")

    def test_hypothetical_subagent_sentence_is_not_actual_claim(self) -> None:
        response_path, event_path = self.write_variant(
            response="실제 subagent를 사용했다면 trace를 남겨야 합니다.\n"
        )

        summary = self.extractor.build_trace_summary(
            case_id="case-workflow-one",
            variant="with-dddjango",
            run_dir=self.run_dir,
            response_path=response_path,
            event_path=event_path,
        )

        self.assertEqual(summary["explicitActualClaims"], [])
        self.assertEqual(summary["traceStatus"], "no-trace")

    def test_completed_agent_review_is_actual_claim(self) -> None:
        response_path, event_path = self.write_variant(
            response="Domain Agent와 DB Agent가 검토 완료했습니다.\n"
        )

        summary = self.extractor.build_trace_summary(
            case_id="case-workflow-one",
            variant="with-dddjango",
            run_dir=self.run_dir,
            response_path=response_path,
            event_path=event_path,
        )

        self.assertEqual(summary["traceCaptureReliable"], False)
        self.assertEqual(summary["traceStatus"], "claim-without-reliable-trace")
        self.assertEqual(
            summary["explicitActualClaims"],
            ["Domain Agent와 DB Agent가 검토 완료했습니다."],
        )
        self.assertIn("Domain Agent", summary["rolesMentioned"])
        self.assertIn("DB Agent", summary["rolesMentioned"])

    def test_fallback_claim_is_detected_without_actual_claim(self) -> None:
        response_path, event_path = self.write_variant(
            response="subagent는 사용하지 않고 순차 검토했습니다.\n"
        )

        summary = self.extractor.build_trace_summary(
            case_id="case-workflow-one",
            variant="with-dddjango",
            run_dir=self.run_dir,
            response_path=response_path,
            event_path=event_path,
        )

        self.assertEqual(summary["explicitActualClaims"], [])
        self.assertEqual(summary["explicitFallbackClaims"], ["subagent는 사용하지 않고 순차 검토했습니다."])
        self.assertEqual(summary["traceStatus"], "fallback-stated")

    def test_english_not_executed_fallback_claim_is_detected(self) -> None:
        response_path, event_path = self.write_variant(
            response=(
                "## Role Map\n\n"
                "Subagents were **not executed** in this read-only planning turn.\n\n"
                "## Sequential Fallback\n\n"
                "1. Domain\n"
                "2. Architecture\n"
            )
        )

        summary = self.extractor.build_trace_summary(
            case_id="case-workflow-one",
            variant="with-dddjango",
            run_dir=self.run_dir,
            response_path=response_path,
            event_path=event_path,
        )

        self.assertEqual(summary["explicitActualClaims"], [])
        self.assertEqual(
            summary["explicitFallbackClaims"],
            ["Subagents were **not executed** in this read-only planning turn."],
        )
        self.assertEqual(summary["traceStatus"], "fallback-stated")

    def test_conditional_delegation_sentence_is_not_actual_claim(self) -> None:
        response_path, event_path = self.write_variant(
            response="사용 가능하면 역할을 나누겠습니다.\n"
        )

        summary = self.extractor.build_trace_summary(
            case_id="case-workflow-one",
            variant="with-dddjango",
            run_dir=self.run_dir,
            response_path=response_path,
            event_path=event_path,
        )

        self.assertEqual(summary["explicitActualClaims"], [])
        self.assertEqual(summary["traceStatus"], "no-trace")

    def test_planned_role_table_with_transaction_is_not_actual_claim(self) -> None:
        response_path, event_path = self.write_variant(
            response=(
                "승인해주면 실제 subagent 실행은 아래 역할로 나누겠습니다.\n\n"
                "| 역할 | 왜 필요한가 |\n"
                "|---|---|\n"
                "| Django Agent | ORM/service 구현 위치, `transaction.atomic`, `on_commit`, "
                "외부 결제 호출 타이밍 검토 |\n"
                "\n이 역할 분해로 실제 subagent 검토를 실행해도 될까요?\n"
            )
        )

        summary = self.extractor.build_trace_summary(
            case_id="case-workflow-one",
            variant="with-dddjango",
            run_dir=self.run_dir,
            response_path=response_path,
            event_path=event_path,
        )

        self.assertEqual(summary["explicitActualClaims"], [])
        self.assertEqual(summary["traceStatus"], "no-trace")
        self.assertIn("Django Agent", summary["rolesMentioned"])

    def test_stderr_text_is_never_used_for_claims_or_roles(self) -> None:
        response_path, event_path = self.write_variant(response="최종 응답입니다.\n")
        stderr_path = self.raw / "case-workflow-one-with-dddjango.stderr.txt"
        stderr_path.write_text("Domain Agent와 DB Agent가 검토 완료했습니다.\n", encoding="utf-8")

        summary = self.extractor.build_trace_summary(
            case_id="case-workflow-one",
            variant="with-dddjango",
            run_dir=self.run_dir,
            response_path=response_path,
            event_path=event_path,
        )

        self.assertEqual(summary["explicitActualClaims"], [])
        self.assertEqual(summary["rolesMentioned"], [])

    def test_structured_events_make_trace_reliable_and_count_tool_calls(self) -> None:
        response_path, event_path = self.write_variant(
            response="Domain Agent가 검토 완료했습니다.\n",
            events="\n".join(
                [
                    json.dumps({"type": "tool_call", "name": "spawn_agent", "role": "Domain Agent"}),
                    json.dumps({"type": "tool_call", "name": "wait_agent", "role": "Domain Agent"}),
                ]
            )
            + "\n",
        )

        summary = self.extractor.build_trace_summary(
            case_id="case-workflow-one",
            variant="with-dddjango",
            run_dir=self.run_dir,
            response_path=response_path,
            event_path=event_path,
        )

        self.assertEqual(summary["sourceKind"], "structured-events")
        self.assertEqual(summary["traceCaptureReliable"], True)
        self.assertEqual(summary["spawnEventCount"], 1)
        self.assertEqual(summary["waitEventCount"], 1)
        self.assertEqual(summary["resultEventCount"], 1)
        self.assertEqual(summary["traceStatus"], "actual-trace")

    def test_started_and_completed_events_for_same_tool_call_count_once(self) -> None:
        response_path, event_path = self.write_variant(
            response="Domain Agent가 검토 완료했습니다.\n",
            events="\n".join(
                [
                    json.dumps(
                        {
                            "type": "item.started",
                            "item": {"id": "item_1", "type": "collab_tool_call", "tool": "spawn_agent"},
                        }
                    ),
                    json.dumps(
                        {
                            "type": "item.completed",
                            "item": {"id": "item_1", "type": "collab_tool_call", "tool": "spawn_agent"},
                        }
                    ),
                    json.dumps(
                        {
                            "type": "item.started",
                            "item": {"id": "item_2", "type": "collab_tool_call", "tool": "wait_agent"},
                        }
                    ),
                    json.dumps(
                        {
                            "type": "item.completed",
                            "item": {"id": "item_2", "type": "collab_tool_call", "tool": "wait_agent"},
                        }
                    ),
                ]
            )
            + "\n",
        )

        summary = self.extractor.build_trace_summary(
            case_id="case-workflow-one",
            variant="with-dddjango",
            run_dir=self.run_dir,
            response_path=response_path,
            event_path=event_path,
        )

        self.assertEqual(summary["spawnEventCount"], 1)
        self.assertEqual(summary["waitEventCount"], 1)
        self.assertEqual(summary["resultEventCount"], 1)
        self.assertEqual(summary["traceStatus"], "actual-trace")

    def test_codex_wait_tool_counts_as_result_collection(self) -> None:
        response_path, event_path = self.write_variant(
            response="Domain Agent가 검토 완료했습니다.\n",
            events="\n".join(
                [
                    json.dumps(
                        {
                            "type": "item.completed",
                            "item": {"id": "item_1", "type": "collab_tool_call", "tool": "spawn_agent"},
                        }
                    ),
                    json.dumps(
                        {
                            "type": "item.completed",
                            "item": {"id": "item_2", "type": "collab_tool_call", "tool": "wait"},
                        }
                    ),
                ]
            )
            + "\n",
        )

        summary = self.extractor.build_trace_summary(
            case_id="case-workflow-one",
            variant="with-dddjango",
            run_dir=self.run_dir,
            response_path=response_path,
            event_path=event_path,
        )

        self.assertEqual(summary["spawnEventCount"], 1)
        self.assertEqual(summary["waitEventCount"], 1)
        self.assertEqual(summary["resultEventCount"], 1)
        self.assertEqual(summary["traceStatus"], "actual-trace")

    def test_close_agent_counts_as_result_collection(self) -> None:
        response_path, event_path = self.write_variant(
            response="Domain Agent가 검토 완료했습니다.\n",
            events="\n".join(
                [
                    json.dumps({"type": "tool_call", "name": "spawn_agent", "role": "Domain Agent"}),
                    json.dumps({"type": "tool_call", "name": "close_agent", "role": "Domain Agent"}),
                ]
            )
            + "\n",
        )

        summary = self.extractor.build_trace_summary(
            case_id="case-workflow-one",
            variant="with-dddjango",
            run_dir=self.run_dir,
            response_path=response_path,
            event_path=event_path,
        )

        self.assertEqual(summary["spawnEventCount"], 1)
        self.assertEqual(summary["waitEventCount"], 0)
        self.assertEqual(summary["resultEventCount"], 1)
        self.assertEqual(summary["traceStatus"], "actual-trace")

    def test_spawn_without_result_collection_is_incomplete_trace(self) -> None:
        response_path, event_path = self.write_variant(
            response="Domain Agent가 검토 완료했습니다.\n",
            events=json.dumps({"type": "tool_call", "name": "spawn_agent", "role": "Domain Agent"})
            + "\n",
        )

        summary = self.extractor.build_trace_summary(
            case_id="case-workflow-one",
            variant="with-dddjango",
            run_dir=self.run_dir,
            response_path=response_path,
            event_path=event_path,
        )

        self.assertEqual(summary["spawnEventCount"], 1)
        self.assertEqual(summary["resultEventCount"], 0)
        self.assertEqual(summary["traceStatus"], "actual-trace-incomplete")

    def test_skipped_trace_status(self) -> None:
        response_path, event_path = self.write_variant(response="NOT RUN: --skip-exec was used.\n")

        summary = self.extractor.build_trace_summary(
            case_id="case-workflow-one",
            variant="with-dddjango",
            run_dir=self.run_dir,
            response_path=response_path,
            event_path=event_path,
            skipped=True,
        )

        self.assertEqual(summary["traceStatus"], "skipped")
        self.assertEqual(summary["traceCaptureReliable"], False)


if __name__ == "__main__":
    unittest.main()
