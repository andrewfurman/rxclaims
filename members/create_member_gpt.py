# the create member GPT function will take in a single string variable, which is a prompt with specifications needed for creating a member. Then the prompt will be sent to ChatGPT and ChatGPT will produce a JSON payload. This chase on payload can then be used to create a new member in the member database table.

import os
import json
from openai import OpenAI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .member_model import Member

# Create database engine and session
engine = create_engine(os.getenv("DATABASE_URL"))
Session = sessionmaker(bind=engine)
session = Session()

client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

def create_member_gpt(prompt):
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": "You are an assistant that creates member profiles for pharmacy insurance coverage based on provided information. Generate only valid insurance-related data that matches the provided information.  These profiles will be used as examples of members with coverage from Emblem Health. Obey the prompt, but if limited information is given, create coverage similar to what is seen here:  emblemhealth_summary = EmblemHealth Essential Plan 200-250 Summary of Benefits General Information: - Underwritten by: Health Insurance Plan of Greater New York (HIP) - Network: Enhanced Care Prime Network (no PCP referral required) - Out-of-Pocket Maximum: $2,000 - Plan Deductible: $0 (no separate prescription deductible) Office Visits: - Primary Care & Preventive: $15 copayment - Specialists: $25 copayment - Mental Health/Substance Abuse: $15 copayment - Telemedicine (Teladoc): No charge - Preventive Services: No charge (includes adult preventive, prenatal, routine gynecological, mammography, immunizations) Prescription Drugs: - Retail Pharmacy (30-day supply): - Preferred Generic (Tier 1): $6 copayment - Non-preferred Generic (Tier 2): $15 copayment - Preferred Brand (Tier 3): $30 copayment - Mail Order Pharmacy (up to 90-day supply): - Preferred Generic (Tier 1): $15 copayment - Non-preferred Generic (Tier 2): $37.50 copayment - Preferred Brand (Tier 3): $75 copayment - Special Notes: No preauthorization for covered drugs treating substance use disorders Special Services: - Advanced Radiology (CT/PET/MRI): $25 copayment (preauthorization required) - Laboratory Services: - PCP Office: $15 copayment - Specialist Office: $25 copayment - Physical & Occupational Therapy: $15 copayment (60 visits/year) - Inpatient Services: - General: $150 copayment per admission (maternity waived) - Rehabilitation & Habilitation: $150 copayment per admission (preauthorization required) - Emergency & Urgent Care: - Ambulance: $75 copayment - Emergency Room: $75 copayment (waived if admitted) - Urgent Care Centers: $25 copayment - Dental Care: - Preventive & Routine: No charge - Major Care: $0 copayment (preauthorization required) - Vision Care: - No charge for prescribed glasses/contact lenses and routine exams - Additional Benefits: - Gym Reimbursement: $200 per 6 months - Durable Medical Equipment (DME): 5% coinsurance - Home Health Care: $15 copayment (40 visits/year) - Dialysis: $15 copayment (limited to 10 visits/year if non-participating) Preauthorization Requirements: - Required for ABA Treatment, Advanced Radiology, Inpatient Services (except emergencies), Physical Therapy beyond limits, Durable Medical Equipment, and other specified services. Notes: - Services must be provided by in-network providers or approved by EmblemHealth Care Management. - Participating providers are not employees of EmblemHealth. - Refer to policy form number 155-23-EPP200-250NONAIAN (01-24) for complete details and limitations. Key Points: - No deductible and $2,000 out-of-pocket max. - Low copayments for primary, preventive, and many outpatient services. - Comprehensive preventive care covered at no cost. - Flexible prescription options with retail and mail-order pharmacies. - Extensive coverage including mental health, dental, vision, and more. - Preauthorization required for several specialized and high-cost services."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "member_profile",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "member_profile": {
                            "type": "object",
                            "properties": {
                                "member_id": {
                                    "type": "string",
                                    "description": "Start with 'EM-' followed by 12 random non sequential digits"
                                },
                                "first_name": {
                                    "type": "string",
                                    "description": "Member's legal first name. If no name is given in the prompt, use a common name, but do not use the most common names like John Jane Liam Clara Lucas unless specified in the prompt."
                                },
                                "last_name": {
                                    "type": "string",
                                    "description": "Member's legal last name. Do not use the most common names like Smith or Jones unless requested in the prompt."
                                },
                                "date_of_birth": {
                                    "type": "string",
                                    "description": "Member's date of birth in YYYY-MM-DD format. Pick a random date in the year, not use january 1st unless specified in the prompt"
                                },
                                "gender": {
                                    "type": "string",
                                    "description": "Member's gender coded as single character (M/F/X)"
                                },
                                "address": {
                                    "type": "string",
                                    "description": "Member's street address. make this line look like a real street in the city selected, not 123 Main St. Make sure to select random street number, not sequential numbers like 456, 9876 or 1234"
                                },
                                "city": {
                                    "type": "string",
                                    "description": "City of member's residence. If the city or location isn't specified in the prompt, make sure that the city is in one of these counties unless specified otherwise in the prompt: Albany Bronx Broome Columbia Delaware Dutchess Fulton Greene Kings (Brooklyn) Montgomery Nassau New York (Manhattan) Orange Otsego Putnam Queens Rensselaer Richmond (Staten Island) Rockland Saratoga Schenectady Schoharie Suffolk Sullivan Ulster Warren Washington Westchester. If the city or location is specified in the prompt, ignore the counties and just use that."
                                },
                                "state": {
                                    "type": "string",
                                    "description": "Two-letter state code of member's residence"
                                },
                                "zip_code": {
                                    "type": "string",
                                    "description": "Postal zip code of member's residence"
                                },
                                "phone_number": {
                                    "type": "string",
                                    "description": "Member's contact phone number"
                                },
                                "insurance_id_number": {
                                    "type": "string",
                                    "description": "Primary insurance identification number. Use for Emblem Health unless otherwise specified. Example: 'EMBLEM-24358157' "
                                },
                                "group_number": {
                                    "type": "string",
                                    "description": "Insurance group number identifying the benefit plan. NYC-29262"
                                },
                                "rx_bin": {
                                    "type": "string",
                                    "description": "Pharmacy benefit BIN (Bank Identification Number). For EmblemHealth's HIP Commercial plans, the BIN is 004336."
                                },
                                "rx_group": {
                                    "type": "string",
                                    "description": "Pharmacy benefit group identifier. Example: EMBHLTH unless otherwise specified."
                                },
                                "rx_pcn": {
                                    "type": "string",
                                    "description": "Pharmacy benefit Processor Control Number. For EmblemHealth's HIP Commercial plans, the PCN is 'ADV' "
                                },
                                "copay_1_generic": {
                                    "type": "string",
                                    "description": "Copay amount for generic medications (Tier 1). Example: '$10'"
                                },
                                "copay_2_preferred": {
                                    "type": "string",
                                    "description": "Copay amount for preferred brand medications (Tier 2) Example: '$30'"
                                },
                                "copay_3_non_preferred": {
                                    "type": "string",
                                    "description": "Copay amount for non-preferred brand medications (Tier 3) Example: '$50'"
                                },
                                "copay_4_specialty": {
                                    "type": "string",
                                    "description": "Copay amount for specialty medications (Tier 4).  Example: '$100'"
                                }
                            },
                            "required": [
                                "member_id", "first_name", "last_name", "date_of_birth", 
                                "gender", "address", "city", "state", "zip_code", 
                                "phone_number", "insurance_id_number", "group_number",
                                "rx_bin", "rx_group", "rx_pcn", "copay_1_generic",
                                "copay_2_preferred", "copay_3_non_preferred", "copay_4_specialty"
                            ],
                            "additionalProperties": False
                        }
                    },
                    "required": ["member_profile"],
                    "additionalProperties": False
                }
            }
        }
    }

    response = client.chat.completions.create(**payload)
    member_data = json.loads(response.choices[0].message.content)['member_profile']
  
    new_member = Member(**member_data)
    session.add(new_member)
    session.commit()
    return member_data

if __name__ == "__main__":
    test_prompt = """Create a member profile for a random person."""

    result = create_member_gpt(test_prompt)
    print("Created member:", json.dumps(result, indent=2))