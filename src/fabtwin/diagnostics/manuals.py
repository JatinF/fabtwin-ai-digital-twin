"""Tenant-filtered manual retrieval."""

from __future__ import annotations

import json
import re

from fabtwin.paths import dataset_dir

TOKEN = re.compile(r"[a-z0-9][a-z0-9\-]*")


def load_documents() -> list[dict]:
    payload = json.loads((dataset_dir() / "documents.json").read_text(encoding="utf-8"))
    return list(payload["documents"])


def load_episodes() -> list[dict]:
    payload = json.loads((dataset_dir() / "episodes.json").read_text(encoding="utf-8"))
    return list(payload["episodes"])


def retrieve(tenant: str, question: str, documents: list[dict] | None = None) -> list[dict]:
    tokens = set(TOKEN.findall(question.lower()))
    ranked = []
    for document in documents if documents is not None else load_documents():
        if document["tenant"] != tenant:
            continue
        body = set(TOKEN.findall(f"{document['title']} {document['text']}".lower()))
        overlap = len(tokens & body)
        if overlap:
            ranked.append((overlap, document["id"], document))
    ranked.sort(key=lambda item: (-item[0], item[1]))
    return [dict(document, overlap=overlap) for overlap, _, document in ranked[:3]]
