# Devpost Submission Details

**Hackathon**: AWS Communication Developer Services (CDS) Agentic AI Partner Hackathon  
**Track**: General Submission & Meta WhatsApp Prize  
**Project Title**: **DAXDA CareFlow CDS: Autonomous Omnichannel Healthcare Agent on AWS Communication Developer Services**  
**Tagline / Elevator Pitch**: An autonomous, HIPAA-governed conversational healthcare agent powered by Amazon Bedrock AgentCore that seamlessly routes patient engagement across AWS End User Messaging (SMS, RCS, WhatsApp) and Amazon SES without losing conversational context.

---

## 1. Project Information & Metadata

| Field | Detail |
| :--- | :--- |
| **Project Title** | DAXDA CareFlow CDS |
| **Participant / Partner** | DAXDA AI Inc. (AWS Partner Network) |
| **Primary Contact** | `dexter@daxda.ai` |
| **AWS Partner Central ACE Campaign Code** | `AWS CDS Agentic AI Hackathon -Sept. 2026` |
| **License** | Apache License 2.0 (Open Source) |
| **Repository URL** | Public GitHub / GitLab: `https://github.com/daxda-ai/daxda-careflow-cds` |
| **Testing Collaborators Invited** | `testing@devpost.com`, `aws-cds-partner@amazon.com` |
| **Target Prize Categories** | Overall AWS CDS Hackathon Grand Prize ($40,000 pool), Meta WhatsApp Prize |

---

## 2. Inspiration

For decades, enterprise customer communication on AWS has been dominated by one-way notifications, one-time passwords (OTPs), and brittle, rules-based IVR trees. When a patient receives an SMS prescription reminder, they are forced to leave the messaging app, download a hospital portal, or wait on hold for a pharmacist. 

If they respond to the SMS, the message vanishes into an unmonitored inbox. If they switch from SMS to WhatsApp or check their email, the context is shattered, requiring the customer to start over from scratch.

When AWS announced the **AWS Communication Developer Services (CDS) Agentic AI Partner Hackathon**, Dexter and the DAXDA team realized this was the exact moment to break through the legacy notification paradigm. We asked:

> *What if an autonomous AI agent treated SMS, RCS, WhatsApp, and SES not as isolated silos, but as a single, fluid conversational canvas—picking up instantly where the last channel left off, remembering every clinical detail, and executing verified actions in real time?*

Thus, **DAXDA CareFlow CDS** was born.

---

## 3. What It Does

DAXDA CareFlow CDS is an autonomous healthcare communication system that transforms fragmented notifications into a closed-loop clinical conversation across four AWS CDS channels:

```
[Channel 1: AWS EUM SMS]       --> Proactive Refill Alert & 2-Way Adherence Question
            │
            ▼
[Channel 2: AWS EUM RCS]       --> Rich Card Carousel of Nearby Pharmacies & Tap-to-Navigate
            │
            ▼
[Channel 3: AWS EUM WhatsApp]  --> Interactive Buttons, Drug Interaction Check & Prescription Photo
            │
            ▼
[Channel 4: Amazon SES]        --> Responsive Clinical Summary, Pickup Fast-Pass QR & SHA-256 Receipt
```

### End-to-End Patient Journey:
1. **AWS End User Messaging SMS**:
   - The patient receives a personalized adherence reminder: *"Hi Sarah, your Lisinopril 10mg refill is ready. Would you like to pick it up or transfer to a closer location?"*
   - Sarah replies via natural language: *"I'm downtown near 5th St today, can I pick it up there?"*
2. **Seamless Escalation to AWS End User Messaging RCS**:
   - Detecting the need for rich visual selection, the agent sends an RCS Rich Card Carousel featuring real-time pharmacy options with thumbnail images, operating hours, stock counts, and 1-tap interactive action chips (`Select Pharmacy`, `Open Map`, `Call Pharmacist`).
   - Sarah taps `Select Downtown Pharmacy`.
3. **Clinical Deep-Dive on AWS End User Messaging Social (WhatsApp)**:
   - Sarah prefers WhatsApp for personal questions and asks: *"Can I take this with ibuprofen? I have a slight headache."*
   - Amazon Bedrock AgentCore invokes the `check_drug_interactions` action group tool, detecting a moderate risk (NSAID + ACE inhibitor) and advising: *"Lisinopril with ibuprofen may reduce blood pressure efficacy and stress renal function. Acetaminophen is clinically preferred. Shall I add it to your pickup order?"*
   - Interactive WhatsApp Quick-Reply buttons allow 1-tap confirmation: `[Confirm Refill]`, `[Switch to Delivery]`, `[Talk to Pharmacist]`.
   - Sarah snaps and uploads a photo of her insurance card / bottle for zero-entry verification.
4. **Amazon Simple Email Service (SES)**:
   - The agent schedules the pickup slot via `schedule_pickup_slot`, locks inventory via `pharmacy_inventory_lookup`, and triggers Amazon SES.
   - Sarah immediately receives an enterprise-grade, responsive HTML email containing:
     - Verified clinical summary and dosage schedule
     - One-time dynamic pickup fast-pass code (`RX-94821-B`) and QR code
     - Turn-by-turn driving directions to 452 5th Avenue
     - Immutable SHA-256 audit receipt guaranteeing HIPAA data provenance.

---

## 4. Technical Architecture & How We Built It

The solution is architected as an event-driven, agentic microservices topology deployed on AWS:

### 1. Communications Backbone (AWS CDS)
- **AWS End User Messaging SMS (`pinpoint-sms-voice-v2`)**: Manages high-throughput, carrier-compliant two-way SMS messaging with opt-out keyword support (`STOP`, `HELP`).
- **AWS End User Messaging RCS**: Constructs rich interactive RCS cards, carousels, and suggestion chips (`OPEN_URL`, `DIAL_PHONE`, `VIEW_LOCATION`, `SUGGESTED_REPLY`).
- **AWS End User Messaging Social (WhatsApp)**: Integrates directly with the Meta Cloud API for WhatsApp Business Platform, handling structured interactive buttons, lists, and inbound media (prescription images).
- **Amazon Simple Email Service (SES)**: Renders accessible, responsive HTML clinical receipts with DKIM/SPF signatures and TLS 1.3 delivery.

### 2. Autonomous Agent Intelligence (Amazon Bedrock AgentCore)
- **Foundation Model**: Anthropic Claude 3.5 Sonnet on Amazon Bedrock.
- **Bedrock Action Groups**:
  - `pharmacy_inventory_lookup`: Live check of medication SKU, NDC code, unit availability, and pharmacy stock across national networks.
  - `schedule_pickup_slot`: Real-time calendar reservation with locker/counter slot allocation.
  - `check_drug_interactions`: Clinical pharmacology safety engine scoring severity levels (`NONE`, `MODERATE`, `CONTRAINDICATED`).
  - `dispatch_omnichannel_handoff`: Autonomous routing trigger determining when conversation state warrants channel switching.

### 3. DAXDA 16-Layer Sentinel Policy Enforcement Point (PEP)
- Healthcare demands rigorous zero-trust compliance. DAXDA Sentinel sits as an inline gate between the AI Agent and the AWS CDS communication adapters:
  - **Automated PHI/PII Scrubbing**: Regex + NER filters detecting and masking Social Security Numbers, credit cards, and sensitive medical record numbers before transmission across public networks.
  - **Controlled Substance NPI Verification**: Restricts scheduling of Schedule II-IV medications without verified physician DEA/NPI validation.
  - **Audit Provenance**: Every inbound message and outbound dispatch creates a cryptographically signed SHA-256 audit trail logged to Amazon CloudWatch and Amazon S3.

---

## 5. Challenges We Ran Into

1. **Cross-Channel Session Fragmentation**:
   - *Problem*: Traditional messaging architectures treat an incoming SMS from `+12065550199` and an incoming WhatsApp message from the same number as completely separate sessions, losing all prior dialog context.
   - *Solution*: We engineered `OmnichannelCDSRouter` with unified identity resolution. All channel events append to an immutable `event_stream` keyed by patient identity, passing the entire history to Bedrock AgentCore at every reasoning step.

2. **Carrier RCS Fallback & Device Diversity**:
   - *Problem*: Not all patient handsets have RCS enabled or supported by their carrier.
   - *Solution*: Implemented an intelligent downgrade waterfall: if an RCS dispatch returns an unroutable status code, the router automatically re-encodes the rich payload into an SMS message with an authenticated micro-portal deep link, then prompts for WhatsApp escalation.

3. **HIPAA & PII Leakage Over Cellular Channels**:
   - *Problem*: Generative models may inadvertently output raw patient identifiers or unmasked clinical history over unencrypted SMS.
   - *Solution*: Developed the fail-closed `DAXDASentinelPEP` which intercepts every outbound message. If any sensitive unmasked pattern is detected, the payload is sanitized and redacted prior to calling the AWS CDS SDK.

---

## 6. Accomplishments That We're Proud Of

- **13/13 Automated Tests Passing**: Comprehensive unit, integration, and security test suite covering all four AWS CDS services in 0.07s.
- **Zero-Context-Loss Omnichannel Routing**: Demonstrated full 4-channel transitions (SMS ➔ RCS ➔ WhatsApp ➔ SES) with Bedrock AgentCore remembering all details across turns without prompting the user twice.
- **Live Interactive 4-Channel Simulator**: Built a full-stack, browser-based multi-phone laboratory running on port 8085 that visually demonstrates concurrent SMS, RCS, WhatsApp, and SES devices in real time.
- **Production-Ready Enterprise Security**: Native fail-closed HIPAA governance with cryptographically verified audit receipts.

---

## 7. What We Learned

- **AWS CDS is a Force Multiplier**: Unifying SMS, RCS, and WhatsApp under AWS End User Messaging eliminates the nightmare of juggling disparate third-party aggregators, billing accounts, and proprietary SDKs.
- **Agentic AI Needs Strict Action Group Boundaries**: Allowing Bedrock AgentCore to autonomously decide *when* to execute actions (like inventory checks or scheduling) makes the experience feel genuinely human, while OpenAPI action schemas keep execution 100% deterministic and safe.
- **RCS and WhatsApp are Changing Healthcare**: Interactive action chips and rich card carousels drive significantly higher conversion and adherence than plain text links.

---

## 8. What's Next for DAXDA CareFlow CDS

1. **AWS Marketplace Repeatable Offering**:
   - Packaging DAXDA CareFlow CDS as an AWS QuickStart / CloudFormation solution for health systems and retail pharmacy chains.
   - AWS Marketplace Listing targeting healthcare payers and pharmacy benefit managers (PBMs).
2. **EHR Integration via HL7 / FHIR**:
   - Native integration with Epic, Cerner, and Athenahealth for automatic bidirectional record synchronization.
3. **Voice Escalation via Amazon Connect**:
   - Adding 1-tap "Talk to Pharmacist" handoffs that bridge directly into Amazon Connect with pre-transferred agent screen-pop context.
4. **AWS Specialist GTM Collaboration**:
   - Co-selling with AWS Healthcare & Life Sciences specialists using our registered AWS Customer Engagement (ACE) opportunity (`AWS CDS Agentic AI Hackathon -Sept. 2026`).

---

## 9. Built With

- **AWS End User Messaging (EUM)**:
  - SMS (`pinpoint-sms-voice-v2`)
  - RCS (`Rich Communication Services`)
  - Social (WhatsApp Meta Cloud API)
- **Amazon Simple Email Service (SES)**
- **Amazon Bedrock AgentCore**
- **Anthropic Claude 3.5 Sonnet**
- **DAXDA Sentinel 16-Layer PEP**
- **Python 3.11 & Boto3**
- **Pytest**
- **HTML5 / CSS3 / Vanilla JavaScript Web Simulator**

---

## 10. Try It Out / Verification Instructions

### Fast Local Quickstart:
```bash
# 1. Clone repository
git clone https://github.com/daxda-ai/daxda-careflow-cds.git
cd daxda-careflow-cds

# 2. Run automated test suite
pytest tests/test_omnichannel_cds.py -v

# 3. Launch interactive 4-channel web simulator
python3 web_simulator/server.py 8085
```
Open `http://localhost:8085` in any modern web browser to interact with the live SMS, RCS, WhatsApp, and SES simulators side-by-side.
