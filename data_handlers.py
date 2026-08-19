from supabase import create_client

def add_chunk(client, document_name, document_desc, page_no, chunk_no_in_doc, bucket_key, chunk):
    response = client.table("raw_text_cache").insert({
        "document_name": document_name,
        "document_description": document_desc,
        "page_no": page_no,
        "chunk_no_in_doc": chunk_no_in_doc,
        "bucket_key": bucket_key,
        "chunk_contents": chunk
    }).execute()
    return response

def add_relevancy_to_chunk(client, document_name, chunk_no_in_doc, task_name):

    response = client.table("raw_chunk_relevances").insert({
        "document_name": document_name,
        "chunk_no_in_doc": chunk_no_in_doc,
        "task_name": task_name,
    }).execute()
    return response

def get_chunk_ids(client, task_name):
    # return document names and chunk_no_in_docs for all chunks relevant to task
    response = (
        client
        .table("raw_chunk_relevances")
        .select("document_name, chunk_no_in_docs")
        .eq("task_name", task_name)
        .execute()
    )

    if response.data:
        document_name = response.data["document_name"]
        chunk_no_in_docs = response.data["chunk_no_in_docs"]
        return document_name, chunk_no_in_docs
    else:
        return None

def get_chunk(client, document_name, chunk_no_in_doc):
    response = (
        client
        .table("raw_text_cache")
        .select("chunk")
        .eq("document_name", document_name)
        .eq("chunk_no_in_doc", chunk_no_in_doc)
        .execute()
    )

    if response.data:
        return response.data["chunk"]
    else:
        return None

def add_scope2_transaction_row(client, document_name, chunk_no_in_doc, merchant_name, date, product, cost, currency, site_name, site_location_city, site_postcode, start_date, end_date, ef):
    response = client.table("scope2_transactions").insert({
        "document_name": document_name,
        "chunk_no_in_doc": chunk_no_in_doc,
        "merchant_name": merchant_name,
        "date": date,
        "product": product,
        "cost": cost,
        "currency": currency,
        "site_name": site_name,
        "site_location_city": site_location_city,
        "site_postcode": site_postcode,
        "start_date": start_date,
        "end_date": end_date,
        "ef": ef
    }).execute()
    return response

def get_display_rows(client, task_name, end_date=None, start_date=None):
    # from raw_text_cache: document_name, document_desc, page_no, chunk_no_in_doc, bucket_key, chunks
    # from scope2_transactions: document_name, chunk_no_in_doc, merchant_name, date, product, cost, currency, site_name, site_location_city, site_postcode, start_date, end_date, ef

    query = (
        client
        .table("raw_text_cache")
        .select("""
            *,
            scope2_transactions (
                *
            ),
            raw_text_relevances (
                task_name
            )
        """)
        .eq("raw_text_relevances.task_name", task_name)
    )

    if start_date is not None:
        query = query.gte("created_at", start_date)

    if end_date is not None:
        query = query.lt("created_at", end_date)

    response = query.execute()

    if response.data:

        #document_name = response.data["document_name"]
        #chunk_no_in_doc = response.data["chunk_no_in_doc"]
        #merchant_name = response.data["scope2_transactions"]["merchant_name"]
        #date = response.data["scope2_transactions"]["date"]
        #product = response.data["scope2_transactions"]["product"]
        #cost = response.data["scope2_transactions"]["cost"]
        #currency = response.data["scope2_transactions"]["currency"]
        #site_name = response.data["scope2_transactions"]["site_name"]
        #site_location_city = response.data["scope2_transactions"]["site_location_city"]
        #site_postcode = response.data["scope2_transactions"]["site_postcode"]
        #start_date = response.data["scope2_transactions"]["start_date"]
        #end_date = response.data["scope2_transactions"]["end_date"]
        #ef = response.data["scope2_transactions"]["ef"]
        #document_desc = response.data["document_desc"]
        #page_no = response.data["page_no"]
        #chunk_no_in_doc = response.data["chunk_no_in_doc"]
        #bucket_key = response.data["bucket_key"]
        #chunk_contents = response.data["chunk_contents"]
        # list of many such

        return response.data
    
    else:
        return None



# response unpacking