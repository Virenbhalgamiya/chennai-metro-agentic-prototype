import os
import shutil
from pathlib import Path

BASE_DIR = Path("d:/illuminati-consulting-prototype")
SOP_DIR = BASE_DIR / "data" / "mock_sops"
FAISS_DIR = BASE_DIR / "faiss_index"

# 1. Clean up old SOPs and index
if SOP_DIR.exists():
    shutil.rmtree(SOP_DIR)
if FAISS_DIR.exists():
    shutil.rmtree(FAISS_DIR)

SOP_DIR.mkdir(parents=True, exist_ok=True)

# 2. Write highly detailed Metro SOPs
sops = {
    "ticketing_smart_cards.md": """# CHENNAI METRO RAIL LIMITED (CMRL)
## STANDARD OPERATING PROCEDURE: TICKETING & SMART CARDS (SOP-TKT-001)

### 1. OBJECTIVE
To establish a standardized workflow for handling passenger grievances related to Automatic Fare Collection (AFC) systems, Token Vending Machines (TVMs), and National Common Mobility Card (NCMC) smart cards to ensure zero revenue leakage while maintaining a seamless passenger experience.

### 2. SCOPE
This SOP covers:
- Smart Card recharge failures (UPI/Credit/Debit/Cash).
- AFC gate hardware/software malfunctions (e.g., fare deducted but gate did not open).
- TVM cash jams, receipt printing failures, or out-of-order errors.
- Unjustified fare deductions and overcharging penalties.

### 3. SERVICE LEVEL AGREEMENTS (SLA)
- **Immediate Assistance (At Station):** Within 5 minutes via Customer Care Kiosk.
- **Financial Refund Resolution:** 3-5 business days for bank-side UPI/Card failures.
- **Card Replacement:** Immediate replacement of physically damaged CMRL cards at the kiosk.

### 4. PROCEDURAL STEPS
#### 4.1. AFC Gate Failures (Fare deducted, gate closed)
1. The on-duty Customer Care Officer (CCO) must request the passenger's Smart Card or Token.
2. The CCO will tap the card on the Station Point of Sale (POS) terminal to read the last transaction log.
3. If the POS confirms deduction without entry/exit registration, the CCO will manually override the card status to allow exit/entry without penalty.
4. If the passenger used an NCMC card from an external bank, log a ticket with the central clearing house. Provide the passenger with a reference ID.

#### 4.2. TVM Cash Jams or Recharge Failures
1. If a passenger reports a TVM taking cash but not dispensing a token/recharge, the Station Controller (SC) must immediately lock down the affected TVM.
2. The SC and a security personnel will open the TVM to verify the cash jam.
3. If the cash is found in the escrow hopper, it is returned to the passenger immediately, and a manual token is issued.
4. If the transaction was digital (UPI), the CCO advises the passenger that failed UPI transactions auto-refund within 72 hours per NPCI guidelines. The passenger must purchase a new token.

### 5. ESCALATION MATRIX
- **Level 1:** Station Customer Care Officer
- **Level 2:** Station Controller (SC)
- **Level 3:** Central Ticketing & Revenue Manager (CTRM)
""",
    "station_facilities.md": """# CHENNAI METRO RAIL LIMITED (CMRL)
## STANDARD OPERATING PROCEDURE: STATION FACILITIES (SOP-FAC-002)

### 1. OBJECTIVE
To ensure world-class cleanliness, hygiene, and mechanical functionality of all passenger-facing infrastructure across all elevated and underground CMRL stations.

### 2. SCOPE
This SOP covers:
- Elevator (Lift) and Escalator breakdowns.
- Housekeeping, platform cleanliness, and washroom hygiene.
- HVAC (Air Conditioning) failures in underground stations.
- Lighting, signage, and PA system outages.

### 3. PROCEDURAL STEPS
#### 3.1. Elevator/Escalator Breakdown
1. **Detection:** Upon complaint or SCADA alert regarding a lift/escalator halt, the Station Controller (SC) immediately views the CCTV to ensure no passengers are trapped.
2. **Entrapment:** If passengers are trapped, the SC immediately triggers the Emergency Rescue Protocol (ERP) and dispatches the on-site mechanical technician. Target rescue time: < 10 minutes.
3. **Outage:** If it is a mechanical failure with no trapped passengers, the SC must place barricades and "Out of Service" signages at both ends within 5 minutes.
4. **Notification:** The PA system must be updated to announce the outage every 15 minutes, directing mobility-impaired passengers to alternative routes or the opposite platform.

#### 3.2. Cleanliness and Hygiene
1. When a complaint is received regarding bio-hazardous spills, garbage, or unclean washrooms, the SC dispatches the Rapid Cleaning Team (RCT) via VHF radio.
2. The RCT must arrive at the incident zone within 5 minutes equipped with appropriate cleaning materials and caution signages.
3. Once cleaned, the RCT supervisor radios the SC to close the incident log.

### 4. PREVENTATIVE MAINTENANCE
- Washrooms are deep-cleaned every 2 hours and logged on the back-of-door manifests.
- Elevators undergo rigorous load testing and mechanical checks on the 1st Tuesday of every month between 01:00 AM and 04:00 AM (non-revenue hours).
""",
    "train_operations.md": """# CHENNAI METRO RAIL LIMITED (CMRL)
## STANDARD OPERATING PROCEDURE: TRAIN OPERATIONS (SOP-OPS-003)

### 1. OBJECTIVE
To manage anomalies in train scheduling, rolling stock health, and passenger comfort inside the train cars, ensuring punctuality and safety.

### 2. SCOPE
This SOP covers:
- Train delays, halts mid-section, and schedule deviations.
- Overcrowding and platform clearance.
- Rolling stock issues: AC failures, door jams, flickering lights, PA system failure inside the train.

### 3. PROCEDURAL STEPS
#### 3.1. Train Delays and Mid-Section Halts
1. If a train halts mid-section (between stations) for more than 3 minutes, the Train Operator (TO) must initiate a PA announcement inside the train explaining the delay and assuring passenger safety.
2. The Operations Control Center (OCC) in Koyambedu monitors headway. If delay exceeds 5 minutes, OCC instructs all Station Controllers down the line to announce the delay.
3. For delays >15 minutes, OCC may authorize short-looping or injecting standby trains from the depot to clear platform crowds.

#### 3.2. Rolling Stock AC Failure / Door Jams
1. **Door Jam:** If a passenger reports a door not opening, the TO will attempt a localized door override. If it fails, the TO must physically inspect the door, isolate it using the manual lock, and place an "Out of Order" sticker. Passengers will use adjacent doors.
2. **AC Failure:** If an entire coach loses HVAC, the TO attempts a soft reset of the Auxiliary Converter from the cabin. If unresolved, the train is marked for maintenance and will be swapped out at the terminal station.
3. Passengers complaining of suffocation must be advised via PA to move to the adjacent interconnected coaches.

### 4. CROWD CONTROL
During peak hours (0800-1100, 1700-2000) or major city events, if platform density exceeds 3 passengers per square meter, the SC will restrict AFC gate entries and deploy crowd marshals to guide passengers behind the yellow tactile lines.
""",
    "staff_behavior.md": """# CHENNAI METRO RAIL LIMITED (CMRL)
## STANDARD OPERATING PROCEDURE: STAFF BEHAVIOR (SOP-HR-004)

### 1. OBJECTIVE
To uphold the highest standards of professionalism and courtesy among all CMRL employees, contractors, and security personnel interacting with the public.

### 2. SCOPE
This SOP covers:
- Reports of rude, aggressive, or unhelpful behavior by Customer Care, Security (CISF/Private), or Housekeeping staff.
- Extortion, bribery, or unauthorized penalty collection.
- Discrimination or harassment by staff towards passengers.

### 3. PROCEDURAL STEPS
#### 3.1. Incident Reporting and Logging
1. When a grievance is filed, the Nodal Officer must extract the exact time, station, and location from the complaint to identify the staff member via duty rosters and CCTV.
2. The Station Manager (SM) is notified to securely backup the audio/video footage of the incident location within 24 hours to prevent overwriting.

#### 3.2. Investigation
1. The SM conducts a preliminary interview with the accused staff member and witnesses.
2. If the staff member belongs to an outsourced contractor (e.g., Security, Housekeeping), the contractor's agency head is officially notified via email.
3. If the complaint involves physical altercation or bribery, the staff member is immediately suspended pending a formal inquiry.

#### 3.3. Resolution and Disciplinary Action
1. **Minor Offense (Rudeness):** The staff member undergoes mandatory soft-skills retraining. A written warning is placed in their file.
2. **Major Offense (Extortion/Assault):** Termination of contract/employment and handover to local law enforcement.
3. **Passenger Communication:** The Nodal Officer must draft a formal apology to the passenger, detailing the exact actions taken against the erring staff, demonstrating CMRL's zero-tolerance policy.
""",
    "safety_security.md": """# CHENNAI METRO RAIL LIMITED (CMRL)
## STANDARD OPERATING PROCEDURE: SAFETY & SECURITY (SOP-SEC-005)

### 1. OBJECTIVE
To ensure the absolute physical safety of all passengers, staff, and assets within the Chennai Metro network, coordinating swiftly with law enforcement and emergency services.

### 2. SCOPE
This SOP covers:
- Medical emergencies on platforms or inside trains.
- Theft, pickpocketing, and unattended baggage.
- Harassment (verbal or physical) of passengers.
- Track trespassing or suicide attempts.

### 3. PROCEDURAL STEPS
#### 3.1. Medical Emergencies
1. If a passenger collapses or requires medical attention, the Station Controller (SC) immediately dispatches the station's First Responder Team with the AED and First Aid kit.
2. The SC calls the emergency ambulance service (108) and designates a security guard to clear a path from the station entrance to the incident spot.
3. If the incident is inside a moving train, the Train Operator alerts the next station to have the medical team waiting at the exact coach alignment mark.

#### 3.2. Unattended Baggage / Bomb Threat
1. The area around the unattended bag is immediately evacuated and cordoned off (minimum 50-meter radius).
2. The SC notifies the State Police Bomb Detection and Disposal Squad (BDDS) and the OCC.
3. Train services bypassing the affected platform may be initiated until the all-clear is given by BDDS.

#### 3.3. Harassment or Theft
1. The victim is escorted to a secure, private room in the SC office.
2. Station Security immediately reviews CCTV to track the perpetrator's movement. If the perpetrator is still in the network, their description is broadcast to all stations and Train Operators.
3. The SC assists the victim in filing an FIR with the jurisdictional Metro Police Station.

#### 3.4. Track Trespassing
1. **IMMEDIATE ACTION:** Anyone dropping onto the tracks triggers an emergency track power cut. The SC hits the Emergency Trip Switch (ETS) on the platform, instantly removing 25kV traction power.
2. OCC is alerted to halt all incoming trains.
3. Security personnel physically remove the trespasser, hand them over to the police, and normal operations resume only after track inspection.
"""
}

for filename, content in sops.items():
    with open(SOP_DIR / filename, "w", encoding="utf-8") as f:
        f.write(content)

print("Highly detailed Metro SOPs generated and old FAISS index wiped.")
