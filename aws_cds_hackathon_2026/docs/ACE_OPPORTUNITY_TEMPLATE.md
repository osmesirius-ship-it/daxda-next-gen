# AWS Partner Central (ACE) Opportunity Registration

**Hackathon Requirement**: Mandatory Created Opportunity ID through AWS Partner Central's AWS Customer Engagement (ACE)  
**Required Marketing Campaign Code**: `AWS CDS Agentic AI Hackathon -Sept. 2026`  
**Partner Name**: DAXDA AI Inc.  
**Partner Network Status**: AWS Registered Partner / APN Member  
**Primary Contact**: Dexter, Lead Architect (`dexter@daxda.ai`)  

---

## 1. Opportunity Summary & Metadata

| Field | Partner Central (ACE) Value |
| :--- | :--- |
| **Opportunity Name** | `DAXDA CareFlow CDS - Omnichannel Healthcare Agent` |
| **Marketing Campaign Code** *(MANDATORY)* | **`AWS CDS Agentic AI Hackathon -Sept. 2026`** |
| **Partner Project Role** | Primary Solution Builder / ISV Software Provider |
| **Opportunity Stage** | Qualified / Prospecting (Ready for AWS Specialist Co-Sell) |
| **Estimated Close Date** | `Q1 2027` (March 31, 2027) |
| **Estimated Contract Value** | `$180,000 USD` (Annual Recurring SaaS + Professional Services) |
| **Estimated Monthly AWS Consumption** | `$12,500 USD / month` |
| **Primary Industry** | Healthcare and Life Sciences (HLS) |
| **Sub-Industry** | Health Systems, Digital Health, Retail Pharmacy Networks, PBMs |

---

## 2. Customer Information (Template / Pilot Account)

| ACE Customer Field | Data Value |
| :--- | :--- |
| **Customer Company Name** | `MetroHealth Regional Care System & Pharmacy Network` |
| **Customer Website** | `https://metrohealth-regional-demo.org` |
| **Customer Country** | United States |
| **Customer Postal Code** | 98101 (Seattle, WA) |
| **Customer Contact Title** | Chief Information Officer (CIO) / VP of Digital Patient Experience |
| **Customer Pain Point** | 42% prescription non-adherence rate; $4.2M annual loss in uncollected prescription copays; 68% patient abandonment of unmonitored SMS reminders; patient portal login friction. |

---

## 3. Solution Overview & Technical Scope

### 3.1 Solution Description
**DAXDA CareFlow CDS** is an enterprise-grade omnichannel healthcare communication platform that replaces static, unmonitored SMS/email notification blasts with an autonomous conversational agent powered by **Amazon Bedrock AgentCore** and **AWS Communication Developer Services (CDS)**.

The solution enables health systems and retail pharmacy chains to engage patients across **AWS End User Messaging SMS**, **AWS End User Messaging RCS**, **AWS End User Messaging Social (WhatsApp)**, and **Amazon Simple Email Service (SES)** within a single, continuous conversational thread. 

Conversational context is preserved across all channels, allowing patients to confirm refills, locate nearby pharmacy lockers via rich RCS carousels, ask clinical pharmacology questions over WhatsApp, and receive secure pickup barcodes via SES email without repeating information.

### 3.2 AWS Services Consumed in Deal
1. **AWS End User Messaging (EUM) SMS**: High-volume 10DLC / shortcode two-way adherence engagement.
2. **AWS End User Messaging (EUM) RCS**: Interactive rich card carousels, action chips, and geolocation routing.
3. **AWS End User Messaging Social (WhatsApp)**: WhatsApp Business Platform integration for clinical drug interaction queries and prescription photo intake.
4. **Amazon Simple Email Service (SES)**: Responsive HTML care plans, pickup fast-pass barcodes, and HIPAA disclosures.
5. **Amazon Bedrock AgentCore**: Anthropic Claude 3.5 Sonnet foundation model driving autonomous clinical reasoning and Action Groups.
6. **Amazon DynamoDB**: Low-latency cross-channel session and event stream persistence.
7. **Amazon S3 & CloudWatch**: Immutable SHA-256 audit vaults with Object Lock for 7-year HIPAA compliance.

---

## 4. Go-To-Market & AWS Specialist Enablement Request

### 4.1 AWS Co-Sell & Specialist Collaboration Request
- **Target AWS Teams**: 
  - AWS Communication Developer Services (CDS) Product & Specialist Teams
  - AWS Healthcare & Life Sciences (HLS) Enterprise Sales
  - AWS Generative AI & Amazon Bedrock Solution Architects
- **Requested AWS Support**:
  - Joint customer discovery calls with Tier-1 health systems and pharmacy benefit managers.
  - Architecture review and technical validation for high-volume EUM WhatsApp WABA provisioning and carrier RCS brand verification.
  - AWS Marketplace listing co-development under CPPO (Channel Partner Private Offers).

### 4.2 Repeatable Product Offering (AWS Marketplace)
DAXDA AI will package DAXDA CareFlow CDS as a **repeatable software offering on the AWS Marketplace**:
- **Delivery Model**: AWS CloudFormation / Terraform QuickStart deployable into customer VPCs or hosted SaaS on DAXDA AWS infrastructure.
- **Pricing Strategy**: Tiered per-active-patient monthly subscription + pass-through AWS CDS messaging consumption.
- **Target Buyers**: Hospital Health Systems, Digital Health Startups, National Pharmacy Chains (e.g., Walgreens/CVS partners), and PBMs.

---

## 5. Step-by-Step Instructions to Submit in AWS Partner Central

1. Log in to [AWS Partner Central](https://partnercentral.awspartner.com/).
2. Navigate to **Customer Engagement** ➔ **My Opportunities** ➔ Click **Create Opportunity**.
3. Under **Campaign Information**, locate the field **Marketing Campaign Code** and enter:
   ```text
   AWS CDS Agentic AI Hackathon -Sept. 2026
   ```
   *(Ensure exact spelling and punctuation as required by hackathon rules).*
4. In the **Project Information** tab, paste the Opportunity Name: `DAXDA CareFlow CDS - Omnichannel Healthcare Agent`.
5. Enter the Estimated Contract Value (`$180,000`) and Close Date (`Q1 2027`).
6. Tag the primary AWS services: `AWS End User Messaging`, `Amazon Bedrock`, `Amazon SES`, and `Amazon DynamoDB`.
7. Submit the opportunity for review.
8. Copy the generated **Opportunity ID** (e.g. `O-0948215`) and paste it into the Devpost submission form.
