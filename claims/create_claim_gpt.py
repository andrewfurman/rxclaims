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
                            "member_id": {"type": "integer"},
                            "service_provider_id_qualifier": {"type": "string"},
                            "service_provider_id": {"type": "string"},
                            "diagnosis_code_qualifier": {"type": "string"},
                            "diagnosis_code": {"type": "string"},
                            "clinical_information": {"type": "string"},
                            "prescription_service_reference_number": {"type": "string"},
                            "product_service_id": {"type": "string"},
                            "quantity_dispensed": {"type": "integer"},
                            "fill_number": {"type": "integer"},
                            "ndc_number": {"type": "string"},
                            "days_supply": {"type": "integer"},
                            "dispense_as_written": {"type": "boolean"},
                            "date_prescription_written": {"type": "string"},
                            "prescription_origin_code": {"type": "string"},
                            "ingredient_cost_submitted": {"type": "number"},
                            "dispensing_fee_submitted": {"type": "number"},
                            "patient_paid_amount_submitted": {"type": "number"},
                            "prescriber_id_qualifier": {"type": "string"},
                            "prescriber_id": {"type": "string"},
                            "prescriber_last_name": {"type": "string"},
                            "prescriber_phone_number": {"type": "string"}
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
    if 'date_prescription_written' in claim_data:
        claim_data['date_prescription_written'] = datetime.strptime(
            claim_data['date_prescription_written'], '%Y-%m-%d').date()

    new_claim = Claim(**claim_data)
    session.add(new_claim)
    session.commit()
    return claim_data

if __name__ == "__main__":
    test_prompt = """Create a claim for a 30-day supply of Lisinopril 10mg tablets. 
    The prescription was written on 2024-01-15 and filled at CVS Pharmacy."""
    
    result = create_claim_gpt(3, test_prompt)
    print("Created claim:", json.dumps(result, indent=2))