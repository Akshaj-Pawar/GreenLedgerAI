from openai import OpenAI
import json
import os
from dotenv import load_dotenv
from supabase import create_client

import data_handlers
import estimation_algs


load_dotenv()

key = os.getenv("OPENAI_API_KEY")

def flatten_dict(d, parent_key="", sep="."):
    items = {}
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.update(flatten_dict(v, new_key, sep))
        else:
            items[new_key] = v
    return items

def task_scope2_from_utility_bills(document_name, chunk_no_in_doc, openai_client, db_connection):

    chunk = data_handlers.get_chunk(document_name, chunk_no_in_doc)
    relevance_def =  "transaction refers to an energy utility bill payment, or any such payemnt referring to the purchase of grid energy, such as would be relevant in a scope 2 emissions calculation"


    prompt = f'''
    Examine the supplied text chunk and for every distinct transaction:
    A) Consider its relevance to the task. 
    A transaction is relevant if: {relevance_def}.
    A transaction is relevant only when the text records that the transaction actually occurred. Mentions of planned, expected, scheduled, hypothetical, cancelled, or requested transactions do not count.
    B) If and only if the transaction appears relevant to the task, extract the information available in the transaction record into the appropriate fields. 
    If no information can be found for a given field, set as null
    Do not infer or invent information that is not supported by the text, your role is strictly data extraction from the chunk, not to offer speculations on uncertainties
    Treat each distinct transaction separately, even when multiple transactions occur in the same paragraph or sentence.
    If there are no relevant transactions in the chunk, return an empty transactions array

    The text you are to analyse begins here: {chunk}
    '''

    response = openai_client.beta.chat.completions.parse(
        model = "gpt-4o-mini",

        messages = [
            {
                "role": "user",
                "content": prompt,
            }
        ],

        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "transaction_extraction",
                "strict": True,
                "schema": {
                    {
                    "type": "object",
                    "properties": {
                        "transactions": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                            "description": {
                                "type": "string",
                                "description": "A short description of the transaction, e.g. 'utility bill payment' or 'salary payment'."
                                # eventually convert into enum
                            },
                            "date": {
                                "type": ["string", "null"],
                                "description": "The transaction date as explicitly stated in the text (year, month, day format). Null if no transaction date can be established."
                            },
                            "merchant_name": {
                                "type": ["string", "null"],
                                "description": "The merchant, payee, or other counterparty if explicitly identifiable."
                            },
                            "product": {
                                "type": ["string", "null"],
                                "description": "The product being purchased in the transaction, as stated in the transaction."
                            },
                            "cost": {
                                "type": ["number", "null"],
                                "description": "The monetary cost of the transaction. Do not infer an amount that is not present in the text."
                            },
                            "currency": {
                                "type": ["string", "null"],
                                "description": "The currency of the transaction, preferably as an ISO 4217 code such as GBP or USD."
                            },
                            "kwhs": {
                                "type": ["number", "null"],
                                "description": "The number of kwhs of energy purchased in the given transaction."            
                            },
                            "site_name": {
                                "type": ["string", "null"],
                                "description": "The name of the building or site that is being billed."        
                            },
                            "site_location_city": {
                                "type": ["string", "null"],
                                "description": "The last line of the address of the building or site that is being billed."               
                            },
                            "site_postcode": {
                                "type": ["string", "null"],
                                "description": "The postcode of the building or site that is being billed."               
                            },
                            "start_date": {
                                "type": ["string", "null"],
                                "description": "For subscription services or utility payments: date at which the billing period covered by the payment record begins."               
                            },
                            "end_date": {
                                "type": ["string", "null"],
                                "description": "For subscription services or utility payments: date at which the billing period covered by the payment record ends."               
                            },
                            "required": ["description","date","merchant_name","product","cost","currency","kwhs","site_name","site_location_city","site_postcode","start_date","end_date"],
                            "additionalProperties": False
                        }
                        }
                    },
                    "required": ["transactions"],
                    "additionalProperties": False
                    }
                }
            }
            }
        }

    )

    output = json.loads(response.choices[0].message.content)
    print(output)

    # unpack JSON into output rows

    for t in output['transactions']:
        output_dict = t["items"]
        ef = estimation_algs.scope2_fub_get_ef(output_dict["site_location_city"], output_dict["site_postcode"], output_dict["merchant_name"], output_dict["product"], output_dict["cost"], output_dict["currency"], output_dict["start_date"], output_dict["end_date"])
        data_handlers.add_scope2_transaction_row(db_connection, document_name, chunk_no_in_doc, output_dict["merchant_name"], output_dict["date"], output_dict["product"], output_dict["cost"], output_dict["currency"], output_dict["site_name"], output_dict["site_location_city"], output_dict["site_postcode"], output_dict["start_date"], output_dict["end_date"], ef)
        # add to a postgres db


test_input = "" # chunk
def test_task_scope2_fub():

    sb_url = os.getenv("SUPABASE_URL")
    sb_key = os.getenv("SUPABASE_ADMIN_KEY")

    db_connection = create_client(
        sb_url,
        sb_key
    )

    openai_client = OpenAI()

    chunk_pks = data_handlers.get_chunk_ids()
    for document_name, chunk_no_in_doc in chunk_pks:
        task_scope2_from_utility_bills(document_name, chunk_no_in_doc, openai_client, db_connection)

def execute_task(task):

    TASK_HANDLERS = {
        "scope2_from_utility_bills": task_scope2_from_utility_bills,
        # keep updated with lists of tasks
    }
    handler = TASK_HANDLERS.get(task)

    if handler is None:
        results = {"success": False, "results": None, "error": f"Unknown task: {task}"}
    else:
        try:
            sb_url = os.getenv("SUPABASE_URL")
            sb_key = os.getenv("SUPABASE_ADMIN_KEY")

            db_connection = create_client(
                sb_url,
                sb_key
            )
            openai_client = OpenAI()

            chunk_pks = data_handlers.get_chunk_ids(task)
            for document_name, chunk_no_in_doc in chunk_pks:
                handler(document_name, chunk_no_in_doc, openai_client, db_connection)

            response = data_handlers.get_display_rows(db_connection, task, end_date=None, start_date=None)
            for rowi in range(len(response)):
                row = flatten_dict(response[rowi], parent_key="", sep=".")
                response[rowi] = row # safe because no deletions or additions

            all_keys = set()
            for row in response:
                all_keys.update(row.keys())
            response = [{k: row.get(k) for k in all_keys} for row in response]

            results = {"success": True, "results": response, "error": None}

        except Exception as e:
            results = {"success": False, "results": None, "error": str(e)}

    return results




