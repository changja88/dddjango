# R8-I2 변이 가드 — 기대 결과

대상 173(i2 81 · review 67 · impl 23 · fixture 2) · 변이체 22 · 검사기 오류 0 []

## 1. 변이 전 검사기 — 기대(ideal)와 다른 대상

`~` = 받아들인 차이(fc = fail-closed red · lim = 문서화 한계 green) · `✗` = 기대와 다름

- ~ [i2] H16_recursive_fc (기대 fc · exit 2)
- ~ [i2] H17_inherited_fc (기대 fc · exit 2)
- ~ [i2] H18_dict_values_fc (기대 fc · exit 2)
- ~ [i2] H19_copy_ctor_lim (기대 lim · exit 0)
- ~ [i2] H23_module_monkeypatch_lim (기대 lim · exit 0)
- ~ [review] RC4_vars_splat (기대 lim · exit 0)
- ~ [review] RC5_asdict (기대 lim · exit 0)
- ~ [review] RC6_shared_dict (기대 lim · exit 0)
- ✗ [review] RA10_eq_grabber (기대 red · exit 0)
- ~ [review] RN2_same_name_archive_clone (기대 lim · exit 0)
- ~ [review] GU2_super_fresh (기대 fc · exit 2)
- ~ [review] GU3_nested_generator_helper (기대 fc · exit 2)
- ~ [review] GC1_callsite_enumerate (기대 fc · exit 2)
- ~ [review] GC2_callsite_zip (기대 fc · exit 2)
- ~ [review] GC3_callsite_sorted (기대 fc · exit 2)
- ~ [review] RK5_metaclass_via_base (기대 lim · exit 0)
- ~ [review] RK6_base_new (기대 lim · exit 0)
- ~ [review] RK7_class_decorator (기대 lim · exit 0)
- ~ [review] G03_dict_values (기대 fc · exit 2)
- ~ [review] G05_map_factory (기대 fc · exit 2)
- ~ [review] G07_loop_over_proven (기대 fc · exit 2)
- ~ [review] G11_copy_method (기대 fc · exit 2)
- ~ [review] G18_local_alias_factory (기대 fc · exit 2)
- ~ [impl] N1_noarg_class_stash (기대 lim · exit 0)
- ~ [impl] N2_noarg_module_list (기대 lim · exit 0)
- ~ [impl] N3_noarg_default_param (기대 lim · exit 0)
- ~ [impl] N4_noarg_prebuilt (기대 lim · exit 0)
- ~ [impl] N5_noarg_functools_cache (기대 lim · exit 0)
- ~ [impl] S7_sorted_kwsplat (기대 fc · exit 2)
- ~ [impl] R4_reversed_named_reused (기대 fc · exit 2)

합계: ok 143 · ~ 29 · ✗ 1

## 2. 변이체별 판정이 바뀐 대상

| 변이체 | 뗀 조건 | 판정이 바뀐 탐침(→ exit) | bad_rules 발견 줄 수(사라진 참양성) |
|---|---|---|---|
| MUT-P1 | 인자 있는 호출의 본문 증명 요구 탈락(선언만으로 전파) | H16_recursive_fc→0, H18_dict_values_fc→0, B1_acc_seeded_from_arg→0, B2_extend_arg→0, B3_loop_append_arg→0, B4_identity_append→0, B5_helper_fills_acc→0, B6_branch_returns_arg→0, B7_ifexp_arg_elem→0, B8_cls_rebound→0, B8b_comprehension_rebinds_cls→0, B9_static_param_named_cls→0, B10_own_name_rebound_local→0, B12_extra_decorator→0, B13_yield_from_arg→0, B13b_yield_then_return_empty→0, B14_nested_def_append→0, B15_lambda_key_append→0, B16_subscript_store→0, B17_iadd_arg→0, B18_slice_store→0, B19_rebind_concat→0, B20_elem_var_rebound→0, B21_walrus_elem→0, B27_locals_extend→0, B28_dunder_iadd→0, B30_insert_arg→0, B31_return_concat_arg→0, B32_return_star_arg→0, B35_alias_extend→0, B38_dataclasses_replace→0, B40_sorted_arg→0, B41_nested_return_arg→0, B44_ifexp_return_arg→0, B45_nonlocal_rebind→0, B47_unbound_list_append→0, B48_vars_extend→0, B49_extend_genexp_arg→0, B50_extend_unproven_factory→0, B51_append_max_arg→0, B56a_tuple_shadow_local→0, B59a_param_object_select→0, B59b_param_any_select→0, B61_dup_name_class_attr→0, B62_object_shadow_local→0, B23_registry_scalar→0, B33_global_acc→0, B34_class_pool→0, B26_module_rebound_class→0, B56b_tuple_shadow_module→0, B57_dunder_new_pool→0, B58_metaclass_call→0, B63_cls_new_in_pool_class→0, B65_decorator_name_shadow→0, O1_bypass_query_arg→0, O2_caller_passed_instances→0, RC1_type_call→0, RC2_dunder_class→0, RC3_copy_copy→0, RA1_extend_iter→0, RA2_iadd_tuple→0, RA3_setitem_dunder→0, RA4_operator_iadd→0, RA5_default_arg_alias→0, RA6_literal_alias→0, RA9_radd_grabber→0, RA13_loop_alias_acc→0, RA7_set_update_genexp→0, RA11_scope_acc_module_list→0, RA12_scope_elem_module_name→0, RR1_finally_return→0, RR2_except_return→0, RR4_match_return→0, RR3_walrus_return→0, RR5_map_identity→0, RE1_cache_setdefault→0, RE2_selector_delegate→0, RE3_scalar_selector→0, RE4_reconcile_boolop→0, RE5_nested_nonlocal_elem→0, RD1_outer_decorator→0, RS1_static_global_rebind→0, RI1_subclass_override_scalar→0, RN1_same_name_real_selector→0, RU1_super_selector→0, GU2_super_fresh→0, GU3_nested_generator_helper→0, RK1_if_block_redef→0, RK2_class_body_import→0, RK3_new_assigned→0, RK4_new_in_if→0, G03_dict_values→0, G05_map_factory→0, G07_loop_over_proven→0, G11_copy_method→0, G18_local_alias_factory→0, D1_classbody_decorator_shadow→0, S4_sorted_received→0, S5_sorted_mixed→0, S6_reversed_concat_received→0, S7_sorted_kwsplat→0, S8_sorted_local_shadow→0, R1_reversed_iter_smuggle→0, R2_reversed_reduce_inline→0, R4_reversed_named_reused→0, G1_module_fn_global_builtin→0 | 21/25 (select_orders, retouch_orders, merge_orders, followup_orders) |
| MUT-noargproof | 무인자 호출에도 본문 증명 요구(Ball — 운영 세션이 제외한 판) | N1_noarg_class_stash→2, N2_noarg_module_list→2, N3_noarg_default_param→2, N4_noarg_prebuilt→2, N5_noarg_functools_cache→2, N7_noarg_module_helper→2 | 25/25 |
| MUT-anyclscall | 단일 팩토리 증명 대신 `cls.<아무 메서드>(..)` 를 새 원소로 인정 | B4_identity_append→0, B50_extend_unproven_factory→0, B23_registry_scalar→0, B63_cls_new_in_pool_class→0, RE3_scalar_selector→0, RI1_subclass_override_scalar→0, RK1_if_block_redef→0, RK2_class_body_import→0 | 24/25 (retouch_orders) |
| MUT-noreadcheck | 누적 이름의 읽기 자리 검사 탈락 | B2_extend_arg→0, B3_loop_append_arg→0, B4_identity_append→0, B5_helper_fills_acc→0, B14_nested_def_append→0, B15_lambda_key_append→0, B16_subscript_store→0, B18_slice_store→0, B20_elem_var_rebound→0, B21_walrus_elem→0, B28_dunder_iadd→0, B30_insert_arg→0, B35_alias_extend→0, B47_unbound_list_append→0, B49_extend_genexp_arg→0, B50_extend_unproven_factory→0, B51_append_max_arg→0, RA1_extend_iter→0, RA3_setitem_dunder→0, RA4_operator_iadd→0, RA5_default_arg_alias→0, RA6_literal_alias→0, RA9_radd_grabber→0, RA13_loop_alias_acc→0, RA7_set_update_genexp→0, G07_loop_over_proven→0, S5_sorted_mixed→0, R1_reversed_iter_smuggle→0, R2_reversed_reduce_inline→0, R4_reversed_named_reused→0 | 24/25 (merge_orders) |
| MUT-noinitcheck | 누적 이름의 결속 값 검사 탈락 | B1_acc_seeded_from_arg→0, R4_reversed_named_reused→0 | 24/25 (followup_orders) |
| MUT-raddany | `+` 피연산자 읽기를 상대와 무관하게 허용(리뷰 m-1 되돌림) | RA9_radd_grabber→0 | 25/25 |
| MUT-nonestedscope | 중첩 def·class·lambda 안 대입을 바깥 단순 대입으로 합침(리뷰 M-2 되돌림) | RA11_scope_acc_module_list→0, RA12_scope_elem_module_name→0 | 25/25 |
| MUT-noclassscan | 클래스 본문 결속을 최상위 문장만 셈(리뷰 M-1 되돌림 — `if` 안 def·`__new__` 대입) | B61_dup_name_class_attr→0, RK1_if_block_redef→0, RK3_new_assigned→0, RK4_new_in_if→0, D1_classbody_decorator_shadow→0 | 25/25 |
| MUT-noclassimport | 클래스 본문 import 결속을 세지 않음(리뷰 M-1 되돌림 — import 덮기) | RK2_class_body_import→0 | 25/25 |
| MUT-nodeco | 데코레이터 정확 일치(하나뿐) 탈락 | B12_extra_decorator→0 | 25/25 |
| MUT-nonew | `__new__` 가드 탈락 | B57_dunder_new_pool→0, B63_cls_new_in_pool_class→0, RK3_new_assigned→0, RK4_new_in_if→0 | 25/25 |
| MUT-nometa | metaclass 제외 탈락 | B58_metaclass_call→0 | 25/25 |
| MUT-nofirst | `cls` 결속 검사 탈락 | B8_cls_rebound→0, B8b_comprehension_rebinds_cls→0 | 25/25 |
| MUT-noyield | yield 거부 탈락 | B13b_yield_then_return_empty→0, GU3_nested_generator_helper→0 | 25/25 |
| MUT-nonamevars | 이름 원소 결속 검사 탈락 | B20_elem_var_rebound→0, RE5_nested_nonlocal_elem→0 | 25/25 |
| MUT-nobuiltin | 내장 가림 검사 탈락 | B56a_tuple_shadow_local→0, B62_object_shadow_local→0, B56b_tuple_shadow_module→0, S8_sorted_local_shadow→0, G1_module_fn_global_builtin→0 | 25/25 |
| MUT-nodup | 클래스 본문 이름 중복 검사 탈락 | B61_dup_name_class_attr→0, RK1_if_block_redef→0, RK2_class_body_import→0 | 25/25 |
| MUT-nodecoshadow | 모듈 범위 데코레이터 이름 가림 검사 탈락 | B65_decorator_name_shadow→0 | 25/25 |
| MUT-noclassdeco | 클래스 본문 데코레이터 이름 가림 검사 탈락(구현 리뷰 M-2 되돌림) | D1_classbody_decorator_shadow→0 | 25/25 |
| MUT-reversedany | 누적 이름의 reversed 인자를 소비 자리와 무관하게 읽기로 인정(재검토 F-1 되돌림) | R1_reversed_iter_smuggle→0, R2_reversed_reduce_inline→0, R4_reversed_named_reused→0 | 25/25 |
| MUT-noglobalbuiltin | 모듈 함수 본문의 `global` 을 내장 가림으로 세지 않음(재검토 F-2 되돌림) | G1_module_fn_global_builtin→0 | 25/25 |
| MUT-sortedany | sorted·reversed 의 인자가 새 컬렉션인지 보지 않음 | B40_sorted_arg→0, S4_sorted_received→0, S5_sorted_mixed→0, S6_reversed_concat_received→0, R4_reversed_named_reused→0 | 25/25 |

잡히지 않은 변이체: 없음
