import json

from guardian import triage


def _full_payload(**overrides):
    payload = {
        "is_document": True,
        "readable": True,
        "document_type": "utility_bill",
        "sender": "City Power Company",
        "what_they_want": "Pay the monthly bill",
        "amount": "$84.20",
        "deadline": "2026-06-28",
        "requested_action": "Pay online or by mail",
        "scam_signals": [],
        "explanation": {
            "what_this_is": "This is an electricity bill.",
            "key_facts": ["From City Power", "Amount $84.20"],
            "worry_reasons": [],
            "what_to_do": ["Pay as you normally do."],
        },
    }
    payload.update(overrides)
    return payload


class TestParseModelJson:
    def test_clean_json(self):
        assert triage.parse_model_json(json.dumps(_full_payload()))["sender"] == "City Power Company"

    def test_fenced_json(self):
        raw = "```json\n" + json.dumps(_full_payload()) + "\n```"
        assert triage.parse_model_json(raw)["document_type"] == "utility_bill"

    def test_json_with_surrounding_prose(self):
        raw = "Here is my analysis:\n" + json.dumps(_full_payload()) + "\nHope that helps!"
        assert triage.parse_model_json(raw) is not None

    def test_trailing_comma_tolerated(self):
        raw = '{"is_document": true, "document_type": "bank",}'
        assert triage.parse_model_json(raw)["document_type"] == "bank"

    def test_braces_inside_strings(self):
        raw = '{"sender": "Acme {Corp}", "is_document": true}'
        assert triage.parse_model_json(raw)["sender"] == "Acme {Corp}"

    def test_garbage_returns_none(self):
        assert triage.parse_model_json("I cannot read this image, sorry.") is None

    def test_invalid_escape_repaired(self):
        # Regression: live MiniCPM-V output contained \' (invalid JSON escape).
        raw = r'{"is_document": true, "sender": "they say you don\'t have time"}'
        data = triage.parse_model_json(raw)
        assert data is not None and "don't" in data["sender"]

    def test_valid_escapes_preserved(self):
        raw = '{"sender": "Line\\nBreak \\"quoted\\" \\\\slash"}'
        data = triage.parse_model_json(raw)
        assert data["sender"] == 'Line\nBreak "quoted" \\slash'

    def test_empty_returns_none(self):
        assert triage.parse_model_json("") is None


class TestValidateExtraction:
    def test_happy_path(self):
        ex = triage.validate_extraction(_full_payload())
        assert ex.document_type == "utility_bill"
        assert ex.amount == "$84.20"
        assert ex.what_this_is == "This is an electricity bill."

    def test_unknown_doc_type_coerced(self):
        ex = triage.validate_extraction(_full_payload(document_type="ransom_note"))
        assert ex.document_type == "other"

    def test_unknown_signal_ids_dropped(self):
        ex = triage.validate_extraction(
            _full_payload(scam_signals=[{"id": "alien_invasion", "evidence": "x"},
                                        {"id": "urgency", "evidence": "act now"}])
        )
        assert [s.id for s in ex.scam_signals] == ["urgency"]

    def test_null_strings_become_none(self):
        ex = triage.validate_extraction(_full_payload(amount="null", deadline=None))
        assert ex.amount is None and ex.deadline is None

    def test_explanation_as_string_kept(self):
        # Regression: live model collapsed the explanation object into prose.
        ex = triage.validate_extraction(
            _full_payload(explanation="This is a tax notice. Be careful.")
        )
        assert ex.what_this_is == "This is a tax notice. Be careful."
        assert ex.what_to_do == []

    def test_list_limits_enforced(self):
        ex = triage.validate_extraction(
            _full_payload(explanation={"key_facts": [f"f{i}" for i in range(10)],
                                       "what_to_do": [f"s{i}" for i in range(10)]})
        )
        assert len(ex.key_facts) == 4 and len(ex.what_to_do) == 4


class TestHeuristics:
    def test_gift_card_detected(self):
        hits = {s.id for s in triage.run_heuristics("Pay with iTunes gift card today")}
        assert "gift_card_or_crypto" in hits

    def test_otp_detected(self):
        hits = {s.id for s in triage.run_heuristics("Share the OTP to verify your account")}
        assert "credentials_request" in hits

    def test_urgency_and_threat_detected(self):
        hits = {s.id for s in triage.run_heuristics(
            "URGENT: final notice — your account will be suspended")}
        assert {"urgency", "threat_or_arrest"} <= hits

    def test_lottery_detected(self):
        hits = {s.id for s in triage.run_heuristics("Congratulations! You have won the lottery")}
        assert "prize_too_good" in hits

    def test_hindi_urgency_detected(self):
        hits = {s.id for s in triage.run_heuristics("तुरंत भुगतान करें")}
        assert "urgency" in hits

    def test_normal_bill_clean(self):
        text = "City Power Company | monthly electricity bill | $84.20 due June 28"
        assert triage.run_heuristics(text) == []


class TestWorryLevel:
    def test_no_signals_low(self):
        assert triage.worry_level("utility_bill", []) == "low"

    def test_one_signal_caution(self):
        assert triage.worry_level("bank", [triage.ScamSignal("urgency")]) == "caution"

    def test_two_signals_warning(self):
        signals = [triage.ScamSignal("urgency"), triage.ScamSignal("gift_card_or_crypto")]
        assert triage.worry_level("bank", signals) == "warning"

    def test_suspected_scam_always_warning(self):
        assert triage.worry_level("suspected_scam", []) == "warning"


class TestMergeSignals:
    def test_model_evidence_wins_on_overlap(self):
        model = [triage.ScamSignal("urgency", "must act within 24 hours")]
        heuristic = [triage.ScamSignal("urgency", "urgent"),
                     triage.ScamSignal("wire_transfer", "western union")]
        merged = {s.id: s.evidence for s in triage.merge_signals(model, heuristic)}
        assert merged["urgency"] == "must act within 24 hours"
        assert "wire_transfer" in merged
