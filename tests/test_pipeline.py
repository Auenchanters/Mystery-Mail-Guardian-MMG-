"""End-to-end pipeline behavior in mock mode + composition rules with real
extractions (no model weights involved)."""

from guardian import config, pipeline, render, triage, ui_text


class TestParamBudget:
    def test_lean_config_under_cap(self):
        assert sum(config.PARAMS_B[m] for m in
                   [config.MINICPM_V_ID, config.VOXCPM_ID]) <= config.PARAM_CAP_B

    def test_full_config_under_cap(self):
        assert sum(config.PARAMS_B.values()) <= config.PARAM_CAP_B

    def test_budget_guard_passes(self):
        assert config.assert_param_budget() <= config.PARAM_CAP_B


class TestAnalyzeMock:
    def test_no_image_localized_error(self):
        for lang in ("en", "hi", "es"):
            result = pipeline.analyze(None, lang)
            assert not result.ok
            assert result.error == ui_text.get(lang, "err_no_image")

    def test_mock_analysis_complete(self):
        result = pipeline.analyze(object(), "en")
        assert result.ok
        assert result.what_this_is
        assert result.worry_level == "low"
        assert result.worry_headline == ui_text.get("en", "worry_low")
        assert result.actions[-1] == ui_text.get("en", "verify")
        assert 0 < len(result.speak_text) <= config.TTS_MAX_CHARS

    def test_mock_localized_in_hindi(self):
        result = pipeline.analyze(object(), "hi")
        assert "बिजली" in result.what_this_is
        assert result.worry_headline == ui_text.get("hi", "worry_low")


class TestCompose:
    def _scammy_extraction(self):
        ex = triage.Extraction(document_type="suspected_scam", sender="IRS Dept",
                               requested_action="Buy gift cards and call immediately")
        ex.scam_signals = [triage.ScamSignal("urgency", "act within 24 hours")]
        ex.what_this_is = "This is a scam letter pretending to be the tax office."
        ex.worry_reasons = ["It says you must act within 24 hours."]
        ex.what_to_do = ["Do not call 1-800-555-0199.", "Show it to a family member."]
        return ex

    def test_scam_letter_gets_warning(self):
        result = pipeline._compose(self._scammy_extraction(), "en")
        assert result.worry_level == "warning"
        assert result.worry_headline == ui_text.get("en", "worry_warning")

    def test_verdict_softened_in_what_this_is(self):
        result = pipeline._compose(self._scammy_extraction(), "en")
        assert "this is a scam letter" not in result.what_this_is.lower()

    def test_contacts_stripped_from_actions(self):
        result = pipeline._compose(self._scammy_extraction(), "en")
        assert all("555" not in a for a in result.actions)

    def test_heuristic_only_signals_get_labels(self):
        # Model reported only urgency; gift card phrase in requested_action should
        # be caught by heuristics and surfaced with its localized label.
        result = pipeline._compose(self._scammy_extraction(), "en")
        assert any("gift card" in r.lower() for r in result.worry_reasons)

    def test_verification_advice_always_last_action(self):
        for lang in ("en", "hi", "es"):
            result = pipeline._compose(self._scammy_extraction(), lang)
            assert result.actions[-1] == ui_text.get(lang, "verify")

    def test_normal_bill_stays_low_but_never_safe(self):
        ex = triage.Extraction(document_type="utility_bill", sender="City Power")
        ex.what_this_is = "This is an electricity bill."
        ex.what_to_do = ["Pay as you normally do."]
        result = pipeline._compose(ex, "en")
        assert result.worry_level == "low"
        assert "safe" not in result.worry_headline.lower()
        assert "double-check" in result.worry_headline


class TestRender:
    def test_model_text_html_escaped(self):
        ex = triage.Extraction(document_type="other")
        ex.what_this_is = 'A letter <script>alert("x")</script> from someone.'
        ex.what_to_do = ["Be <b>careful</b>"]
        what_html, _, todo_html = render.render_result(pipeline._compose(ex, "en"))
        assert "<script>" not in what_html and "&lt;script&gt;" in what_html
        assert "<b>" not in todo_html

    def test_worry_card_class_matches_level(self):
        result = pipeline.analyze(object(), "en")
        _, worry_html, _ = render.render_result(result)
        assert "card-low" in worry_html

    def test_error_renders_single_card(self):
        what_html, worry_html, todo_html = render.render_result(pipeline.analyze(None, "es"))
        assert ui_text.get("es", "err_no_image") in what_html
        assert worry_html == "" and todo_html == ""

    def test_placeholder_renders_all_langs(self):
        for lang in ("en", "hi", "es"):
            what_html, _, _ = render.render_placeholder(lang)
            assert ui_text.get(lang, "waiting") in what_html
