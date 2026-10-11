"""
Evidence-Grounded AI Medical Health Summary Service
Synthesizes plain-language health explanations grounded strictly in extracted report evidence.
Supports live LLM invocation (OpenAI / Sarvam) and an advanced Clinical Inference Engine
with strict safety guardrails distinguishing laboratory flags from clinical diagnoses,
preserving all units and reference intervals, and strictly avoiding medication alterations.
"""

import uuid
import json
import httpx
from datetime import datetime
from typing import Dict, Any, List, Optional
from uuid import UUID

from app.core.config import settings
from app.repositories.store import store
from app.providers.translation import get_translation_provider, validate_translation_preservation

SAFETY_DISCLAIMER_EN = (
    "INFORMATIONAL ASSISTANCE ONLY: This tool is not a doctor, diagnostic system, or emergency service. "
    "Clinical Note: An abnormal laboratory result is an isolated test flag, not a confirmed clinical diagnosis. "
    "Medication Safeguard: Never initiate, stop, or alter prescription medications without consulting your healthcare provider."
)

SAFETY_DISCLAIMER_TA = (
    "தகவல் உதவி மட்டுமே: இந்த செயலி மருத்துவரோ அல்லது அவசர சிகிச்சை முறையோ அல்ல. "
    "மருத்துவக் குறிப்பு: அதிகரித்த அல்லது குறைந்த அளவீடு என்பது ஆய்வகக் கண்காணிப்பு மட்டுமே; இது உறுதிப்படுத்தப்பட்ட மருத்துவ நோயறிதல் அல்ல. "
    "மருந்து பாதுகாப்பு எச்சரிக்கை: உங்கள் மருத்துவரை கலந்தாலோசிக்காமல் மருந்துகளில் எந்த மாற்றமும் செய்யாதீர்கள்."
)

CLINICAL_INTERPRETATION_MAP = {
    "glucose": {
        "system": "Glycemic Regulation",
        "high": "Measures sugar levels in the bloodstream. Indicates higher than normal glucose in plasma after fasting; elevated values suggest insulin handling should be reviewed with your doctor. Note: Elevated fasting glucose is an isolated laboratory flag, not an automatic diabetes diagnosis.",
        "low": "Measures sugar levels in the bloodstream. Indicates lower than normal plasma sugar concentrations (hypoglycemia). Can cause dizziness or shakiness and warrants discussing meal timing and medication balance with your doctor."
    },
    "hba1c": {
        "system": "Glycemic Control (3-Month Average)",
        "high": "Reflects elevated average blood glucose over the past 8 to 12 weeks. An elevated HbA1c is a clinical flag for glycemic review, but treatment planning requires individualized physician assessment.",
        "low": "Values within or below range reflect lower circulating glycated hemoglobin."
    },
    "cholesterol": {
        "system": "Cardiovascular Lipid Profile",
        "high": "Indicates elevated circulating total blood cholesterol. High lipid markers contribute to cardiovascular risk scoring but require clinical interpretation alongside blood pressure, lifestyle, and other factors.",
        "low": "Low circulating total cholesterol; generally discussed in context of overall nutritional profile."
    },
    "ldl": {
        "system": "Cardiovascular Lipid Profile (Atherogenic)",
        "high": "Elevated low-density lipoprotein (LDL), commonly termed atherogenic cholesterol. Elevated readings are reviewed by doctors to determine diet modifications or lipid-lowering pharmacotherapy.",
        "low": "Optimal low levels of low-density lipoproteins."
    },
    "hdl": {
        "system": "Cardiovascular Lipid Profile (Protective)",
        "high": "Higher high-density lipoprotein is generally considered cardiovascularly favorable.",
        "low": "Lower levels of protective high-density lipoprotein; lifestyle factors such as aerobic exercise and diet are frequently discussed with clinicians."
    },
    "triglyceride": {
        "system": "Circulating Blood Lipids",
        "high": "Elevated blood triglycerides. Commonly associated with dietary carbohydrate intake, metabolic state, or physical activity; discussed with clinicians during routine wellness checks.",
        "low": "Normal or low circulating triglyceride levels."
    },
    "hemoglobin": {
        "system": "Hematology & Oxygen Transport",
        "high": "Elevated hemoglobin concentration, occasionally observed in dehydration or high-altitude acclimation.",
        "low": "Lower than expected hemoglobin (indicative of anemia or iron insufficiency). May contribute to fatigue and warrants dietary or clinical iron evaluation."
    },
    "wbc": {
        "system": "Immune & Inflammatory Response",
        "high": "Elevated leukocyte count. Commonly signifies the body's immune response to an infection, inflammation, or physical stress.",
        "low": "Depressed white blood cell count; clinician review is recommended to assess immune resilience."
    },
    "platelet": {
        "system": "Hemostasis & Blood Clotting",
        "high": "Thrombocytosis (elevated platelets); evaluated by doctors for reactive inflammatory causes.",
        "low": "Thrombocytopenia (low platelets); important to review with a physician to evaluate clotting support and prevent bleeding risks."
    },
    "creatinine": {
        "system": "Renal Filtration (Kidney Function)",
        "high": "Elevated serum creatinine suggests reduced glomerular filtration rate in kidneys. Note: Creatinine can fluctuate with hydration and muscle mass; formal diagnosis requires a renal panel review by a physician.",
        "low": "Generally low clinical consequence; may reflect low muscle mass."
    },
    "bun": {
        "system": "Renal & Urea Cycle",
        "high": "Elevated blood urea nitrogen, reflecting protein breakdown or kidney clearance.",
        "low": "Low urea nitrogen; commonly associated with low dietary protein or high hydration."
    },
    "uric acid": {
        "system": "Purine Metabolism",
        "high": "Elevated serum uric acid (hyperuricemia); monitored in connection with joint discomfort (gout) or kidney stones.",
        "low": "Generally unremarkable."
    },
    "bilirubin": {
        "system": "Hepatic & Biliary Function",
        "high": "Elevated serum bilirubin. Indicates biliary clearance or red blood cell breakdown; physician review is advised to evaluate liver and gallbladder health.",
        "low": "Within expected baseline clearance."
    },
    "sgot": {
        "system": "Hepatic Enzyme (AST)",
        "high": "Elevated AST enzyme, released from liver and heart muscle tissues during cellular stress. Evaluated alongside other liver parameters.",
        "low": "Normal physiological concentration."
    },
    "sgpt": {
        "system": "Hepatic Enzyme (ALT)",
        "high": "Elevated ALT enzyme, a specific marker of liver hepatocellular sensitivity. Evaluated by doctors for fatty liver, medication effects, or metabolic factors.",
        "low": "Normal physiological concentration."
    },
    "tsh": {
        "system": "Endocrine & Thyroid Regulation",
        "high": "Elevated TSH suggests the pituitary is stimulating an underactive thyroid gland (hypothyroidism indicator). Confirmatory free T3/T4 testing and clinician evaluation are standard.",
        "low": "Low TSH suggests thyroid overactivity (hyperthyroidism indicator); requires endocrinological review."
    }
}

async def generate_evidence_grounded_summary(document_id: UUID, candidate_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generates evidence-grounded summary in English and translates to Tamil.
    If an external LLM is configured (OpenAI/Sarvam), calls the live model.
    Otherwise runs our robust Clinical Inference Engine with strict safeguards.
    """
    doc_type = candidate_data.get("document_type", "lab_report")
    provider = candidate_data.get("healthcare_provider") or "Healthcare Facility"
    doc_date = candidate_data.get("document_date") or str(datetime.now().date())
    
    observations = candidate_data.get("observations", [])
    medications = candidate_data.get("medications", [])
    
    # Try calling live LLM if configured
    if settings.SUMMARY_MODEL_PROVIDER in ("openai", "sarvam") and settings.SUMMARY_MODEL_API_KEY:
        llm_result = await _call_live_llm_summarizer(candidate_data)
        if llm_result:
            summary_id = uuid.uuid4()
            summary_record_en = {
                "id": summary_id,
                "document_id": document_id,
                "language": "en",
                "overview": llm_result.get("overview", ""),
                "key_findings": llm_result.get("key_findings", []),
                "abnormal_explanations": llm_result.get("abnormal_explanations", []),
                "questions_for_doctor": llm_result.get("questions_for_doctor", []),
                "limitations": llm_result.get("limitations", "Based solely on provided document evidence."),
                "safety_disclaimer": SAFETY_DISCLAIMER_EN,
                "created_at": datetime.now()
            }
            store.summaries[f"{document_id}_en"] = summary_record_en
            await translate_summary_to_tamil(document_id, summary_record_en)
            return summary_record_en

    # Local Clinical Inference Engine
    key_findings: List[str] = []
    abnormal_explanations: List[Dict[str, str]] = []
    questions_for_doctor: List[str] = []
    
    # 1. Analyze Observations
    for obs in observations:
        tname = obs.get("test_name", "")
        val = obs.get("value_numeric")
        unit = obs.get("unit") or ""
        rlow = obs.get("reference_low")
        rhigh = obs.get("reference_high")
        flag = obs.get("source_abnormal_flag")
        
        val_str = f"{val} {unit}".strip()
        ref_str = f"{rlow} - {rhigh} {unit}".strip() if (rlow is not None and rhigh is not None) else "Not stated"
        
        is_above = (rhigh is not None and val is not None and val > rhigh) or flag == "H"
        is_below = (rlow is not None and val is not None and val < rlow) or flag == "L"
        
        if is_above:
            status_text = "Above Reference Range"
            key_findings.append(f"{tname} is recorded at {val_str} (Reference: {ref_str}) [Above Range].")
            plain_exp = _get_plain_explanation(tname, "high", val_str, ref_str)
            abnormal_explanations.append({
                "test_name": tname,
                "value": val_str,
                "reference": ref_str,
                "status": status_text,
                "plain_explanation": plain_exp
            })
            questions_for_doctor.append(f"What factors might be contributing to my elevated {tname} reading ({val_str})?")
        elif is_below:
            status_text = "Below Reference Range"
            key_findings.append(f"{tname} is recorded at {val_str} (Reference: {ref_str}) [Below Range].")
            plain_exp = _get_plain_explanation(tname, "low", val_str, ref_str)
            abnormal_explanations.append({
                "test_name": tname,
                "value": val_str,
                "reference": ref_str,
                "status": status_text,
                "plain_explanation": plain_exp
            })
            questions_for_doctor.append(f"Should my low {tname} reading ({val_str}) be re-tested to rule out transient fluctuation?")
        else:
            key_findings.append(f"{tname} is recorded at {val_str}, within normal reference parameters.")

    # 2. Analyze Medications
    for med in medications:
        mname = med.get("medication_name", "")
        strn = med.get("strength") or ""
        dose = med.get("dose_instructions") or ""
        freq = med.get("frequency") or ""
        dur = med.get("duration") or ""
        key_findings.append(f"Prescribed {mname} ({strn}): {dose} ({freq}) for {dur}.")
        questions_for_doctor.append(f"Are there any specific dietary precautions or drug interactions to watch for while taking {mname}?")

    # Overview formulation
    if doc_type == "prescription":
        overview = f"Outpatient prescription from {provider} issued on {doc_date} outlining recommended medications and dosage regimens."
    else:
        overview = f"Laboratory diagnostic report from {provider} dated {doc_date} detailing measured biomarkers and physiological indices."
        
    if not questions_for_doctor:
        questions_for_doctor = [
            "Are there lifestyle or dietary adjustments recommended based on these findings?",
            "When should follow-up diagnostic monitoring be scheduled?"
        ]

    # Save English summary
    summary_id = uuid.uuid4()
    summary_record_en = {
        "id": summary_id,
        "document_id": document_id,
        "language": "en",
        "overview": overview,
        "key_findings": key_findings,
        "abnormal_explanations": abnormal_explanations,
        "questions_for_doctor": questions_for_doctor,
        "limitations": (
            "This health summary is based strictly on numbers printed in the provided document. "
            "Isolated lab flags are not clinical diagnoses. Formal diagnosis and treatment requires comprehensive evaluation by a licensed physician."
        ),
        "safety_disclaimer": SAFETY_DISCLAIMER_EN,
        "created_at": datetime.now()
    }
    store.summaries[f"{document_id}_en"] = summary_record_en
    
    # Auto-generate Tamil translation
    await translate_summary_to_tamil(document_id, summary_record_en)
    
    return summary_record_en

def _get_plain_explanation(test_name: str, direction: str, val_str: str, ref_str: str = "Standard Laboratory Reference") -> str:
    name_l = test_name.lower()
    for key, data in CLINICAL_INTERPRETATION_MAP.items():
        if key in name_l:
            exp = data.get(direction, "")
            return f"{exp} (Recorded: {val_str}, Lab Reference: {ref_str})."
            
    return (
        f"This measured parameter is {direction}er than the laboratory reference range of {ref_str}. "
        f"Laboratory flags reflect physiological concentration changes and require physician evaluation for context."
    )

async def _call_live_llm_summarizer(candidate_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Invokes external LLM API with strict medical grounding instructions.
    """
    prompt = (
        "You are an expert Clinical Health Copilot AI. Synthesize a plain-language health explanation "
        "strictly grounded in the extracted medical report data below.\n\n"
        "RULES:\n"
        "1. Never diagnose diseases: Explicitly distinguish lab flags from clinical diagnoses.\n"
        "2. Preserve all numerical values, units, and reference intervals verbatim.\n"
        "3. Never recommend altering or stopping medications.\n"
        "4. Output strictly valid JSON with keys: overview, key_findings (list), "
        "abnormal_explanations (list of {test_name, value, reference, status, plain_explanation}), "
        "questions_for_doctor (list), limitations (string).\n\n"
        f"DATA:\n{json.dumps(candidate_data, indent=2)}"
    )
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {settings.SUMMARY_MODEL_API_KEY}"},
                json={
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": "You are a medically grounded health copilot. Respond only in JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    "response_format": {"type": "json_object"},
                    "temperature": 0.2
                }
            )
            if resp.status_code == 200:
                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                return json.loads(content)
    except Exception:
        pass
    return None

async def translate_summary_to_tamil(document_id: UUID, en_summary: Dict[str, Any]) -> Dict[str, Any]:
    trans_provider = get_translation_provider()
    
    overview_ta = await trans_provider.translate_text(en_summary["overview"], "en", "ta")
    
    key_findings_ta = []
    for kf in en_summary["key_findings"]:
        t_kf = await trans_provider.translate_text(kf, "en", "ta")
        if not validate_translation_preservation(kf, t_kf):
            t_kf = kf
        key_findings_ta.append(t_kf)
        
    abnormal_ta = []
    for ab in en_summary["abnormal_explanations"]:
        p_exp = await trans_provider.translate_text(ab["plain_explanation"], "en", "ta")
        abnormal_ta.append({
            "test_name": ab["test_name"],
            "value": ab["value"],
            "reference": ab["reference"],
            "status": "இயல்பு வரம்பை விட அதிகம்" if "Above" in ab["status"] else "இயல்பு வரம்பை விட குறைவு",
            "plain_explanation": p_exp
        })
        
    questions_ta = []
    for q in en_summary["questions_for_doctor"]:
        t_q = await trans_provider.translate_text(q, "en", "ta")
        questions_ta.append(t_q)
        
    ta_summary_id = uuid.uuid4()
    summary_record_ta = {
        "id": ta_summary_id,
        "document_id": document_id,
        "language": "ta",
        "overview": overview_ta,
        "key_findings": key_findings_ta,
        "abnormal_explanations": abnormal_ta,
        "questions_for_doctor": questions_ta,
        "limitations": "இந்த விளக்கம் வழங்கப்பட்ட ஆவணத்தில் உள்ள தகவல்களை மட்டுமே அடிப்படையாகக் கொண்டது. மருத்துவ நோயறிதலுக்கு முறையான மருத்துவ பரிசோதனை அவசியம்.",
        "safety_disclaimer": SAFETY_DISCLAIMER_TA,
        "created_at": datetime.now()
    }
    
    store.summaries[f"{document_id}_ta"] = summary_record_ta
    return summary_record_ta
