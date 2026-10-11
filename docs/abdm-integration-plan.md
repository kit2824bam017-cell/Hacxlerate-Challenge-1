# AI-Powered Personal Health Copilot - ABDM / ABHA Integration Architecture & Pathway

## 1. Executive Summary
The Ayushman Bharat Digital Mission (ABDM) promotes an interoperable digital health ecosystem across India through:
1. **ABHA (Ayushman Bharat Health Account)**: A 14-digit national health identity enabling citizens to link, store, and share digital health records.
2. **HRP (Health Repository Provider) & HIP/HIU (Health Information Provider / User)**: Decentralized standards-based health information exchange orchestrated via the ABDM Gateway.
3. **FHIR R4**: Standardized clinical resource packaging (`DiagnosticReport`, `Prescription / MedicationRequest`, `DischargeSummary`, `OPConsultation`).

---

## 2. Mock vs Sandbox vs Production Architecture

To adhere strictly to healthcare safety and challenge constraints without making unverified claims:
- **Active Prototype Mode (`ABHA_PROVIDER=mock`)**: An explicitly simulated sandbox workflow displaying clearly fictional identifiers (e.g. `MOCK-ABHA-0001`). It demonstrates the complete citizen-facing linking and revocation experience with 0 false claims.
- **Pluggable Provider Pattern (`ABHAProvider`)**:
  ```python
  class ABHAProvider(ABC):
      @abstractmethod
      async def initiate_link(self, patient_id: UUID, abha_id: str) -> dict: ...
      @abstractmethod
      async def verify_otp(self, patient_id: UUID, transaction_id: str, otp: str) -> dict: ...
      @abstractmethod
      async def get_status(self, patient_id: UUID) -> dict: ...
      @abstractmethod
      async def revoke_link(self, patient_id: UUID) -> dict: ...
  ```

---

## 3. Official ABDM Gateway Integration Roadmap

When official sandbox access and National Health Authority (NHA) credentials (`client_id`, `client_secret`) are provisioned:

```mermaid
sequenceDiagram
    autonumber
    actor Patient as Citizen
    participant App as Copilot Backend
    participant Gateway as ABDM Gateway (dev.abdm.gov.in)
    participant HIP as Hospital / Diagnostic Lab HIP

    Note over App, Gateway: Milestone 1: Milestone M1 (ABHA Creation & Verification)
    Patient->>App: Enter 14-digit ABHA or Mobile
    App->>Gateway: POST /v1/registration/aadhaar/generateOtp
    Gateway-->>Patient: OTP SMS
    Patient->>App: Enter OTP
    App->>Gateway: POST /v1/registration/aadhaar/verifyOTP
    Gateway-->>App: X-Token & ABHA Profile (ABHA Address, ABHA Number)
    App->>App: Store verified external_reference (Never raw OTP/Aadhaar)

    Note over App, Gateway: Milestone 2: Milestone M2 (Consent Management & HIP Linking)
    Gateway->>App: HIP Discovery & Link Request
    App->>Patient: Request Patient Consent for Health Data Exchange
    Patient->>App: Consent Granted (Purpose, Expiry, Resource Scope)
    App->>Gateway: POST /v0.5/consent-requests/on-init (Consent Artifact)

    Note over App, HIP: Milestone 3: Milestone M3 (Health Data Transfer via FHIR)
    Gateway->>HIP: POST /v0.5/consents/hip/notify
    App->>HIP: POST /v0.5/health-information/hip/request (Encrypted ECDH Key)
    HIP-->>App: Transmit Bundled FHIR R4 Records
    App->>App: Decrypt, Normalize & Ingest into Health Timeline
```

---

## 4. FHIR R4 Resource Mapping Layer

The prototype persists all extracted medical facts in FHIR-compatible structures:
- **`DiagnosticReport`**: Laboratory investigations and clinical impressions
- **`Observation`**: Individual quantitative metrics (`Fasting Blood Glucose`, `HbA1c`, `Total Cholesterol`) referencing LOINC coding systems and numerical boundaries
- **`MedicationRequest`**: Prescriptions containing dosage timing, duration, and practitioner references
- **`Encounter`**: Clinic visits, outpatient consultations, and hospital encounters
