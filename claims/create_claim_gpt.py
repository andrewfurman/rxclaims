# Create claim gpt (member.database_id int, string prompt) 

# dysfunction will take in the database ID of a member along with a prompt, which is just a string as parameters and will then call the ChatGPT API to request all of the data. Fields needed to create a new claim in the claims table.

import os, sys, json
from openai import OpenAI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Add root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Now we can import from other directories
from claims.claim_model import db, Claim
from members.member_model import Member

# Create database engine and session
engine = create_engine(os.getenv("DATABASE_URL"))
Session = sessionmaker(bind=engine)
session = Session()

client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

def create_claim_gpt(member_database_id: int, prompt: str):
    payload = {
    "model": "gpt-4o-mini",
    "messages": [
        {
            "role": "system",
            "content": "You are an assistant that creates pharmacy insurance claims based on provided information. Generate only valid pharmacy claim data that matches the provided information. Include appropriate service provider IDs, diagnosis codes, and pricing information that would be typical for pharmacy claims."
        },
        {
            "role": "user",
            "content": prompt
        }
    ],
    "response_format": {
        "type": "json_schema",
        "json_schema": {
            "name": "claim_data",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    "claim": {
                        "type": "object",
                        "properties": {
                            "member_id": {
                                "type": "integer",
                                "description": "Internal database identifier for the member. Not to be confused with the NCPDP Member ID/Cardholder ID. Example: 12345"
                            },
                            "service_provider_id_qualifier": {
                                "type": "string",
                                "description": "NCPDP field identifying type of pharmacy ID being submitted. Common values: '01' = NPI, '05' = Medicaid ID, '07' = NCPDP Provider ID, '08' = State License. Example: '01'"
                            },
                            "service_provider_id": {
                                "type": "string",
                                "description": "Unique identifier for the dispensing pharmacy. If NPI, must be 10 digits. Example NPI: '1234567890', Example NCPDP: 'AB12345'"
                            },
                            "diagnosis_code_qualifier": {
                                "type": "string",
                                "description": "Indicates diagnosis code format. '01' = ICD-9, '02' = ICD-10. Required for certain drugs requiring diagnosis documentation. Example: '02'"
                            },
                            "diagnosis_code": {
                                "type": "string",
                                "description": "ICD-10 or ICD-9 code justifying medical necessity. Must match qualifier format. Example ICD-10: 'E11.9' (Type 2 Diabetes)"
                            },
                            "clinical_information": {
                                "type": "string",
                                "description": "Free-form text containing relevant patient clinical data, often used for prior authorization or step therapy documentation. Example: 'Patient failed formulary alternative lisinopril due to cough'"
                            },
                            "prescription_service_reference_number": {
                                "type": "string",
                                "description": "Unique prescription number assigned by pharmacy. Maximum 12 characters, must be unique per pharmacy location. Example: 'RX123456789'"
                            },
                            "product_service_id": {
                                "type": "string",
                                "description": "Typically the NDC code but can include compound codes. 11 digits without hyphens for NDC. Example NDC: '00071015523'"
                            },
                            "quantity_dispensed": {
                                "type": "integer",
                                "description": "Actual quantity of drug dispensed. For tablets/capsules, must be whole numbers. For liquids/creams can include up to 3 decimal places. Example: 30 (for 30 tablets)"
                            },
                            "fill_number": {
                                "type": "integer",
                                "description": "Sequential number indicating fill number of the prescription. '0' = new, '1-99' = refill number. Example: 0 (new), 1 (first refill)"
                            },
                            "ndc_number": {
                                "type": "string",
                                "description": "11-digit National Drug Code identifying specific manufacturer, product, and package size. Must be a valid FDA NDC. Example: '00071015523' (Lipitor 10mg tablets)"
                            },
                            "days_supply": {
                                "type": "integer",
                                "description": "Number of days the dispensed quantity should last based on prescribed directions. Must be >0 and typically ≤90. Example: 30"
                            },
                            "dispense_as_written": {
                                "type": "boolean",
                                "description": "DAW code indicator. True = DAW 1 (Physician written DAW), False = DAW 0 (No product selection indicated). Example: true"
                            },
                            "date_prescription_written": {
                                "type": "string",
                                "description": "Date prescriber wrote the prescription. Cannot be future date, typically within last year. Format: YYYY-MM-DD. Example: '2024-01-15'"
                            },
                            "prescription_origin_code": {
                                "type": "string",
                                "description": "Code indicating prescription source. '1' = Written, '2' = Telephone, '3' = Electronic, '4' = Facsimile, '5' = Pharmacy. Example: '3'"
                            },
                            "ingredient_cost_submitted": {
                                "type": "number",
                                "description": "Pharmacy's submitted cost for the drug, excluding dispensing fee. Up to 2 decimal places. Example: 105.99"
                            },
                            "dispensing_fee_submitted": {
                                "type": "number",
                                "description": "Fee charged by pharmacy for professional services. Typically $0.01-$15.00. Up to 2 decimal places. Example: 1.50"
                            },
                            "patient_paid_amount_submitted": {
                                "type": "number",
                                "description": "Amount collected from patient (copay/coinsurance). Up to 2 decimal places. Must be ≥0.00. Example: 10.00"
                            },
                            "prescriber_id_qualifier": {
                                "type": "string",
                                "description": "Code identifying type of prescriber ID. '01' = NPI (most common), '12' = DEA number, '14' = State License. Example: '01'"
                            },
                            "prescriber_id": {
                                "type": "string",
                                "description": "Prescriber's ID matching qualifier type. NPI must be 10 digits, DEA must be 9 characters. Example NPI: '1234567890'"
                            },
                            "prescriber_last_name": {
                                "type": "string",
                                "description": "Prescriber's last name exactly as registered with their NPI/DEA. Maximum 35 characters. Example: 'SMITH'"
                            },
                            "prescriber_phone_number": {
                                "type": "string",
                                "description": "Prescriber's contact number. 10 digits, no formatting characters. Example: '8005551234'"
                            }
                        },
                        "required": [
                            "member_id",
                            "service_provider_id_qualifier",
                            "service_provider_id",
                            "diagnosis_code_qualifier",
                            "diagnosis_code",
                            "clinical_information",
                            "prescription_service_reference_number",
                            "product_service_id",
                            "quantity_dispensed",
                            "fill_number",
                            "ndc_number",
                            "days_supply",
                            "dispense_as_written",
                            "date_prescription_written",
                            "prescription_origin_code",
                            "ingredient_cost_submitted",
                            "dispensing_fee_submitted",
                            "patient_paid_amount_submitted",
                            "prescriber_id_qualifier",
                            "prescriber_id",
                            "prescriber_last_name",
                            "prescriber_phone_number"
                        ],
                        "additionalProperties": False
                    }
                },
                "required": ["claim"],
                "additionalProperties": False
            }
        }
    }
}

    response = client.chat.completions.create(**payload)
    claim_data = json.loads(response.choices[0].message.content)['claim']
    
    # Ensure member_id is set to the provided database_id
    claim_data['member_id'] = member_database_id
    
    # Convert date string to date object if present
    # if 'date_prescription_written' in claim_data:
    #     claim_data['date_prescription_written'] = datetime.strptime(
    #         claim_data['date_prescription_written'], '%Y-%m-%d').date()

    new_claim = Claim(**claim_data)
    session.add(new_claim)
    session.commit()
    return claim_data

if __name__ == "__main__":
    test_prompt = """Create a claim for a 30-day supply of Lisinopril 10mg tablets. 
    The prescription was written on 2024-01-15 and filled at CVS Pharmacy."""
    
    result = create_claim_gpt(3, test_prompt)
    print("Created claim:", json.dumps(result, indent=2))