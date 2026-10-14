# System Architecture & Technical Specifications

**Project**: DAXDA CareFlow CDS  
**Hackathon**: AWS Communication Developer Services (CDS) Agentic AI Partner Hackathon  
**Document**: Architecture Topology, Data Flows, and Sequence Specifications  

---

## 1. High-Level Architecture Topology

The following diagram illustrates the complete end-to-end cloud topology of DAXDA CareFlow CDS, linking patient client endpoints, AWS Communication Developer Services, the Omnichannel Router, DAXDA Sentinel Governance, and Amazon Bedrock AgentCore:

```mermaid
graph TB
    subgraph Patients["Patient Channels & Devices"]
        P_SMS["📱 Handset 1: Cellular SMS<br/>(Carrier Network)"]
        P_RCS["📱 Handset 2: Rich RCS Client<br/>(Google Messages / Samsung)"]
        P_WA["💬 Handset 3: WhatsApp Client<br/>(Meta Cloud Network)"]
        P_EMAIL["✉️ Handset 4: Patient Mailbox<br/>(Email / IMAP / Web)"]
    end

    subgraph AWS_CDS["AWS Communication Developer Services (CDS)"]
        EUM_SMS["AWS End User Messaging SMS<br/>pinpoint-sms-voice-v2"]
        EUM_RCS["AWS End User Messaging RCS<br/>Rich Cards, Carousels, Action Chips"]
        EUM_WA["AWS End User Messaging Social<br/>WhatsApp Business Platform (Meta API)"]
        SES["Amazon Simple Email Service (SES)<br/>Responsive HTML, TLS 1.3, DKIM/SPF"]
    end

    subgraph Gateway["Ingress / Egress API Gateway"]
        API_GW["Amazon API Gateway / Webhooks<br/>TLS Termination & Signature Validation"]
    end

    subgraph Governance["DAXDA Sentinel HIPAA Security Boundary"]
        PEP["DAXDA Sentinel 16-Layer PEP<br/>• Automated PHI/PII Redactor<br/>• Controlled Substance NPI Checker<br/>• SHA-256 Audit Provenance Engine"]
    end

    subgraph Core["Omnichannel Orchestration Core"]
        ROUTER["OmnichannelCDSRouter<br/>Cross-Channel Identity Resolution<br/>Unified Event Stream Engine"]
        SESSION_DB[("Amazon DynamoDB<br/>Omnichannel Sessions & State")]
    end

    subgraph AgentCore["Agentic AI Decision Layer"]
        BEDROCK["Amazon Bedrock AgentCore<br/>Anthropic Claude 3.5 Sonnet<br/>Multi-Turn Autonomous Reasoning"]
        
        subgraph ActionGroups["Bedrock Action Groups"]
            AG_INV["pharmacy_inventory_lookup<br/>Real-Time Pharmacy Stock & NDC"]
            AG_SCHED["schedule_pickup_slot<br/>Locker / Counter Reservation"]
            AG_DRUG["check_drug_interactions<br/>Clinical Pharmacology Engine"]
            AG_HANDOFF["dispatch_omnichannel_handoff<br/>Channel Escalation Trigger"]
        end
    end

    subgraph Backends["Enterprise Healthcare Systems"]
        EHR[("Hospital EHR / Epic / FHIR")]
        AUDIT_LOG[("Amazon S3 & CloudWatch<br/>Immutable Audit Vault")]
    end

    %% Inbound / Outbound Links
    P_SMS <-->|SMS Cellular| EUM_SMS
    P_RCS <-->|RCS Data| EUM_RCS
    P_WA <-->|HTTPS/WSS| EUM_WA
    SES -->|SMTP / TLS| P_EMAIL

    EUM_SMS <--> API_GW
    EUM_RCS <--> API_GW
    EUM_WA <--> API_GW
    API_GW <--> PEP

    PEP <--> ROUTER
    ROUTER <--> SESSION_DB
    ROUTER <--> BEDROCK

    BEDROCK --> AG_INV
    BEDROCK --> AG_SCHED
    BEDROCK --> AG_DRUG
    BEDROCK --> AG_HANDOFF

    AG_INV <--> EHR
    AG_SCHED <--> EHR
    PEP --> AUDIT_LOG
    ROUTER --> SES
```

---

## 2. End-to-End Cross-Channel Sequence Flow

The following sequence diagram details the full cross-channel handoff workflow, showing how conversational state is preserved seamlessly across SMS, RCS, WhatsApp, and SES:

```mermaid
sequenceDiagram
    autonumber
    actor Patient as 👤 Patient (Sarah)
    participant SMS as 📱 EUM SMS
    participant RCS as 📲 EUM RCS
    participant WA as 💬 EUM WhatsApp
    participant SES as ✉️ Amazon SES
    participant Router as 🧭 Omnichannel Router
    participant Sentinel as 🛡️ DAXDA Sentinel PEP
    participant Bedrock as 🧠 Bedrock AgentCore
    participant ActionGroups as ⚙️ Clinical Tools / Action Groups

    %% Phase 1: SMS
    Note over Patient,SMS: Phase 1: Proactive Adherence Prompt (SMS)
    Router->>SMS: Outbound Refill Reminder
    SMS-->>Patient: "Hi Sarah, your Lisinopril 10mg refill is ready. Pick up or transfer?"
    Patient->>SMS: "I'm downtown near 5th St today, can I pick it up there?"
    SMS->>Router: Inbound SMS webhook (+12065550199)
    Router->>Sentinel: Inbound PHI Scan & Tokenization
    Sentinel->>Bedrock: Process user inquiry with historical context
    Bedrock->>ActionGroups: pharmacy_inventory_lookup(medication="Lisinopril", location="Downtown 5th St")
    ActionGroups-->>Bedrock: Stock: 42 bottles at 452 5th Ave
    Bedrock-->>Router: Trigger RCS Escalation with Rich Carousel Options

    %% Phase 2: RCS
    Note over Patient,RCS: Phase 2: Rich Media Selection & Geolocation (RCS)
    Router->>Sentinel: Sanitize Outbound RCS Payload
    Sentinel->>RCS: SendMediaMessage (Rich Carousel of 2 Pharmacies + Action Chips)
    RCS-->>Patient: Render Rich Card (Photos, Map Pin, "Select Downtown", "Call")
    Patient->>RCS: Tap [Select Downtown Pharmacy]
    RCS->>Router: Inbound Action Callback (choice="Downtown 5th St")
    Router->>Bedrock: Update session state (target_pharmacy="Downtown 5th St")

    %% Phase 3: WhatsApp
    Note over Patient,WA: Phase 3: Conversational Clinical Deep-Dive (WhatsApp)
    Patient->>WA: "Can I take this with ibuprofen? I have a slight headache."
    WA->>Router: Inbound WhatsApp Message (+12065550199)
    Router->>Sentinel: PHI / PII Scan & Verification
    Sentinel->>Bedrock: Multi-turn clinical reasoning (Current Rx: Lisinopril, Inquiry: Ibuprofen)
    Bedrock->>ActionGroups: check_drug_interactions("Lisinopril", "Ibuprofen")
    ActionGroups-->>Bedrock: MODERATE: ACE inhibitor + NSAID reduces antihypertensive effect
    Bedrock-->>Router: Formulate clinical advice + Quick-Reply Buttons
    Router->>Sentinel: Outbound PII Redaction
    Sentinel->>WA: Send Interactive Button Message
    WA-->>Patient: "Lisinopril + Ibuprofen may stress kidney function. Acetaminophen preferred. Confirm Refill?"<br/>[Confirm Refill] [Talk to Pharmacist]
    Patient->>WA: Tap [Confirm Refill]
    WA->>Router: Button Payload ("CONFIRM_REFILL")
    Router->>Bedrock: Autonomous Finalization
    Bedrock->>ActionGroups: schedule_pickup_slot(pharmacy_id="PHARM_5TH_DOWNTOWN", time="Today 4:00 PM")
    ActionGroups-->>Bedrock: Confirmed slot #LOCKER-12

    %% Phase 4: SES Email
    Note over Patient,SES: Phase 4: Finalized Care Plan & Pickup Fast-Pass (Amazon SES)
    Bedrock->>Router: Final Dispatch Event (Receipt + QR + Clinical Summary)
    Router->>Sentinel: Generate Cryptographic SHA-256 Audit Seal
    Sentinel->>SES: SendEmail (HTML Template with Fast-Pass QR Code)
    SES-->>Patient: Deliver Clinical Care Plan & Barcode Pass to sarah.patient@example.com
```

---

## 3. Core Component Specifications

### 3.1 Omnichannel Session Orchestrator (`OmnichannelCDSRouter`)
- **Session Identification**: Combines E.164 phone numbers (`+12065550199`) and verified email addresses (`sarah.patient@example.com`) into a unified `patient_id`.
- **Event Sourcing**: Rather than maintaining fragile state flags, all user actions, inbound texts, outbound carousels, button clicks, and action group outputs append to an immutable `event_stream`.
- **Channel Switching Engine**: Evaluates payload type and context to select the most cost-effective and engaging CDS channel:
  - Text prompts ➔ **SMS**
  - Multi-option comparisons / maps ➔ **RCS**
  - Clinical discussions / rich interactive flows ➔ **WhatsApp**
  - Formal receipts / clinical summaries / legal disclosures ➔ **SES**

### 3.2 Amazon Bedrock AgentCore
- **Foundation Model**: `anthropic.claude-3-5-sonnet-20241022-v2:0`
- **Inference Mode**: Multi-turn dialogue with memory buffer and tool use.
- **Action Group Schemas**:
  1. `pharmacy_inventory_lookup(medication, dosage, zip_code, radius_miles)`
  2. `schedule_pickup_slot(patient_id, pharmacy_id, slot_time, medication)`
  3. `check_drug_interactions(primary_drug, proposed_drug)`
  4. `dispatch_omnichannel_handoff(target_channel, reason, payload_preview)`

### 3.3 DAXDA Sentinel HIPAA Security Boundary
The DAXDA Sentinel Policy Enforcement Point (PEP) operates under a **Zero-Trust, Fail-Closed** paradigm:
- **SSN & Financial Masking**: Pattern recognition redacting `XXX-XX-XXXX` and standard credit card formats (`(?:\d{4}[- ]?){3}\d{4}`).
- **Controlled Substance NPI Gating**: Checks medications against DEA Schedule II-V lists. If detected without an authorized prescriber NPI, the booking is held for manual clinician verification.
- **Audit Provenance Engine**: Computes SHA-256 digests over:
  ```
  Digest = SHA256(SessionID + Timestamp + Channel + InboundPayload + OutboundPayload + Salt)
  ```
  Logged synchronously to Amazon CloudWatch and cold-vaulted in Amazon S3 Object Lock for 7 years.

---

## 4. AWS Services & Implementation Matrix

| AWS Service | Role in DAXDA CareFlow CDS | API / SDK Methods Used |
| :--- | :--- | :--- |
| **AWS End User Messaging SMS** | High-throughput outbound adherence triggers & inbound conversational replies | `boto3.client('pinpoint-sms-voice-v2')`<br/>`send_text_message()` |
| **AWS End User Messaging RCS** | Rich cards, 3-card carousels, action chips (`OPEN_URL`, `DIAL_PHONE`, `VIEW_LOCATION`) | `boto3.client('pinpoint-sms-voice-v2')`<br/>`send_media_message()` |
| **AWS End User Messaging Social** | WhatsApp Business Platform integration: interactive buttons, photo intake, two-way dialog | Meta Graph API via AWS EUM Social webhook endpoints |
| **Amazon Simple Email Service (SES)** | Responsive HTML clinical receipts, pickup fast-pass codes, QR codes, HIPAA disclosures | `boto3.client('sesv2')`<br/>`send_email()` |
| **Amazon Bedrock AgentCore** | Autonomous agentic reasoning, intent extraction, tool calling, conversational memory | `boto3.client('bedrock-agent-runtime')`<br/>`invoke_agent()` |
| **Amazon DynamoDB** | Low-latency omnichannel session store and cross-channel message buffer | `boto3.resource('dynamodb')` |
| **Amazon CloudWatch & S3** | Cryptographic audit logging and HIPAA compliance retention | CloudWatch Logs & S3 Object Lock |

---

## 5. Security, Privacy & Compliance Architecture

```
+-------------------------------------------------------------------------+
|                  ENTERPRISE ZERO-TRUST SECURITY PERIMETER               |
|                                                                         |
|   +-----------------------+                 +-----------------------+   |
|   |   In Transit:         |                 |   At Rest:            |   |
|   |   • TLS 1.3 Strict    |                 |   • AWS KMS (CMK)     |   |
|   |   • Mutual TLS (mTLS) |                 |   • AES-256-GCM       |   |
|   |   • API HMAC-SHA256   |                 |   • S3 Object Lock    |   |
|   +-----------------------+                 +-----------------------+   |
|                                                                         |
|   +-----------------------------------------------------------------+   |
|   |              DAXDA 16-Layer Sentinel Policy Engine              |   |
|   |   Layer 1-4:   Regex & Token-Level PHI Redactor                |   |
|   |   Layer 5-8:   Controlled Substance NPI Prescriber Gate        |   |
|   |   Layer 9-12:  Cross-Channel Session Nonce Verification        |   |
|   |   Layer 13-16: SHA-256 Audit Seal & Compliance Archival         |   |
|   +-----------------------------------------------------------------+   |
+-------------------------------------------------------------------------+
```
