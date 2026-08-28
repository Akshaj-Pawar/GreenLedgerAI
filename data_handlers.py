from supabase import create_client

# This script contains all functions that directly interact with the superbase database
# It is called by any script that needs to interact with said database
# in order to run any function in this script a funcitonal supabase client must alreayd exist, and be provided as input

def add_chunk(client, document_name, document_desc, page_no, chunk_no_in_doc, bucket_key, chunk):
    # tested
    response = client.table("raw_text_cache").upsert({
        "document_name": document_name,
        "document_description": document_desc,
        "page_no": page_no,
        "chunk_no_in_doc": chunk_no_in_doc,
        "bucket_key": bucket_key,
        "chunk_contents": chunk
    }).execute()
    return response


def get_chunk(client, document_name, chunk_no_in_doc):
    # tested
    response = (
        client
        .table("raw_text_cache")
        .select("chunk_contents")
        .eq("document_name", document_name)
        .eq("chunk_no_in_doc", chunk_no_in_doc)
        .execute()
    )

    if response.data:
        return response.data[0]["chunk_contents"]
    else:
        return None


def add_relevancy_to_chunk(client, document_name, chunk_no_in_doc, task_name):

    response = client.table("raw_chunk_relevances").upsert({
        "document_name": document_name,
        "chunk_no_in_doc": chunk_no_in_doc,
        "task_name": task_name,
    }).execute()
    return response


def get_chunk_ids(client, task_name):
    # return document names and chunk_no_in_doc for all chunks relevant to task
    response = (
        client
        .table("raw_chunk_relevances")
        .select("document_name, chunk_no_in_doc")
        .eq("task_name", task_name)
        .execute()
    )

    if response.data:
        return [
            (row["document_name"], row["chunk_no_in_doc"])
            for row in response.data
        ]
    else:
        return []
    

def add_scope2_transaction_row(client, document_name, chunk_no_in_doc, merchant_name, date, product, cost, currency, site_name, site_location_city, site_postcode, start_date, end_date, ef):
    response = client.table("scope2_transactions").upsert({
        "document_name": document_name,
        "chunk_no_in_doc": chunk_no_in_doc,
        "merchant_name": merchant_name,
        "date_of_payment": date,
        "product": product,
        "cost": cost,
        "currency": currency,
        "site_name": site_name,
        "site_city": site_location_city,
        "site_postcode": site_postcode,
        "billing_period_start_date": start_date,
        "billing_period_end_date": end_date,
        "emission_factor": ef
    }).execute()
    return response


def get_display_rows(client, task_name, end_date=None, start_date=None):
    # from raw_text_cache: document_name, document_desc, page_no, chunk_no_in_doc, bucket_key, chunks
    # from scope2_transactions: document_name, chunk_no_in_doc, merchant_name, date, product, cost, currency, site_name, site_location_city, site_postcode, start_date, end_date, ef

    task_table_names = {"scope2_from_utility_bills": "scope2_transactions"}
    task_table_name = task_table_names[task_name]

    query = (
        client
        .table("raw_text_cache")
        .select(f"""
            *,
            {task_table_name} (
                *
            ),
            raw_chunk_relevances!inner (
                task_name
            )
        """)
        .eq("raw_chunk_relevances.task_name", task_name)
    )

    if start_date is not None:
        query = query.gte("created_at", start_date)

    if end_date is not None:
        query = query.lt("created_at", end_date)

    response = query.execute()

    if response.data:

        display_rows = []

        for chunk in response.data:

            transactions = chunk.get(task_table_name, [])

            if len(transactions) == 0:
                continue

            for transaction in transactions:

                row = {
                    **chunk,
                    **transaction
                }

                # Remove fields we don't want in the display row
                row.pop(task_table_name, None)
                row.pop("raw_chunk_relevances", None)

                display_rows.append(row)

        return display_rows
    
    else:
        return None

    # reference doc:

        #document_name = response.data["document_name"]
        #chunk_no_in_doc = response.data["chunk_no_in_doc"]
        #merchant_name = response.data["scope2_transactions"]["merchant_name"]
        #date = response.data["scope2_transactions"]["date_of_payment"]
        #product = response.data["scope2_transactions"]["product"]
        #cost = response.data["scope2_transactions"]["cost"]
        #currency = response.data["scope2_transactions"]["currency"]
        #site_name = response.data["scope2_transactions"]["site_name"]
        #site_location_city = response.data["scope2_transactions"]["site_city"]
        #site_postcode = response.data["scope2_transactions"]["site_postcode"]
        #start_date = response.data["scope2_transactions"]["billing_period_start_date"]
        #end_date = response.data["scope2_transactions"]["billing_period_end_date"]
        #ef = response.data["scope2_transactions"]["emission_factor"]
        #document_desc = response.data["document_desc"]
        #page_no = response.data["page_no"]
        #chunk_no_in_doc = response.data["chunk_no_in_doc"]
        #bucket_key = response.data["bucket_key"]
        #chunk_contents = response.data["chunk_contents"]
        # list of many such

def debug_reset_database(client):
    client.rpc("debug_reset_database").execute()
    # delete scope2_transactions then delete raw_chunk_relevancies then delete chunks

