"""All user-facing strings in English, Hindi, and Spanish.

Written at a low reading level on purpose — the user may be 70+ and stressed
about a letter they don't understand. Calm, concrete, never alarmist."""

from __future__ import annotations

STRINGS: dict[str, dict[str, str]] = {
    "en": {
        "title": "📬 Mystery-Mail Guardian",
        "tagline": "Take a photo of a confusing letter. I will explain it in plain words.",
        "privacy": "🔒 Your letter never leaves this device. Everything runs locally on small models.",
        "upload_label": "Take a photo of your letter",
        "language_label": "Language / भाषा / Idioma",
        "analyze_btn": "📖 Read my letter",
        "read_aloud_btn": "🔊 Read it aloud",
        "audio_label": "Listen",
        "section_what": "What this is",
        "section_worry": "Should you worry?",
        "section_todo": "What to do",
        "worry_low": "This looks like normal mail, but always double-check before paying or replying.",
        "worry_caution": "⚠️ Be careful. This letter has a warning sign often seen in scams:",
        "worry_warning": "🚨 Please be very careful. This letter shows several warning signs often seen in scams:",
        "verify": "Before you pay or reply: contact the company or office through a phone number or "
                  "website you already know and trust — never use the contact details printed in this letter.",
        "disclaimer": "I can make mistakes. For anything important, check with someone you trust.",
        "err_no_image": "Please add a photo of your letter first.",
        "err_unreadable": "I could not read this photo clearly. Please try again with more light, a bit closer.",
        "err_not_document": "This photo does not look like a letter or document. Please take a photo of the letter itself.",
        "err_model": "Something went wrong while reading the letter. Please try once more.",
        "err_no_speech": "Read a letter first, then I can read the result aloud.",
        "waiting": "Your explanation will appear here.",
    },
    "hi": {
        "title": "📬 Mystery-Mail Guardian",
        "tagline": "किसी भी उलझाने वाली चिट्ठी की फोटो लें। मैं उसे आसान शब्दों में समझाऊँगा।",
        "privacy": "🔒 आपकी चिट्ठी इस डिवाइस से बाहर नहीं जाती। सब कुछ छोटे मॉडलों पर, यहीं चलता है।",
        "upload_label": "अपनी चिट्ठी की फोटो लें",
        "language_label": "Language / भाषा / Idioma",
        "analyze_btn": "📖 मेरी चिट्ठी पढ़ो",
        "read_aloud_btn": "🔊 आवाज़ में सुनाओ",
        "audio_label": "सुनिए",
        "section_what": "यह क्या है",
        "section_worry": "क्या चिंता की बात है?",
        "section_todo": "अब क्या करें",
        "worry_low": "यह सामान्य चिट्ठी लगती है, फिर भी पैसे देने या जवाब देने से पहले हमेशा जाँच लें।",
        "worry_caution": "⚠️ सावधान रहें। इस चिट्ठी में एक ऐसा संकेत है जो अक्सर धोखाधड़ी में दिखता है:",
        "worry_warning": "🚨 बहुत सावधान रहें। इस चिट्ठी में धोखाधड़ी जैसे कई संकेत दिख रहे हैं:",
        "verify": "पैसे देने या जवाब देने से पहले: उस कंपनी या दफ़्तर से उसी नंबर या वेबसाइट पर बात करें "
                  "जिसे आप पहले से जानते और भरोसा करते हैं — इस चिट्ठी में छपे नंबर या पते का इस्तेमाल न करें।",
        "disclaimer": "मुझसे गलती हो सकती है। किसी भी ज़रूरी बात के लिए अपने किसी भरोसेमंद व्यक्ति से ज़रूर पूछें।",
        "err_no_image": "पहले अपनी चिट्ठी की फोटो डालें।",
        "err_unreadable": "मैं इस फोटो को साफ़ नहीं पढ़ पाया। ज़्यादा रोशनी में, थोड़ा पास से दोबारा फोटो लें।",
        "err_not_document": "यह फोटो चिट्ठी या दस्तावेज़ जैसी नहीं लगती। कृपया चिट्ठी की ही फोटो लें।",
        "err_model": "चिट्ठी पढ़ते समय कुछ गड़बड़ हो गई। कृपया एक बार फिर कोशिश करें।",
        "err_no_speech": "पहले कोई चिट्ठी पढ़वाएँ, फिर मैं नतीजा आवाज़ में सुना सकता हूँ।",
        "waiting": "आपकी चिट्ठी की जानकारी यहाँ दिखेगी।",
    },
    "es": {
        "title": "📬 Mystery-Mail Guardian",
        "tagline": "Tome una foto de una carta confusa. Se la explico en palabras sencillas.",
        "privacy": "🔒 Su carta nunca sale de este dispositivo. Todo funciona localmente con modelos pequeños.",
        "upload_label": "Tome una foto de su carta",
        "language_label": "Language / भाषा / Idioma",
        "analyze_btn": "📖 Leer mi carta",
        "read_aloud_btn": "🔊 Léamela en voz alta",
        "audio_label": "Escuchar",
        "section_what": "Qué es esto",
        "section_worry": "¿Debe preocuparse?",
        "section_todo": "Qué hacer",
        "worry_low": "Parece correo normal, pero verifique siempre antes de pagar o responder.",
        "worry_caution": "⚠️ Tenga cuidado. Esta carta tiene una señal de alerta común en estafas:",
        "worry_warning": "🚨 Tenga mucho cuidado. Esta carta muestra varias señales de alerta comunes en estafas:",
        "verify": "Antes de pagar o responder: contacte a la empresa u oficina por un teléfono o sitio web "
                  "que usted ya conozca y en el que confíe — nunca use los datos de contacto impresos en esta carta.",
        "disclaimer": "Puedo equivocarme. Para cualquier asunto importante, consulte con alguien de confianza.",
        "err_no_image": "Primero agregue una foto de su carta.",
        "err_unreadable": "No pude leer esta foto con claridad. Intente de nuevo con más luz, un poco más cerca.",
        "err_not_document": "Esta foto no parece una carta o documento. Por favor, tome una foto de la carta.",
        "err_model": "Algo salió mal al leer la carta. Inténtelo una vez más.",
        "err_no_speech": "Primero lea una carta; después puedo leerle el resultado en voz alta.",
        "waiting": "Su explicación aparecerá aquí.",
    },
}

# Localized labels for the scam-signal taxonomy in triage.SIGNAL_IDS.
SIGNAL_LABELS: dict[str, dict[str, str]] = {
    "urgency": {
        "en": "It pushes you to act immediately",
        "hi": "यह तुरंत कुछ करने का दबाव डालती है",
        "es": "Le presiona a actuar de inmediato",
    },
    "gift_card_or_crypto": {
        "en": "It asks for payment by gift card or cryptocurrency",
        "hi": "यह गिफ्ट कार्ड या क्रिप्टो से भुगतान माँगती है",
        "es": "Pide pago con tarjetas de regalo o criptomonedas",
    },
    "wire_transfer": {
        "en": "It asks for a wire or money transfer",
        "hi": "यह वायर ट्रांसफर या मनी ट्रांसफर माँगती है",
        "es": "Pide una transferencia de dinero",
    },
    "credentials_request": {
        "en": "It asks for passwords, OTP codes, or personal ID numbers",
        "hi": "यह पासवर्ड, OTP या निजी पहचान नंबर माँगती है",
        "es": "Pide contraseñas, códigos OTP o números de identidad",
    },
    "prize_too_good": {
        "en": "It promises a prize or deal that seems too good to be true",
        "hi": "यह ऐसा इनाम या ऑफ़र देती है जो सच होने के लिए बहुत अच्छा लगता है",
        "es": "Promete un premio u oferta demasiado buena para ser verdad",
    },
    "threat_or_arrest": {
        "en": "It threatens fines, arrest, or closing your account",
        "hi": "यह जुर्माने, गिरफ़्तारी या खाता बंद करने की धमकी देती है",
        "es": "Amenaza con multas, arresto o cierre de su cuenta",
    },
    "sender_mismatch": {
        "en": "The sender's name and contact details do not match",
        "hi": "भेजने वाले का नाम और संपर्क विवरण मेल नहीं खाते",
        "es": "El nombre del remitente y sus datos no coinciden",
    },
    "unofficial_contact": {
        "en": "It tells you to use contact details that skip official channels",
        "hi": "यह आधिकारिक माध्यम छोड़कर दूसरे नंबर या पते पर संपर्क करने को कहती है",
        "es": "Pide usar datos de contacto que evitan los canales oficiales",
    },
    "pressure_to_act": {
        "en": "It uses fear or pressure so you do not stop to think",
        "hi": "यह डर या दबाव बनाती है ताकि आप सोच-विचार न कर सकें",
        "es": "Usa miedo o presión para que no lo piense con calma",
    },
    "lookalike_bill": {
        "en": "It looks like a bill but may be advertising or fake",
        "hi": "यह बिल जैसी दिखती है पर विज्ञापन या नकली हो सकती है",
        "es": "Parece una factura pero puede ser publicidad o falsa",
    },
}


def get(lang: str, key: str) -> str:
    """Localized string with English fallback."""
    return STRINGS.get(lang, STRINGS["en"]).get(key, STRINGS["en"].get(key, key))


def signal_label(signal_id: str, lang: str) -> str:
    labels = SIGNAL_LABELS.get(signal_id, {})
    return labels.get(lang, labels.get("en", signal_id))
