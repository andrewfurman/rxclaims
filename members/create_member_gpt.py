# the create member GPT function will take in a single string variable, which is a prompt with specifications needed for creating a member. Then the prompt will be sent to ChatGPT and ChatGPT will produce a JSON payload. This chase on payload can then be used to create a new member in the member database table.

import os
import json
from openai import OpenAI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from member_model import db, Member

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
                "content": "You are an assistant that creates member profiles for pharmacy insurance coverage based on provided information. Generate only valid insurance-related data that matches the provided information."
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
                                    "description": "Unique identifier for the member in the insurance system"
                                },
                                "first_name": {
                                    "type": "string",
                                    "description": "Member's legal first name"
                                },
                                "last_name": {
                                    "type": "string",
                                    "description": "Member's legal last name"
                                },
                                "date_of_birth": {
                                    "type": "string",
                                    "description": "Member's date of birth in YYYY-MM-DD format"
                                },
                                "gender": {
                                    "type": "string",
                                    "description": "Member's gender coded as single character (M/F/X)"
                                },
                                "address": {
                                    "type": "string",
                                    "description": "Member's street address"
                                },
                                "city": {
                                    "type": "string",
                                    "description": "City of member's residence"
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
                                    "description": "Primary insurance identification number"
                                },
                                "group_number": {
                                    "type": "string",
                                    "description": "Insurance group number identifying the benefit plan"
                                },
                                "rx_bin": {
                                    "type": "string",
                                    "description": "Pharmacy benefit BIN (Bank Identification Number)"
                                },
                                "rx_group": {
                                    "type": "string",
                                    "description": "Pharmacy benefit group identifier"
                                },
                                "rx_pcn": {
                                    "type": "string",
                                    "description": "Pharmacy benefit Processor Control Number"
                                },
                                "copay_1_generic": {
                                    "type": "string",
                                    "description": "Copay amount for generic medications (Tier 1)"
                                },
                                "copay_2_preferred": {
                                    "type": "string",
                                    "description": "Copay amount for preferred brand medications (Tier 2)"
                                },
                                "copay_3_non_preferred": {
                                    "type": "string",
                                    "description": "Copay amount for non-preferred brand medications (Tier 3)"
                                },
                                "copay_4_specialty": {
                                    "type": "string",
                                    "description": "Copay amount for specialty medications (Tier 4)"
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
    test_prompt = """Create a member profile for John Smith. He was born on 1980-01-01, 
    lives at 123 Main St, Boston MA 02108, and has phone number 617-555-1234. 
    His insurance ID is ABC123456."""

    result = create_member_gpt(test_prompt)
    print("Created member:", json.dumps(result, indent=2))