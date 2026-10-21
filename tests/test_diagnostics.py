"""Synthetic image features, tenant manuals, and the NIST archive."""

from __future__ import annotations

from fabtwin.diagnostics.images import IMAGE_KINDS, classify_image, render
from fabtwin.diagnostics.manuals import load_documents, load_episodes, retrieve
from fabtwin.diagnostics.nist_archive import archive_manifest, global_dice


def test_image_rules_match_the_four_renders():
    for image_id, kind in IMAGE_KINDS.items():
        assert classify_image(render(image_id)) == kind


def test_retrieval_keeps_the_tenant_boundary():
    documents = load_documents()
    expected = {
        "SYN-EP-001": "SYN-DOC-COOLING",
        "SYN-EP-002": "SYN-DOC-PRESSURE",
        "SYN-EP-003": "SYN-DOC-DRIFT",
        "SYN-EP-004": "SYN-DOC-NORMAL",
        "SYN-EP-005": "SYN-DOC-COOLING",
        "SYN-EP-B01": "SYN-DOC-OTHER",
    }
    for episode in load_episodes():
        ranked = retrieve(episode["tenant"], episode["question"], documents)
        assert ranked[0]["id"] == expected[episode["episode_id"]]
        assert ranked[0]["tenant"] == episode["tenant"]
        if episode["tenant"] == "tenant-a":
            assert "SYN-DOC-OTHER" not in {item["id"] for item in ranked}


def test_nist_dice_is_spec_and_the_unet_was_not_run():
    rows = global_dice()
    assert [round(row["arithmetic_mean"], 12) for row in rows] == [
        round(0.7888469074374048, 12),
        round(0.8466672651576093, 12),
        round(0.8162391854030813, 12),
    ]
    assert all(row["evidence_class"] == "SPEC" and row["unet_executed_by_fabtwin"] is False for row in rows)
    manifest = archive_manifest()
    assert manifest["intensity_sets_zip"] == "not-downloaded"
    assert manifest["aimodel_sets_zip"] == "not-downloaded"
    assert manifest["unet_executed_by_fabtwin"] is False
    assert len(manifest["metrics_zip_sha256"]) == 64
    assert manifest["metrics_zip_bytes"] == 787689
    assert manifest["readme_bytes"] == 13114
