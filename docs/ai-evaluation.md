# AI-Powered Personal Health Copilot - AI & OCR Evaluation Methodology

## 1. Evaluation Framework

To avoid unsupported accuracy claims, extraction and summarization quality are evaluated against a verified ground-truth test suite consisting of synthetic, de-identified Indian medical records:
- **Synthetic Printed Lab Panels**: Complete Blood Count (CBC), Lipid Panel, Liver Function Tests (LFT), Fasting Blood Glucose & HbA1c.
- **Synthetic Doctor Prescriptions**: Outpatient prescription slips containing brand names, strengths, frequencies (OD, BD, TDS), and handwritten notes.
- **Synthetic Discharge Summaries**: Hospital discharge reports with admission/discharge dates, primary diagnoses, and medication recommendations.

---

## 2. Key Metrics & Ground-Truth Verification

| Evaluation Dimension | Measurement Method | Verification Criterion |
|---|---|---|
| **Field Extraction Accuracy** | Exact match vs Levenshtein distance on test names | > 95% on printed lab reports |
| **Numerical Value & Unit Precision** | Strict equality check | 100% preservation (no numeric loss or unit corruption) |
| **Reference Range Parsing** | Lower and upper interval comparison | Accurate numeric boundary segmentation |
| **Abnormal Flag Fidelity** | Printed 'H' / 'L' matching | Matches source report without hallucinating danger |
| **Medication Extraction** | Drug brand vs generic identification | Explicit separation of strength and frequency |
| **Bilingual Translation Grounding** | Named-entity and numerical preservation | All numbers, units, and drug names preserved in Tamil |
| **Uncertainty Calibration** | Unreadable handwriting detection | Flagged as `needs_review` instead of hallucinated |

---

## 3. Evaluation Pipeline Execution

The automated evaluation suite is executed via:
```bash
python -m pytest backend/tests/test_ai_evaluation.py -v
```

The test suite validates:
1. Extraction fidelity on synthetic lab panels
2. Extraction fidelity on synthetic prescriptions
3. Summary grounding (no unmentioned diagnoses or medications)
4. Tamil translation safety (number, unit, and drug preservation)
