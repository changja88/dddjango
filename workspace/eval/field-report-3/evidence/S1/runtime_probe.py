"""S-1 런타임 실증 — subscript TypeError 재현 → django_stubs_ext.monkeypatch() 후 통과 여부 전수.

실행: cd <격리 사본> && <spring venv python> runtime_probe.py  (DJANGO_SETTINGS_MODULE 없이)
"""
from __future__ import annotations

import json
import sys

import django
from django import forms
from django.contrib import admin
from django.contrib.admin import options as admin_options
from django.forms import models as form_models
from django.views import View
from django.views.generic import (
    ArchiveIndexView, CreateView, DeleteView, DetailView, FormView, ListView,
    RedirectView, TemplateView, UpdateView,
)
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import FormMixin, ModelFormMixin
from django.views.generic.list import MultipleObjectMixin

TARGETS = [
    ("forms.ModelForm", forms.ModelForm),
    ("forms.BaseModelForm", form_models.BaseModelForm),
    ("forms.BaseInlineFormSet", forms.BaseInlineFormSet),
    ("forms.BaseModelFormSet", forms.BaseModelFormSet),
    ("admin.ModelAdmin", admin.ModelAdmin),
    ("admin.options.BaseModelAdmin", admin_options.BaseModelAdmin),
    ("admin.options.InlineModelAdmin", admin_options.InlineModelAdmin),
    ("admin.TabularInline", admin.TabularInline),
    ("admin.StackedInline", admin.StackedInline),
    ("views.View", View),
    ("generic.TemplateView", TemplateView),
    ("generic.RedirectView", RedirectView),
    ("generic.DetailView", DetailView),
    ("generic.ListView", ListView),
    ("generic.FormView", FormView),
    ("generic.CreateView", CreateView),
    ("generic.UpdateView", UpdateView),
    ("generic.DeleteView", DeleteView),
    ("generic.ArchiveIndexView", ArchiveIndexView),
    ("generic.detail.SingleObjectMixin", SingleObjectMixin),
    ("generic.list.MultipleObjectMixin", MultipleObjectMixin),
    ("generic.edit.FormMixin", FormMixin),
    ("generic.edit.ModelFormMixin", ModelFormMixin),
]


def probe(label: str) -> list[dict]:
    rows = []
    for name, cls in TARGETS:
        try:
            r = cls[int]
            ok = True
            note = f"→ {r!r}"
        except TypeError as e:
            ok = False
            note = str(e)
        has_cgi = "__class_getitem__" in cls.__dict__
        inherited = any("__class_getitem__" in k.__dict__ for k in cls.__mro__[1:])
        rows.append({"phase": label, "name": name, "subscript_ok": ok, "own_cgi": has_cgi,
                     "inherited_cgi": inherited, "note": note})
    return rows


def main() -> None:
    print(f"django {django.__version__} python {sys.version.split()[0]}")
    before = probe("before")
    import django_stubs_ext
    django_stubs_ext.monkeypatch()
    after = probe("after")
    # 상속으로 subscript 가 실제 클래스 정의에 쓰이는지(기저 표현) 확인
    class_def_checks = []
    for name, cls in TARGETS:
        try:
            ns = {"B": cls}
            exec(f"class X(B[int]):\n    pass", ns)  # noqa: S102
            class_def_checks.append({"name": name, "class_def_ok": True, "mro0": ns["X"].__mro__[1].__name__})
        except TypeError as e:
            class_def_checks.append({"name": name, "class_def_ok": False, "err": str(e)})
    print("| 클래스 | before subscript | after subscript | own __class_getitem__(after) | 상속 __class_getitem__(after) | after 기저 `class X(B[int])` |")
    print("|---|---|---|---|---|---|")
    for b, a, c in zip(before, after, class_def_checks):
        print(f"| `{a['name']}` | {'통과' if b['subscript_ok'] else 'TypeError'} | {'통과' if a['subscript_ok'] else 'TypeError'} | {a['own_cgi']} | {a['inherited_cgi']} | {'통과 ('+c.get('mro0','')+')' if c['class_def_ok'] else 'TypeError'} |")
    with open(sys.argv[1] if len(sys.argv) > 1 else "runtime_probe.jsonl", "w", encoding="utf-8") as fh:
        for r in before + after:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
        for c in class_def_checks:
            fh.write(json.dumps({"phase": "after-classdef", **c}, ensure_ascii=False) + "\n")
    print("\nbefore TypeError 문면:")
    for r in before:
        if not r["subscript_ok"]:
            print(f"  {r['name']}: {r['note']}")


if __name__ == "__main__":
    main()
