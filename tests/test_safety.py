"""The §7 safety layer is the product's spine — test it hard."""

from guardian import safety


class TestSoftenVerdicts:
    def test_scam_verdict_softened(self):
        out = safety.soften_verdicts("This is a scam. Throw it away.")
        assert "this is a scam" not in out.lower()
        assert "could be" in out.lower()

    def test_definite_scam_softened(self):
        out = safety.soften_verdicts("This is definitely a scam!")
        assert "definitely" not in out.lower()

    def test_safe_verdict_softened(self):
        out = safety.soften_verdicts("Don't worry, this is completely safe.")
        assert "is completely safe" not in out.lower()
        assert "verify" in out.lower()

    def test_trust_verdict_softened(self):
        out = safety.soften_verdicts("You can trust this letter.")
        assert "you can trust this" not in out.lower()

    def test_hindi_verdict_softened(self):
        out = safety.soften_verdicts("यह पक्का धोखा है।")
        assert "पक्का" not in out
        assert "हो सकती है" in out

    def test_spanish_verdict_softened(self):
        out = safety.soften_verdicts("Esto es una estafa.")
        assert "podría ser" in out

    def test_cautious_text_unchanged(self):
        text = "This looks like a normal bill from City Power, but always verify."
        assert safety.soften_verdicts(text) == text


class TestStripContactDetails:
    def test_phone_removed(self):
        assert "555" not in safety.strip_contact_details("Call 1-800-555-0199 now")

    def test_international_phone_removed(self):
        assert "98765" not in safety.strip_contact_details("Ring +91 98765 43210 today")

    def test_url_removed(self):
        out = safety.strip_contact_details("Visit https://evil-bank.example/pay to settle")
        assert "evil-bank" not in out

    def test_www_url_removed(self):
        assert "scam.example" not in safety.strip_contact_details("Go to www.scam.example now")

    def test_email_removed(self):
        assert "@" not in safety.strip_contact_details("Email refunds@scam.example today")

    def test_plain_text_preserved(self):
        text = "Ask a family member to look at the letter with you."
        assert safety.strip_contact_details(text) == text

    def test_years_and_amounts_survive(self):
        out = safety.strip_contact_details("Pay $84.20 before June 28, 2026.")
        assert "$84.20" in out and "2026" in out


class TestFraming:
    def test_action_step_sanitized_end_to_end(self):
        step = "This is a scam — call 1-800-555-0199 or visit www.evil.example"
        out = safety.sanitize_action_step(step)
        assert "555" not in out and "evil.example" not in out
        assert "this is a scam" not in out.lower()

    def test_verification_advice_never_empty_all_langs(self):
        for lang in ("en", "hi", "es"):
            advice = safety.verification_advice(lang)
            assert len(advice) > 20

    def test_worry_headline_has_no_verdict(self):
        for lang in ("en", "hi", "es"):
            for level in ("low", "caution", "warning"):
                headline = safety.worry_headline(level, lang)
                assert headline  # exists
                lowered = headline.lower()
                assert "is a scam" not in lowered and "is safe" not in lowered

    def test_disclaimer_exists_all_langs(self):
        for lang in ("en", "hi", "es"):
            assert len(safety.disclaimer(lang)) > 10
