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

    def test_stray_period_between_fields_repaired(self):
        # Regression: live model emitted '"...threats".' then the next key —
        # a stray period instead of a comma. json_repair handles this tail.
        raw = ('{"is_document": true, "explanation": {'
               '"what_this_is": "a tax notice. be careful".\n'
               '"key_facts": ["amount is $500"]}}')
        data = triage.parse_model_json(raw)
        assert data is not None
        ex = triage.validate_extraction(data)
        assert "$500" in ex.key_facts[0]

    def test_truncated_mid_string_salvaged(self):
        # Regression: generation cut off mid-explanation -> unterminated JSON.
        raw = '{"is_document": true, "amount": "$500", "explanation": "Be careful abo'
        data = triage.parse_model_json(raw)
        assert data is not None and data["amount"] == "$500"

    def test_truncated_mid_structure_salvaged(self):
        raw = '{"is_document": true, "scam_signals": [{"id": "urgency", "evidence": "act now"}'
        data = triage.parse_model_json(raw)
        assert data["scam_signals"][0]["id"] == "urgency"

    def test_truncated_after_comma_salvaged(self):
        raw = '{"is_document": true, "sender": "City Power",'
        data = triage.parse_model_json(raw)
        assert data["sender"] == "City Power"

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

    def test_prompt_echo_facts_dropped(self):
        # Regression (live, 06-11): the model parroted the schema's field
        # descriptions back as "facts" instead of extracting real values.
        ex = triage.validate_extraction(
            _full_payload(explanation={
                "key_facts": ["who sent it", "What they want", "money mentioned",
                              "From: City Power Company"],
                "what_to_do": ["what to do", "Pay the way you normally pay."],
            })
        )
        assert ex.key_facts == ["From: City Power Company"]
        assert ex.what_to_do == ["Pay the way you normally pay."]

    def test_all_echo_facts_leave_empty_list(self):
        # All-echo lists must end up empty so the deterministic fallback
        # synthesis kicks in instead of rendering placeholder bullets.
        ex = triage.validate_extraction(
            _full_payload(explanation={"key_facts": ["amount", "deadline:",
                                                     "Key facts", "sender"]})
        )
        assert ex.key_facts == []


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

    def test_hindi_gift_card_detected(self):
        # Modal ML-eval (06-12): hi/ja scam letters under-flagged — the
        # heuristic taxonomy lacked Devanagari/Japanese scam vocabulary.
        signals = triage.run_heuristics("केवल गिफ्ट कार्ड से भुगतान करें")
        assert "gift_card_or_crypto" in [s.id for s in signals]

    def test_japanese_scam_vocabulary_detected(self):
        text = "至急ギフトカードで支払ってください。支払わなければ逮捕されます。"
        ids = [s.id for s in triage.run_heuristics(text)]
        assert "gift_card_or_crypto" in ids
        assert "urgency" in ids
        assert "threat_or_arrest" in ids

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
