"""
SQLite Durable Data Store & Document Storage Repository
Provides ACID-compliant persistent storage surviving server restarts,
mirroring the Supabase PostgreSQL production schema.
"""

import os
import json
import sqlite3
from pathlib import Path
from uuid import UUID
from datetime import datetime, date
from typing import Dict, Any, List, Optional

DB_DIR = Path(__file__).resolve().parent.parent.parent / "data"
STORAGE_DIR = DB_DIR / "storage"
DB_PATH = DB_DIR / "health_copilot.db"

class PersistentDataStore:
    def __init__(self):
        os.makedirs(DB_DIR, exist_ok=True)
        os.makedirs(STORAGE_DIR, exist_ok=True)
        self.conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_db_schema()
        self._seed_if_empty()

    def _init_db_schema(self):
        cursor = self.conn.cursor()
        cursor.executescript("""
        CREATE TABLE IF NOT EXISTS patients (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            full_name TEXT NOT NULL,
            date_of_birth TEXT,
            gender TEXT,
            blood_group TEXT,
            contact_phone TEXT,
            email TEXT,
            emergency_contact TEXT,
            preferred_language TEXT DEFAULT 'en',
            created_at TEXT,
            updated_at TEXT
        );

        CREATE TABLE IF NOT EXISTS documents (
            id TEXT PRIMARY KEY,
            patient_id TEXT NOT NULL,
            storage_path TEXT,
            original_filename TEXT,
            mime_type TEXT,
            file_size_bytes INTEGER,
            document_type TEXT,
            document_date TEXT,
            processing_status TEXT,
            error_message TEXT,
            created_at TEXT,
            updated_at TEXT
        );

        CREATE TABLE IF NOT EXISTS extractions (
            id TEXT PRIMARY KEY,
            document_id TEXT NOT NULL UNIQUE,
            raw_ocr_text TEXT,
            structured_candidate_data TEXT,
            extraction_provider TEXT,
            provider_model TEXT,
            validation_status TEXT,
            review_status TEXT,
            created_at TEXT,
            updated_at TEXT
        );

        CREATE TABLE IF NOT EXISTS observations (
            id TEXT PRIMARY KEY,
            patient_id TEXT NOT NULL,
            document_id TEXT,
            health_record_id TEXT,
            code TEXT,
            display_name TEXT NOT NULL,
            value_numeric REAL,
            value_text TEXT,
            unit TEXT,
            reference_low REAL,
            reference_high REAL,
            source_abnormal_flag TEXT,
            effective_at TEXT,
            validation_status TEXT,
            created_at TEXT
        );

        CREATE TABLE IF NOT EXISTS medications (
            id TEXT PRIMARY KEY,
            patient_id TEXT NOT NULL,
            document_id TEXT,
            medication_name TEXT NOT NULL,
            generic_name TEXT,
            strength TEXT,
            dose_instructions TEXT,
            route TEXT,
            frequency TEXT,
            duration TEXT,
            prescription_date TEXT,
            medication_status TEXT,
            review_status TEXT,
            created_at TEXT
        );

        CREATE TABLE IF NOT EXISTS summaries (
            key TEXT PRIMARY KEY,
            id TEXT NOT NULL,
            document_id TEXT NOT NULL,
            language TEXT NOT NULL,
            overview TEXT,
            key_findings TEXT,
            abnormal_explanations TEXT,
            questions_for_doctor TEXT,
            limitations TEXT,
            safety_disclaimer TEXT,
            created_at TEXT
        );

        CREATE TABLE IF NOT EXISTS abha_links (
            patient_id TEXT PRIMARY KEY,
            id TEXT NOT NULL,
            provider TEXT,
            environment TEXT,
            external_reference TEXT,
            status TEXT,
            verification_method TEXT,
            verified_at TEXT,
            created_at TEXT,
            updated_at TEXT
        );

        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT,
            details TEXT,
            created_at TEXT
        );
        """)
        self.conn.commit()

    def _seed_if_empty(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM patients")
        if cursor.fetchone()[0] == 0:
            patient_id = "00000000-0000-0000-0000-000000000001"
            user_id = "00000000-0000-0000-0000-000000000001"
            now_iso = datetime.now().isoformat()
            
            # Seed Patient
            cursor.execute("""
            INSERT INTO patients (id, user_id, full_name, date_of_birth, gender, blood_group, contact_phone, email, emergency_contact, preferred_language, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                patient_id, user_id, "Ananya Sharma", "1988-06-14", "female", "B+",
                "+91-98765-43210", "ananya.sharma@example.internal", "+91-98765-12345 (Spouse)",
                "en", "2026-01-15T10:00:00", "2026-09-20T10:00:00"
            ))

            # Seed Documents
            doc1_id = "30000000-0000-0000-0000-000000000001"
            doc2_id = "30000000-0000-0000-0000-000000000002"
            doc3_id = "30000000-0000-0000-0000-000000000003"
            
            cursor.execute("""
            INSERT INTO documents (id, patient_id, storage_path, original_filename, mime_type, file_size_bytes, document_type, document_date, processing_status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (doc1_id, patient_id, "patient_001/docs/lipid_glucose_panel_2026.pdf", "lipid_glucose_panel_2026.pdf", "application/pdf", 245890, "lab_report", "2026-09-15", "completed", "2026-09-15T09:30:00", "2026-09-15T09:35:00"))

            cursor.execute("""
            INSERT INTO documents (id, patient_id, storage_path, original_filename, mime_type, file_size_bytes, document_type, document_date, processing_status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (doc2_id, patient_id, "patient_001/docs/doctor_prescription_sep2026.jpg", "doctor_prescription_sep2026.jpg", "image/jpeg", 524100, "prescription", "2026-09-18", "completed", "2026-09-18T11:00:00", "2026-09-18T11:05:00"))

            cursor.execute("""
            INSERT INTO documents (id, patient_id, storage_path, original_filename, mime_type, file_size_bytes, document_type, document_date, processing_status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (doc3_id, patient_id, "patient_001/docs/cbc_baseline_2026.pdf", "cbc_baseline_2026.pdf", "application/pdf", 198400, "lab_report", "2026-03-10", "completed", "2026-03-10T08:30:00", "2026-03-10T08:35:00"))

            # Save sample file bytes
            with open(STORAGE_DIR / f"{doc1_id}.bin", "wb") as f:
                f.write(b"%PDF-1.4 [Synthetic Lipid & Fasting Blood Sugar Report Content]")
            with open(STORAGE_DIR / f"{doc2_id}.bin", "wb") as f:
                f.write(b"[Synthetic Doctor Prescription Image Content]")
            with open(STORAGE_DIR / f"{doc3_id}.bin", "wb") as f:
                f.write(b"%PDF-1.4 [Synthetic Baseline Lab Report Content]")

            # Seed Extraction for Doc 1
            ext1_id = "40000000-0000-0000-0000-000000000001"
            cand_data = {
                "document_type": "lab_report",
                "document_date": "2026-09-15",
                "healthcare_provider": "Metro Diagnostics & Labs, Chennai",
                "practitioner_name": "Dr. Meera Krishnan, MD",
                "observations": [
                    {"id": "obs-1", "test_name": "Fasting Blood Glucose", "value_numeric": 138, "unit": "mg/dL", "reference_low": 70, "reference_high": 99, "source_abnormal_flag": "H", "confidence": "high", "validation_status": "verified", "source_text": "Fasting Blood Glucose: 138 mg/dL (70-99) [H]"},
                    {"id": "obs-2", "test_name": "HbA1c", "value_numeric": 7.4, "unit": "%", "reference_low": 4.0, "reference_high": 5.6, "source_abnormal_flag": "H", "confidence": "high", "validation_status": "verified", "source_text": "HbA1c: 7.4 % (4.0-5.6) [H]"},
                    {"id": "obs-3", "test_name": "Total Cholesterol", "value_numeric": 228, "unit": "mg/dL", "reference_low": 125, "reference_high": 200, "source_abnormal_flag": "H", "confidence": "high", "validation_status": "verified", "source_text": "Total Cholesterol: 228 mg/dL (125-200) [H]"},
                    {"id": "obs-4", "test_name": "HDL Cholesterol", "value_numeric": 46, "unit": "mg/dL", "reference_low": 40, "reference_high": 60, "source_abnormal_flag": "NORMAL", "confidence": "high", "validation_status": "verified", "source_text": "HDL Cholesterol: 46 mg/dL (40-60) [NORMAL]"},
                    {"id": "obs-5", "test_name": "LDL Cholesterol", "value_numeric": 142, "unit": "mg/dL", "reference_low": 0, "reference_high": 100, "source_abnormal_flag": "H", "confidence": "high", "validation_status": "verified", "source_text": "LDL Cholesterol: 142 mg/dL (<100) [H]"}
                ],
                "medications": [],
                "unreadable_segments": []
            }
            cursor.execute("""
            INSERT INTO extractions (id, document_id, raw_ocr_text, structured_candidate_data, extraction_provider, provider_model, validation_status, review_status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                ext1_id, doc1_id, "METRO DIAGNOSTICS & LABS, CHENNAI\nFasting Blood Glucose: 138 mg/dL\nHbA1c: 7.4%",
                json.dumps(cand_data), "sarvam", "sarvam-doc-intelligence-v1", "high_confidence", "approved",
                "2026-09-15T09:32:00", "2026-09-15T09:35:00"
            ))

            # Seed Observations
            obs_seed = [
                ("50000000-0000-0000-0000-000000000001", doc1_id, "1558-6", "Fasting Blood Glucose", 138, "mg/dL", 70, 99, "H", "2026-09-15T08:00:00"),
                ("50000000-0000-0000-0000-000000000002", doc1_id, "4548-4", "HbA1c", 7.4, "%", 4.0, 5.6, "H", "2026-09-15T08:00:00"),
                ("50000000-0000-0000-0000-000000000003", doc1_id, "2093-3", "Total Cholesterol", 228, "mg/dL", 125, 200, "H", "2026-09-15T08:00:00"),
                ("50000000-0000-0000-0000-000000000004", doc1_id, "2085-9", "HDL Cholesterol", 46, "mg/dL", 40, 60, "NORMAL", "2026-09-15T08:00:00"),
                ("50000000-0000-0000-0000-000000000005", doc1_id, "13457-7", "LDL Cholesterol", 142, "mg/dL", 0, 100, "H", "2026-09-15T08:00:00"),
                ("50000000-0000-0000-0000-000000000006", doc3_id, "1558-6", "Fasting Blood Glucose", 114, "mg/dL", 70, 99, "H", "2026-03-10T08:00:00"),
                ("50000000-0000-0000-0000-000000000007", doc3_id, "4548-4", "HbA1c", 6.6, "%", 4.0, 5.6, "H", "2026-03-10T08:00:00"),
                ("50000000-0000-0000-0000-000000000008", doc3_id, "2093-3", "Total Cholesterol", 210, "mg/dL", 125, 200, "H", "2026-03-10T08:00:00"),
            ]
            for oid, did, code, name, val, unit, rlow, rhigh, flag, eff in obs_seed:
                cursor.execute("""
                INSERT INTO observations (id, patient_id, document_id, code, display_name, value_numeric, value_text, unit, reference_low, reference_high, source_abnormal_flag, effective_at, validation_status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (oid, patient_id, did, code, name, val, str(val), unit, rlow, rhigh, flag, eff, "validated", eff))

            # Seed Medications
            med_seed = [
                ("60000000-0000-0000-0000-000000000001", doc2_id, "Glycomet 500 SR", "Metformin Hydrochloride", "500 mg", "1 tab with dinner", "oral", "Once daily", "90 days", "2026-09-18", "active"),
                ("60000000-0000-0000-0000-000000000002", doc2_id, "Telma 40", "Telmisartan", "40 mg", "1 tab in morning after food", "oral", "Once daily", "90 days", "2026-09-18", "active"),
                ("60000000-0000-0000-0000-000000000003", doc2_id, "Atorva 10", "Atorvastatin Calcium", "10 mg", "1 tab at bedtime", "oral", "Once daily at night", "90 days", "2026-09-18", "prescribed"),
            ]
            for mid, did, mname, gname, strn, dose, rt, freq, dur, pdate, mstatus in med_seed:
                cursor.execute("""
                INSERT INTO medications (id, patient_id, document_id, medication_name, generic_name, strength, dose_instructions, route, frequency, duration, prescription_date, medication_status, review_status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (mid, patient_id, did, mname, gname, strn, dose, rt, freq, dur, pdate, mstatus, "confirmed", "2026-09-18T11:00:00"))

            # Seed Summaries
            sum1_en_id = "80000000-0000-0000-0000-000000000001"
            cursor.execute("""
            INSERT INTO summaries (key, id, document_id, language, overview, key_findings, abnormal_explanations, questions_for_doctor, limitations, safety_disclaimer, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                f"{doc1_id}_en", sum1_en_id, doc1_id, "en",
                "This laboratory report from Metro Diagnostics dated 15 Sep 2026 details your Fasting Blood Glucose, HbA1c, and Lipid Panel measurements.",
                json.dumps([
                    "Fasting Blood Glucose is recorded at 138 mg/dL (Reference: 70 - 99 mg/dL).",
                    "HbA1c is recorded at 7.4% (Reference: 4.0 - 5.6%).",
                    "Total Cholesterol is 228 mg/dL and LDL is 142 mg/dL, both elevated above standard laboratory cutoffs.",
                    "HDL Cholesterol is 46 mg/dL, within the desirable range."
                ]),
                json.dumps([
                    {"test_name": "Fasting Blood Glucose", "value": "138 mg/dL", "reference": "70 - 99 mg/dL", "status": "Above Reference Range", "plain_explanation": "Blood sugar after overnight fasting. Elevated levels indicate that insulin handling may need review with your clinician."},
                    {"test_name": "HbA1c", "value": "7.4%", "reference": "4.0 - 5.6%", "status": "Above Reference Range", "plain_explanation": "Reflects average blood sugar control over the past 2 to 3 months."},
                    {"test_name": "LDL Cholesterol", "value": "142 mg/dL", "reference": "< 100 mg/dL", "status": "Above Reference Range", "plain_explanation": "Often referred to as low-density lipoprotein; elevated levels are considered in cardiovascular risk assessments."}
                ]),
                json.dumps([
                    "Should my diabetes medication be adjusted based on the current HbA1c of 7.4%?",
                    "Do I need dietary changes or medication for elevated LDL cholesterol (142 mg/dL)?",
                    "When should I repeat these blood tests?"
                ]),
                "This summary is based solely on the values printed in the provided laboratory report. Clinical diagnosis requires comprehensive medical evaluation.",
                "INFORMATIONAL ASSISTANCE ONLY: This tool is not a doctor, diagnostic system, or emergency service. Never alter prescription medications without consulting your healthcare provider.",
                "2026-09-15T09:35:00"
            ))

            sum1_ta_id = "80000000-0000-0000-0000-000000000002"
            cursor.execute("""
            INSERT INTO summaries (key, id, document_id, language, overview, key_findings, abnormal_explanations, questions_for_doctor, limitations, safety_disclaimer, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                f"{doc1_id}_ta", sum1_ta_id, doc1_id, "ta",
                "இது 15 செப்டம்பர் 2026 அன்று மெட்ரோ டயக்னாஸ்டிக்ஸ் ஆய்வகத்தால் வழங்கப்பட்ட உண்ணாநிலை இரத்த சர்க்கரை, HbA1c மற்றும் கொழுப்பு அளவுகளின் பரிசோதனை அறிக்கை.",
                json.dumps([
                    "உண்ணாநிலை இரத்த சர்க்கரை அளவு 138 mg/dL ஆக பதிவாகியுள்ளது (இயல்பு வரம்பு: 70 - 99 mg/dL).",
                    "HbA1c அளவு 7.4% ஆக உள்ளது (இயல்பு வரம்பு: 4.0 - 5.6%).",
                    "மொத்த கொலஸ்ட்ரால் 228 mg/dL மற்றும் LDL கொலஸ்ட்ரால் 142 mg/dL ஆக இயல்பு வரம்பை விட அதிகமாக உள்ளன."
                ]),
                json.dumps([
                    {"test_name": "Fasting Blood Glucose", "value": "138 mg/dL", "reference": "70 - 99 mg/dL", "status": "இயல்பு வரம்பை விட அதிகம்", "plain_explanation": "இரவு உணவுக்குப் பிறகு காலையில் எடுக்கப்படும் இரத்த சர்க்கரை அளவு."},
                    {"test_name": "HbA1c", "value": "7.4%", "reference": "4.0 - 5.6%", "status": "இயல்பு வரம்பை விட அதிகம்", "plain_explanation": "கடந்த 2 முதல் 3 மாதங்களின் சராசரி இரத்த சர்க்கரை அளவைக் குறிக்கிறது."}
                ]),
                json.dumps([
                    "எனது தற்போதைய HbA1c 7.4% அடிப்படையில் சர்க்கரை நோய் மருந்துகளை மாற்ற வேண்டுமா?",
                    "அடுத்த பரிசோதனையை எப்போது மேற்கொள்ள வேண்டும்?"
                ]),
                "இந்த விளக்கம் வழங்கப்பட்ட ஆய்வக அறிக்கையில் உள்ள தகவல்களை மட்டுமே அடிப்படையாகக் கொண்டது.",
                "தகவல் உதவி மட்டுமே: இந்த செயலி மருத்துவரோ அல்லது அவசர சிகிச்சை முறையோ அல்ல. உங்கள் மருத்துவரை கலந்தாலோசிக்காமல் மருந்துகளில் எந்த மாற்றமும் செய்யாதீர்கள்.",
                "2026-09-15T09:36:00"
            ))

            # Seed ABHA Link
            cursor.execute("""
            INSERT INTO abha_links (patient_id, id, provider, environment, external_reference, status, verification_method, verified_at, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                patient_id, "90000000-0000-0000-0000-000000000001", "mock", "sandbox", "MOCK-ABHA-0001", "linked", "simulated_otp",
                "2026-09-20T10:00:00", "2026-09-20T10:00:00", "2026-09-20T10:00:00"
            ))

            self.conn.commit()

    # --- Collection-like mapping properties for transparent integration ---
    @property
    def patients(self):
        return _TableProxy(self.conn, "patients", id_col="id", is_json=False)

    @property
    def documents(self):
        return _TableProxy(self.conn, "documents", id_col="id", is_json=False)

    @property
    def extractions(self):
        return _TableProxy(self.conn, "extractions", id_col="document_id", is_json=True, json_cols=["structured_candidate_data"])

    @property
    def observations(self):
        return _TableProxy(self.conn, "observations", id_col="id", is_json=False)

    @property
    def medications(self):
        return _TableProxy(self.conn, "medications", id_col="id", is_json=False)

    @property
    def summaries(self):
        return _TableProxy(self.conn, "summaries", id_col="key", is_json=True, json_cols=["key_findings", "abnormal_explanations", "questions_for_doctor"])

    @property
    def abha_links(self):
        return _TableProxy(self.conn, "abha_links", id_col="patient_id", is_json=False)

    @property
    def document_files(self):
        return _FileStorageProxy(STORAGE_DIR)

    @property
    def audit_logs(self):
        return _AuditLogsProxy(self.conn)


class _TableProxy:
    def __init__(self, conn, table_name: str, id_col: str = "id", is_json: bool = False, json_cols: List[str] = None):
        self.conn = conn
        self.table_name = table_name
        self.id_col = id_col
        self.is_json = is_json
        self.json_cols = json_cols or []

    def _convert_row(self, row: sqlite3.Row) -> Dict[str, Any]:
        d = dict(row)
        for col in self.json_cols:
            if col in d and isinstance(d[col], str):
                try:
                    d[col] = json.loads(d[col])
                except Exception:
                    pass
        # Convert UUID strings back to UUID instances for id/patient_id
        for id_field in ["id", "patient_id", "document_id", "user_id"]:
            if id_field in d and isinstance(d[id_field], str):
                try:
                    d[id_field] = UUID(d[id_field])
                except Exception:
                    pass
        # Convert date/datetime fields
        for dt_field in ["created_at", "updated_at", "effective_at", "verified_at"]:
            if dt_field in d and isinstance(d[dt_field], str):
                try:
                    d[dt_field] = datetime.fromisoformat(d[dt_field])
                except Exception:
                    pass
        for date_field in ["date_of_birth", "document_date", "prescription_date"]:
            if date_field in d and isinstance(d[date_field], str):
                try:
                    d[date_field] = date.fromisoformat(d[date_field])
                except Exception:
                    pass
        return d

    def get(self, key: Any, default=None):
        str_key = str(key)
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT * FROM {self.table_name} WHERE {self.id_col} = ?", (str_key,))
        row = cursor.fetchone()
        if not row:
            return default
        return self._convert_row(row)

    def __getitem__(self, key: Any):
        res = self.get(key)
        if res is None:
            raise KeyError(f"Key {key} not found in {self.table_name}")
        return res

    def __setitem__(self, key: Any, value: Dict[str, Any]):
        str_key = str(key)
        val_copy = dict(value)
        # Serialize fields
        for col in self.json_cols:
            if col in val_copy and not isinstance(val_copy[col], str):
                val_copy[col] = json.dumps(val_copy[col], default=str)
        for k, v in val_copy.items():
            if isinstance(v, (UUID, datetime, date)):
                val_copy[k] = v.isoformat() if hasattr(v, "isoformat") else str(v)
        
        # Ensure id/key column is set
        val_copy[self.id_col] = str_key
        
        cols = list(val_copy.keys())
        placeholders = [":" + c for c in cols]
        update_clauses = [f"{c} = excluded.{c}" for c in cols if c != self.id_col]
        
        sql = f"""
        INSERT INTO {self.table_name} ({', '.join(cols)})
        VALUES ({', '.join(placeholders)})
        ON CONFLICT({self.id_col}) DO UPDATE SET
        {', '.join(update_clauses)}
        """
        cursor = self.conn.cursor()
        cursor.execute(sql, val_copy)
        self.conn.commit()

    def __contains__(self, key: Any) -> bool:
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT 1 FROM {self.table_name} WHERE {self.id_col} = ?", (str(key),))
        return cursor.fetchone() is not None

    def __delitem__(self, key: Any):
        cursor = self.conn.cursor()
        cursor.execute(f"DELETE FROM {self.table_name} WHERE {self.id_col} = ?", (str(key),))
        self.conn.commit()

    def values(self) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT * FROM {self.table_name}")
        return [self._convert_row(r) for r in cursor.fetchall()]

    def items(self):
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT * FROM {self.table_name}")
        rows = cursor.fetchall()
        for r in rows:
            yield (r[self.id_col], self._convert_row(r))

    def __iter__(self):
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT {self.id_col} FROM {self.table_name}")
        for r in cursor.fetchall():
            yield r[0]

    def __len__(self):
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {self.table_name}")
        return cursor.fetchone()[0]


class _FileStorageProxy:
    def __init__(self, storage_dir: Path):
        self.storage_dir = storage_dir

    def get(self, doc_id: Any, default=None):
        file_path = self.storage_dir / f"{str(doc_id)}.bin"
        if not file_path.exists():
            return default
        with open(file_path, "rb") as f:
            return f.read()

    def __getitem__(self, doc_id: Any) -> bytes:
        res = self.get(doc_id)
        if res is None:
            raise KeyError(f"File for document {doc_id} not found")
        return res

    def __setitem__(self, doc_id: Any, file_bytes: bytes):
        file_path = self.storage_dir / f"{str(doc_id)}.bin"
        with open(file_path, "wb") as f:
            f.write(file_bytes)

    def __contains__(self, doc_id: Any) -> bool:
        return (self.storage_dir / f"{str(doc_id)}.bin").exists()

    def __delitem__(self, doc_id: Any):
        file_path = self.storage_dir / f"{str(doc_id)}.bin"
        if file_path.exists():
            file_path.unlink()


class _AuditLogsProxy:
    def __init__(self, conn):
        self.conn = conn

    def append(self, log_entry: Dict[str, Any]):
        cursor = self.conn.cursor()
        action = log_entry.get("action", "system_event")
        details = json.dumps(log_entry.get("details", {}))
        now_str = datetime.now().isoformat()
        cursor.execute("INSERT INTO audit_logs (action, details, created_at) VALUES (?, ?, ?)", (action, details, now_str))
        self.conn.commit()

    def __iter__(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM audit_logs ORDER BY id DESC")
        for r in cursor.fetchall():
            yield dict(r)

    def __len__(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM audit_logs")
        return cursor.fetchone()[0]
