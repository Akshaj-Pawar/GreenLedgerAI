import data_handlers
from supabase import create_client
from dotenv import load_dotenv
import os
import sys

load_dotenv()

sb_url = os.getenv("SUPABASE_URL")
sb_key = os.getenv("SUPABASE_ADMIN_KEY")

print("sb_url:", repr(sb_url))
print("sb_key length:", len(sb_key))

client = create_client(
    sb_url,
    sb_key
)

data_handlers.debug_reset_database(client)

def test_add_chunk(client, document_name="test_document.pdf", chunk_no_in_doc=2, chunk="This is test chunk content."):
    response = data_handlers.add_chunk(
        client,
        document_name=document_name,
        document_desc="Test document",
        page_no=5,
        chunk_no_in_doc=chunk_no_in_doc,
        bucket_key="test-bucket-key",
        chunk=chunk,
    )

    assert response.data
    assert len(response.data) == 1

    inserted = response.data[0]

    assert inserted["document_name"] == document_name
    assert inserted["document_description"] == "Test document"
    assert inserted["page_no"] == 5
    assert inserted["chunk_no_in_doc"] == chunk_no_in_doc
    assert inserted["bucket_key"] == "test-bucket-key"
    assert inserted["chunk_contents"] == chunk

    chunk_contents = data_handlers.get_chunk(client, document_name, chunk_no_in_doc)

    assert chunk_contents
    print(chunk_contents)
    assert chunk_contents == chunk

    print("TEST PASSED")


def test_add_relevancy_to_chunk(client, document_name="test_document.pdf", chunk_no_in_doc=2, chunk="This is test chunk content."):
    # First create the chunk that the relevance row refers to.
    data_handlers.add_chunk(
        client,
        document_name,
        "Test document",
        5,
        chunk_no_in_doc,
        "test-key",
        chunk,
    )

    response = data_handlers.add_relevancy_to_chunk(
        client,
        document_name,
        chunk_no_in_doc,
        task_name="scope2_from_utility_bills"
    )

    assert response.data
    assert len(response.data) == 1

    inserted = response.data[0]

    assert inserted["document_name"] == "test_document.pdf"
    assert inserted["chunk_no_in_doc"] == 2
    assert inserted["task_name"] == "scope2_from_utility_bills"

    print("TEST PASSED")

def test_get_chunk_ids(client):
    data_handlers.add_chunk(
        client,
        "doc_a.pdf",
        "Document A",
        1,
        3,
        "bucket-a",
        "Chunk A3",
    )

    data_handlers.add_relevancy_to_chunk(
        client,
        "doc_a.pdf",
        3,
        "scope2_from_utility_bills",
    )

    data_handlers.add_chunk(
        client,
        "doc_b.pdf",
        "Document B",
        2,
        7,
        "bucket-b",
        "Chunk B7",
    )

    data_handlers.add_relevancy_to_chunk(
        client,
        "doc_b.pdf",
        7,
        "scope2_from_utility_bills",
    )

    result = data_handlers.get_chunk_ids(client, "scope2_from_utility_bills")

    assert set(result) == {
        ("doc_a.pdf", 3),
        ("doc_b.pdf", 7),
    }

    print("TEST PASSED")

def test_get_chunk_ids_filters_by_task(client):
    data_handlers.add_chunk(
        client,
        "doc.pdf",
        "Test document",
        1,
        1,
        "bucket",
        "Relevant to task A",
    )

    data_handlers.add_chunk(
        client,
        "doc.pdf",
        "Test document",
        1,
        2,
        "bucket",
        "Relevant to task B",
    )

    data_handlers.add_relevancy_to_chunk(
        client,
        "doc.pdf",
        1,
        "scope2_from_utility_bills",
    )

    data_handlers.add_relevancy_to_chunk(
        client,
        "doc.pdf",
        2,
        "task_b",
    )

    result = data_handlers.get_chunk_ids(client, "scope2_from_utility_bills")

    assert result == [
        ("doc.pdf", 1)
    ]
    assert result[0] == ("doc.pdf", 1)
    assert ("doc.pdf", 2) not in result

def test_add_scope2_transaction_row(client):
    data_handlers.add_chunk(
        client,
        "energy.pdf",
        "Energy report",
        12,
        5,
        "energy-key",
        "Electricity consumption information",
    )

    response = data_handlers.add_scope2_transaction_row(
        client=client,
        document_name="energy.pdf",
        chunk_no_in_doc=5,
        merchant_name="Acme Energy",
        date="2026-01-15",
        product="Electricity",
        cost=1250.50,
        currency="GBP",
        site_name="London Office",
        site_location_city="London",
        site_postcode="NW1 1AA",
        start_date="2026-01-01",
        end_date="2026-01-31",
        ef=0.233,
    )

    assert response.data
    assert len(response.data) == 1

    row = response.data[0]

    assert row["document_name"] == "energy.pdf"
    assert row["chunk_no_in_doc"] == 5
    assert row["merchant_name"] == "Acme Energy"
    assert row["product"] == "Electricity"
    assert float(row["cost"]) == 1250.50
    assert row["currency"] == "GBP"
    assert row["site_name"] == "London Office"
    assert row["site_city"] == "London"
    assert row["site_postcode"] == "NW1 1AA"
    assert float(row["emission_factor"]) == 0.233

def test_get_display_rows_filters_by_task(client):
    # Chunk 1
    data_handlers.add_chunk(
        client,
        "doc.pdf",
        "Test document",
        1,
        1,
        "bucket",
        "Chunk one",
    )

    data_handlers.add_relevancy_to_chunk(
        client,
        "doc.pdf",
        1,
        "scope2_from_utility_bills",
    )

    data_handlers.add_scope2_transaction_row(
        client,
        "doc.pdf",
        1,
        "Merchant A",
        "2026-01-10",
        "Electricity",
        100,
        "GBP",
        "Site A",
        "London",
        "NW1",
        "2026-01-01",
        "2026-01-31",
        0.2,
    )

    # Chunk 2
    data_handlers.add_chunk(
        client,
        "doc.pdf",
        "Test document",
        2,
        2,
        "bucket",
        "Chunk two",
    )

    data_handlers.add_relevancy_to_chunk(
        client,
        "doc.pdf",
        2,
        "scope2_from_utility_bills",
    )

    data_handlers.add_scope2_transaction_row(
        client,
        "doc.pdf",
        2,
        "Merchant B",
        "2026-02-10",
        "Gas",
        200,
        "GBP",
        "Site B",
        "Manchester",
        "M1",
        "2026-02-01",
        "2026-02-28",
        0.3,
    )

    # Chunk 3 — NOT relevant to scope2
    data_handlers.add_chunk(
        client,
        "doc.pdf",
        "Test document",
        3,
        3,
        "bucket",
        "Chunk three",
    )


    data_handlers.add_relevancy_to_chunk(
        client,
        "doc.pdf",
        3,
        "task_b",
    )

    data_handlers.add_scope2_transaction_row(
        client,
        "doc.pdf",
        3,
        "Merchant C",
        "2026-03-10",
        "Fuel",
        300,
        "GBP",
        "Site C",
        "Bristol",
        "BS1",
        "2026-03-01",
        "2026-03-31",
        0.4,
    )

    #'''
    result = data_handlers.get_display_rows(client, "scope2_from_utility_bills")
    for row in result:
        print("CHUNK:" + str(row["document_name"]) + str(row["chunk_no_in_doc"]))
        print("RELEVANCES:" + str(row.get("raw_chunk_relevances")))
        print("")

    assert result is not None
    assert len(result) == 2

    chunk_numbers = {
        row["chunk_no_in_doc"]
        for row in result
    }

    assert chunk_numbers == {1, 2}
    #'''

def test_get_display_rows_handles_multiple_transactions(client):
    data_handlers.add_chunk(
        client,
        "multi.pdf",
        "Multiple transaction test",
        1,
        1,
        "bucket",
        "Chunk with multiple transactions",
    )

    data_handlers.add_relevancy_to_chunk(
        client,
        "multi.pdf",
        1,
        "scope2_from_utility_bills",
    )

    data_handlers.add_scope2_transaction_row(
        client,
        "multi.pdf",
        1,
        "Merchant A",
        "2026-01-01",
        "Electricity",
        100,
        "GBP",
        "Site A",
        "London",
        "NW1",
        "2026-01-01",
        "2026-01-31",
        0.2,
    )

    data_handlers.add_scope2_transaction_row(
        client,
        "multi.pdf",
        1,
        "Merchant B",
        "2026-02-01",
        "Gas",
        200,
        "GBP",
        "Site B",
        "London",
        "NW1",
        "2026-02-01",
        "2026-02-28",
        0.3,
    )

    result = data_handlers.get_display_rows(client, "scope2_from_utility_bills")

    assert len(result) == 1

    transactions = result[0]["scope2_transactions"]

    assert len(transactions) == 2

    merchants = {
        transaction["merchant_name"]
        for transaction in transactions
    }

    assert merchants == {"Merchant A", "Merchant B"}

test_add_chunk(client, document_name="test_document.pdf", chunk_no_in_doc=2, chunk="This is test chunk content.")
test_add_chunk(client, document_name="test_document.pdf", chunk_no_in_doc=3, chunk="This is not test chunk content.")
test_add_chunk(client, document_name="document_test.pdf", chunk_no_in_doc=3, chunk="This is not test chunk content.")
test_add_chunk(client, document_name="test_document.pdf", chunk_no_in_doc=3, chunk="This is not test chunk content.")
assert data_handlers.get_chunk(client, document_name="test_document.pdf", chunk_no_in_doc=2) == "This is test chunk content."
assert data_handlers.get_chunk(client, document_name="test_document.pdf", chunk_no_in_doc=3) == "This is not test chunk content."
print("TEST PASSED")

test_add_relevancy_to_chunk(client, document_name="test_document.pdf", chunk_no_in_doc=2, chunk="This is test chunk content.")
data_handlers.debug_reset_database(client)
test_get_chunk_ids(client)
data_handlers.debug_reset_database(client)
test_get_chunk_ids_filters_by_task(client)
data_handlers.debug_reset_database(client)

data_handlers.debug_reset_database(client)

test_add_scope2_transaction_row(client)
print("TEST PASSED")

data_handlers.debug_reset_database(client)

test_get_display_rows_filters_by_task(client)
print("TEST PASSED")

data_handlers.debug_reset_database(client)

test_get_display_rows_handles_multiple_transactions(client)
print("TEST PASSED")

data_handlers.debug_reset_database(client)