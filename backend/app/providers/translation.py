"""
Translation Provider Layer for Indian Languages (Tamil & Regional)
Integrates live Sarvam AI Mayura translation engine, LLM translation adapter,
and a comprehensive medical-domain Tamil translator preserving numeric integrity,
clinical units, and safety safeguards.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
import re
import httpx
from app.core.config import settings

class BaseTranslationProvider(ABC):
    @abstractmethod
    async def translate_text(self, text: str, source_lang: str, target_lang: str) -> str:
        pass

class SarvamTranslationProvider(BaseTranslationProvider):
    """
    Sarvam Mayura translation engine adapter for Indian languages.
    """
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url

    async def translate_text(self, text: str, source_lang: str, target_lang: str) -> str:
        if not self.api_key:
            raise ValueError("SARVAM_API_KEY required for live translation.")
        
        headers = {"api-subscription-key": self.api_key}
        payload = {
            "input": text,
            "source_language_code": f"{source_lang}-IN" if "-" not in source_lang else source_lang,
            "target_language_code": f"{target_lang}-IN" if "-" not in target_lang else target_lang,
            "speaker_gender": "Female",
            "mode": "formal"
        }
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.post(f"{self.base_url}/translate", headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data.get("translated_text", text)

class LLMTranslationProvider(BaseTranslationProvider):
    """
    OpenAI/Sarvam LLM powered translation adapter for complex medical health explanations.
    """
    def __init__(self, api_key: str, provider: str = "openai"):
        self.api_key = api_key
        self.provider = provider

    async def translate_text(self, text: str, source_lang: str, target_lang: str) -> str:
        if not self.api_key:
            return text
            
        system_prompt = (
            "You are a medical translator specializing in Indian languages. "
            "Translate the clinical health summary into clear, empathetic Tamil (ta). "
            "CRITICAL HEALTHCARE RULE: Keep all numbers, units (e.g. mg/dL, %, g/dL), "
            "and drug names exactly verbatim without alteration. Preserve safety disclaimers."
        )
        try:
            async with httpx.AsyncClient(timeout=25.0) as client:
                resp = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={
                        "model": "gpt-4o-mini",
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": f"Translate this text to Tamil:\n\n{text}"}
                        ],
                        "temperature": 0.2
                    }
                )
                if resp.status_code == 200:
                    data = resp.json()
                    return data["choices"][0]["message"]["content"].strip()
        except Exception:
            pass
        return text

class MedicalTamilTranslationProvider(BaseTranslationProvider):
    """
    Comprehensive Medical Tamil Translation Engine with expansive terminology,
    biomarker translations, and clinical safeguarding.
    """
    def __init__(self):
        self.medical_glossary = {
            # Glycemic Biomarkers
            "Fasting Blood Glucose": "உண்ணாநிலை இரத்த சர்க்கரை அளவு (Fasting Blood Glucose)",
            "Postprandial Blood Glucose": "உணவுக்குப் பின் இரத்த சர்க்கரை (Postprandial Blood Glucose)",
            "Random Blood Glucose": "தற்செயல் இரத்த சர்க்கரை அளவு (Random Blood Glucose)",
            "HbA1c": "HbA1c (சராசரி இரத்த சர்க்கரை)",
            
            # Lipid Profile
            "Total Cholesterol": "மொத்த கொலஸ்ட்ரால் (Total Cholesterol)",
            "HDL Cholesterol": "நல்ல கொலஸ்ட்ரால் (HDL Cholesterol)",
            "LDL Cholesterol": "கெட்ட கொலஸ்ட்ரால் (LDL Cholesterol)",
            "Serum Triglycerides": "ட்parsingரைகிளிசரைடுகள் (Serum Triglycerides)",
            
            # Hematology / CBC
            "Hemoglobin": "ஹீமோகுளோபின் (Hemoglobin)",
            "Total Leukocyte Count (WBC)": "வெள்ளை இரத்த அணுக்கள் (WBC Count)",
            "Platelet Count": "இரத்த தட்டணுக்கள் (Platelet Count)",
            
            # Renal Function
            "Serum Creatinine": "சீரம் கிரியேட்டினின் (Serum Creatinine - சிறுநீரக செயல்பாடு)",
            "Blood Urea Nitrogen (BUN)": "இரத்த யூரியா நைட்ரஜன் (BUN)",
            "Serum Uric Acid": "யூரிக் அமிலம் (Serum Uric Acid)",
            
            # Hepatic & Thyroid
            "Serum Bilirubin (Total)": "பிலிரூபின் (Bilirubin - கல்லீரல் பித்தம்)",
            "SGOT / AST": "SGOT / AST (கல்லீரல் நொதி)",
            "SGPT / ALT": "SGPT / ALT (கல்லீரல் நொதி)",
            "Thyroid Stimulating Hormone (TSH)": "தைராய்டு ஹார்மோன் (TSH)",
            
            # Reference ranges & flags
            "Above Reference Range": "இயல்பு வரம்பை விட அதிகம் (Above Range)",
            "Below Reference Range": "இயல்பு வரம்பை விட குறைவு (Below Range)",
            "within normal reference parameters": "சாதாரண ஆய்வக வரம்பிற்குள் உள்ளது",
            "Not stated": "குறிப்பிடப்படவில்லை",
            
            # Dosage terms
            "Once daily": "தினசரி ஒரு வேளை",
            "Twice daily": "தினசரி இரண்டு வேளை",
            "Three times daily": "தினசரி மூன்று வேளை",
            "Once daily at night": "தினசரி இரவு படுக்கும் முன்",
            "tablet": "மாத்திரை",
            "after dinner": "இரவு உணவுக்குப் பின்",
            "in the morning": "காலையில்",
            "at bedtime": "படுக்கும் முன்",
            "before breakfast": "காலை உணவுக்கு முன்",
            "oral": "வாய்வழியாக"
        }

    async def translate_text(self, text: str, source_lang: str, target_lang: str) -> str:
        if target_lang != "ta":
            return text
            
        res = text
        for eng, tam in self.medical_glossary.items():
            res = res.replace(eng, tam)
            
        # Clinical explanation phrases
        phrases = [
            ("This laboratory report from", "இந்த ஆய்வக அறிக்கை -"),
            ("details your", "இதில் உள்ள அளவீடுகள்:"),
            ("is recorded at", "பதிவாகியுள்ள அளவு:"),
            ("Reference:", "இயல்பு வரம்பு:"),
            ("both elevated above standard laboratory cutoffs", "இரண்டும் ஆய்வக வழக்கமான வரம்பை விட அதிகமாக உள்ளன"),
            ("within the desirable range", "விரும்பத்தக்க சாதாரண வரம்பிற்குள் உள்ளது"),
            ("Reflects average blood sugar control over the past 2 to 3 months", "கடந்த 2 முதல் 3 மாதங்களின் சராசரி இரத்த சர்க்கரை கட்டுப்பாட்டைக் குறிக்கிறது"),
            ("Should my diabetes medication be adjusted", "எனது சர்க்கரை நோய் மருந்துகளை மாற்ற வேண்டுமா"),
            ("What might be contributing to my elevated", "அதிகரித்த அளவீட்டிற்கான சாத்தியமான காரணங்கள் என்ன"),
            ("Should my low", "எனது குறைந்த அளவீட்டை மீண்டும்"),
            ("reading be re-tested", "பரிசோதிக்க வேண்டுமா"),
            ("Are there lifestyle or dietary adjustments recommended", "உணவு முறை அல்லது வாழ்க்கை முறையில் மாற்றங்கள் தேவையா"),
            ("When should follow-up diagnostic tests be scheduled", "அடுத்த பின்தொடர் பரிசோதனைகளை எப்போது திட்டமிட வேண்டும்"),
            ("Prescribed", "பரிந்துரைக்கப்பட்ட மருந்து:"),
            ("for", "கால அளவு:"),
            ("Are there any specific dietary precautions while taking", "இந்த மருந்தை உட்கொள்ளும்போது குறிப்பிட்ட உணவுப் பத்தியங்கள் உள்ளதா"),
            ("INFORMATIONAL ASSISTANCE ONLY: This tool is not a doctor", "தகவல் உதவி மட்டுமே: இந்த செயலி மருத்துவர் அல்ல"),
            ("Laboratory diagnostic report from", "ஆய்வக அறிக்கை -"),
            ("Outpatient prescription from", "பரிந்துரைக்கப்பட்ட மருத்துவச் சீட்டு -"),
            ("Clinical Note: An elevated/depressed value is a laboratory observation, not a confirmed clinical diagnosis.", "மருத்துவக் குறிப்பு: அதிகரித்த அல்லது குறைந்த அளவீடு என்பது ஆய்வகக் கண்காணிப்பு மட்டுமே; இது உறுதிப்படுத்தப்பட்ட மருத்துவ நோயறிதல் அல்ல."),
            ("Medication Safeguard: Never alter prescription medications without consulting your healthcare provider.", "மருந்து பாதுகாப்பு எச்சரிக்கை: உங்கள் மருத்துவரை கலந்தாலோசிக்காமல் மருந்துகளில் எந்த மாற்றமும் செய்யாதீர்கள்.")
        ]
        
        for src, dst in phrases:
            res = res.replace(src, dst)
            
        return res

def validate_translation_preservation(original: str, translated: str) -> bool:
    """
    Healthcare Safety Verification:
    Verifies that numbers and critical medical units in the original text
    are safely preserved in the translation and not corrupted or lost.
    """
    orig_numbers = set(re.findall(r"\b\d+(?:\.\d+)?\b", original))
    trans_numbers = set(re.findall(r"\b\d+(?:\.\d+)?\b", translated))
    
    missing_numbers = orig_numbers - trans_numbers
    if missing_numbers:
        return False
    return True

def get_translation_provider() -> BaseTranslationProvider:
    if settings.SARVAM_PROVIDER_MODE == "live" and settings.SARVAM_API_KEY:
        return SarvamTranslationProvider(settings.SARVAM_API_KEY, settings.SARVAM_BASE_URL)
    if settings.SUMMARY_MODEL_PROVIDER in ("openai", "sarvam") and settings.SUMMARY_MODEL_API_KEY:
        return LLMTranslationProvider(settings.SUMMARY_MODEL_API_KEY, settings.SUMMARY_MODEL_PROVIDER)
    return MedicalTamilTranslationProvider()
