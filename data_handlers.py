from supabase import create_client

def add_chunk(client, document_name, document_desc, page_no, chunk_no_in_doc, bucket_key):
    response = client.table("raw_text_cache").insert({
        "document_name": document_name,
        "document_description": document_desc,
        "page_no": page_no,
        "chunk_no_in_doc": chunk_no_in_doc,
        "bucket_key": bucket_key
    }).execute()
    return response

def add_relevancy_to_chunk(client, document_name, chunk_no_in_doc, task_id):
    response = client.table("raw_text_cache").insert({
        "document_name": document_name,
        "chunk_no_in_doc": chunk_no_in_doc,
        "task_id": task_id
    }).execute()
    return response