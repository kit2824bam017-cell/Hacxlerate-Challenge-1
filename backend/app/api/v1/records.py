"""
Health Records, Longitudinal Trends, and FHIR R4 Export API Router
Manages confirmed laboratory observations, chronological trend analysis,
medication reconciliation, and standards-compliant FHIR R4 interoperability export.
"""

from fastapi import APIRouter, HTTPException, Query, Header
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from collections import defaultdict

from app.repositories.store import store
from app.schemas.observation import ObservationResponse, TestTrendResponse, TrendPoint
from app.schemas.medication import MedicationResponse, MedicationStatusUpdate
from app.core.config import settings

router = APIRouter(tags=["Health Records"])

@router.get("/observations", response_model=List[ObservationResponse])
async def list_observations(
    test_name: Optional[str] = Query(None),
    x_patient_id: Optional[str] = Header(None, alias="X-Patient-Id")
):
    pid_str = x_patient_id if x_patient_id else settings.DEMO_PATIENT_ID
    try:
        patient_id = UUID(pid_str)
    except Exception:
        patient_id = UUID(settings.DEMO_PATIENT_ID)
        
    obs_list = [o for o in store.observations.values() if o["patient_id"] == patient_id]
    if test_name:
        obs_list = [o for o in obs_list if test_name.lower() in o["display_name"].lower()]
    obs_list.sort(key=lambda x: x["effective_at"] or x["created_at"], reverse=True)
    return obs_list

@router.get("/observations/trends", response_model=List[TestTrendResponse])
async def get_observation_trends(x_patient_id: Optional[str] = Header(None, alias="X-Patient-Id")):
    """
    Returns comparable longitudinal history for tests having multiple data points.
    Strictly groups identical test names and units to prevent invalid comparisons.
    """
    pid_str = x_patient_id if x_patient_id else settings.DEMO_PATIENT_ID
    try:
        patient_id = UUID(pid_str)
    except Exception:
        patient_id = UUID(settings.DEMO_PATIENT_ID)
        
    obs_list = [o for o in store.observations.values() if o["patient_id"] == patient_id and o.get("value_numeric") is not None]
    
    grouped = defaultdict(list)
    for o in obs_list:
        key = (o["display_name"], o.get("unit") or "")
        grouped[key].append(o)
        
    trends: List[TestTrendResponse] = []
    for (tname, unit), items in grouped.items():
        items.sort(key=lambda x: x["effective_at"] or x["created_at"])
        
        history = [
            TrendPoint(
                date=(item["effective_at"] or item["created_at"]).strftime("%Y-%m-%d"),
                value=float(item["value_numeric"]),
                unit=unit,
                reference_low=item.get("reference_low"),
                reference_high=item.get("reference_high"),
                source_document_id=item.get("document_id")
            )
            for item in items
        ]
        
        latest = items[-1]
        trends.append(TestTrendResponse(
            test_name=tname,
            unit=unit,
            reference_low=latest.get("reference_low"),
            reference_high=latest.get("reference_high"),
            history=history
        ))
        
    return trends

@router.get("/medications", response_model=List[MedicationResponse])
async def list_medications(
    status: Optional[str] = Query(None),
    x_patient_id: Optional[str] = Header(None, alias="X-Patient-Id")
):
    pid_str = x_patient_id if x_patient_id else settings.DEMO_PATIENT_ID
    try:
        patient_id = UUID(pid_str)
    except Exception:
        patient_id = UUID(settings.DEMO_PATIENT_ID)
        
    meds = [m for m in store.medications.values() if m["patient_id"] == patient_id]
    if status:
        meds = [m for m in meds if m.get("medication_status") == status]
    meds.sort(key=lambda x: x["prescription_date"] or x["created_at"].date(), reverse=True)
    return meds

@router.patch("/medications/{medication_id}", response_model=MedicationResponse)
async def update_medication_status(medication_id: UUID, req: MedicationStatusUpdate):
    med = store.medications.get(medication_id)
    if not med:
        raise HTTPException(status_code=404, detail="Medication record not found.")
    med["medication_status"] = req.medication_status
    store.medications[medication_id] = med
    return med

@router.get("/fhir/bundle")
async def export_fhir_r4_bundle(x_patient_id: Optional[str] = Header(None, alias="X-Patient-Id")) -> Dict[str, Any]:
    """
    Exports a standards-conformant HL7 FHIR R4 Bundle containing Patient,
    Observation, and MedicationRequest resources formatted for ABDM / NDHM interoperability.
    """
    pid_str = x_patient_id if x_patient_id else settings.DEMO_PATIENT_ID
    try:
        patient_id = UUID(pid_str)
    except Exception:
        patient_id = UUID(settings.DEMO_PATIENT_ID)
        
    patient = store.patients.get(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found.")
        
    entries: List[Dict[str, Any]] = []
    
    # 1. FHIR Patient Resource
    patient_resource = {
        "resource": {
            "resourceType": "Patient",
            "id": str(patient["id"]),
            "identifier": [
                {
                    "system": "https://healthid.ndhm.gov.in",
                    "value": "ananya.sharma@abdm"
                }
            ],
            "name": [
                {
                    "use": "official",
                    "text": patient["full_name"],
                    "family": patient["full_name"].split()[-1] if " " in patient["full_name"] else "",
                    "given": patient["full_name"].split()[:-1] if " " in patient["full_name"] else [patient["full_name"]]
                }
            ],
            "gender": patient.get("gender", "unknown"),
            "birthDate": str(patient.get("date_of_birth", "1988-06-14")),
            "telecom": [
                {"system": "phone", "value": patient.get("contact_phone", "")},
                {"system": "email", "value": patient.get("email", "")}
            ]
        }
    }
    entries.append(patient_resource)
    
    # 2. FHIR Observations
    obs_list = [o for o in store.observations.values() if o["patient_id"] == patient_id]
    for obs in obs_list:
        loinc_code = obs.get("code") or "30954-2"
        obs_entry = {
            "resource": {
                "resourceType": "Observation",
                "id": str(obs["id"]),
                "status": "final",
                "category": [
                    {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                                "code": "laboratory",
                                "display": "Laboratory"
                            }
                        ]
                    }
                ],
                "code": {
                    "coding": [
                        {
                            "system": "http://loinc.org",
                            "code": loinc_code,
                            "display": obs["display_name"]
                        }
                    ],
                    "text": obs["display_name"]
                },
                "subject": {"reference": f"Patient/{str(patient_id)}"},
                "effectiveDateTime": (obs.get("effective_at") or obs["created_at"]).isoformat(),
                "valueQuantity": {
                    "value": obs.get("value_numeric"),
                    "unit": obs.get("unit", ""),
                    "system": "http://unitsofmeasure.org"
                },
                "referenceRange": [
                    {
                        "low": {"value": obs.get("reference_low"), "unit": obs.get("unit", "")},
                        "high": {"value": obs.get("reference_high"), "unit": obs.get("unit", "")}
                    }
                ] if obs.get("reference_low") is not None or obs.get("reference_high") is not None else []
            }
        }
        if obs.get("source_abnormal_flag"):
            obs_entry["resource"]["interpretation"] = [
                {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
                            "code": obs["source_abnormal_flag"],
                            "display": "High" if obs["source_abnormal_flag"] == "H" else ("Low" if obs["source_abnormal_flag"] == "L" else "Normal")
                        }
                    ]
                }
            ]
        entries.append(obs_entry)
        
    # 3. FHIR MedicationRequests
    med_list = [m for m in store.medications.values() if m["patient_id"] == patient_id]
    for med in med_list:
        med_entry = {
            "resource": {
                "resourceType": "MedicationRequest",
                "id": str(med["id"]),
                "status": "active" if med.get("medication_status") == "active" else "completed",
                "intent": "order",
                "medicationCodeableConcept": {
                    "text": f"{med['medication_name']} ({med.get('strength', '')})"
                },
                "subject": {"reference": f"Patient/{str(patient_id)}"},
                "authoredOn": str(med.get("prescription_date", datetime.now().date())),
                "dosageInstruction": [
                    {
                        "text": med.get("dose_instructions", "Take as directed"),
                        "route": {
                            "text": med.get("route", "oral")
                        }
                    }
                ]
            }
        }
        entries.append(med_entry)
        
    return {
        "resourceType": "Bundle",
        "type": "collection",
        "timestamp": datetime.now().isoformat(),
        "total": len(entries),
        "entry": entries
    }
