import uuid
from datetime import datetime
from typing import Dict, Any, List
from uuid import UUID

from app.repositories.store import store
from app.providers.translation import get_translation_provider, validate_translation_preservation

SAFETY_DISCLAIMER_EN = (
    "INFORMATIONAL ASSISTANCE ONLY: This tool is not a doctor, diagnostic system, or emergency service. "
    "Never alter prescription medications without consulting your healthcare provider."
)

SAFETY_DISCLAIMER_TA = (
    "தகவல் உதவி மட்டுமே: இந்த செயலி மருத்துவரோ அல்லது அவசர சிகிச்சை முறையோ அல்ல. "
    "உங்கள் மருத்துவரை கலந்தாலோசிக்காமல் மருந்துகளில் எந்த மாற்றமும் செய்யாதீர்கள்."
)

async def generate_evidence_grounded_summary(document_id: UUID, candidate_data: Dict[str, Any]) -> Dict[str, Any]:
    doc_type = candidate_data.get("document_type", "lab_report")
    provider = candidate_data.get("healthcare_provider") or "Healthcare Provider"
    doc_date = candidate_data.get("document_date") or str(datetime.now().date())
    
    observations = candidate_data.get("observations", [])
    medications = candidate_data.get("medications", [])
    
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
            plain_exp = _get_plain_explanation(tname, "high", val_str)
            abnormal_explanations.append({
                "test_name": tname,
                "value": val_str,
                "reference": ref_str,
                "status": status_text,
                "plain_explanation": plain_exp
            })
            questions_for_doctor.append(f"What might be contributing to my elevated {tname} ({val_str})?")
        elif is_below:
            status_text = "Below Reference Range"
            key_findings.append(f"{tname} is recorded at {val_str} (Reference: {ref_str}) [Below Range].")
            plain_exp = _get_plain_explanation(tname, "low", val_str)
            abnormal_explanations.append({
                "test_name": tname,
                "value": val_str,
                "reference": ref_str,
                "status": status_text,
                "plain_explanation": plain_exp
            })
            questions_for_doctor.append(f"Should my low {tname} reading ({val_str}) be re-tested?")
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
        questions_for_doctor.append(f"Are there any specific dietary precautions while taking {mname}?")

    # Overview formulation
    if doc_type == "prescription":
        overview = f"Outpatient prescription from {provider} issued on {doc_date} outlining recommended medications."
    else:
        overview = f"Laboratory diagnostic report from {provider} dated {doc_date} detailing measured biomarkers."
        
    if not questions_for_doctor:
        questions_for_doctor = [
            "Are there lifestyle or dietary adjustments recommended based on these findings?",
            "When should follow-up diagnostic tests be scheduled?"
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
        "limitations": "This summary is based solely on the values printed in the provided document. Clinical diagnosis requires comprehensive medical evaluation.",
        "safety_disclaimer": SAFETY_DISCLAIMER_EN,
        "created_at": datetime.now()
    }
    store.summaries[f"{document_id}_en"] = summary_record_en
    
    # Auto-generate Tamil translation
    await translate_summary_to_tamil(document_id, summary_record_en)
    
    return summary_record_en

def _get_plain_explanation(test_name: str, direction: str, val_str: str) -> str:
    name_l = test_name.lower()
    if "glucose" in name_l or "sugar" in name_l:
        return "Measures sugar levels in the bloodstream. Elevated values suggest insulin handling should be reviewed with your doctor."
    elif "hba1c" in name_l:
        return "Reflects average blood sugar control over the past 2 to 3 months. Elevated values warrant consultation on glycemic management."
    elif "cholesterol" in name_l or "triglyceride" in name_l or "ldl" in name_l:
        return "Measures circulating lipid/fat levels in the blood. Elevated concentrations are evaluated in cardiovascular risk assessments."
    elif "hemoglobin" in name_l:
        if direction == "low":
            return "Protein in red blood cells that carries oxygen. Lower levels can indicate mild anemia or iron deficiency."
        return "Carries oxygen throughout the body."
    return f"This measured parameter is {direction}er than the laboratory reference range. Discuss contextual implications with your doctor."

async def translate_summary_to_tamil(document_id: UUID, en_summary: Dict[str, Any]) -> Dict[str, Any]:
    trans_provider = get_translation_provider()
    
    overview_ta = await trans_provider.translate_text(en_summary["overview"], "en", "ta")
    
    key_findings_ta = []
    for kf in en_summary["key_findings"]:
        t_kf = await trans_provider.translate_text(kf, "en", "ta")
        # Validate numerical preservation
        if not validate_translation_preservation(kf, t_kf):
            t_kf = kf  # Fallback to source English text for patient safety
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
