#1. Direct LLM call
#   └── Does OpenAI respond?

#2. Direct LLM call + JSON assertions
#   └── Is response.transactions an array of objects?
#   └── Are all expected fields present?
#   └── Can fields be null?

#3. task_scope2_from_utility_bills()
#   └── Does LLM response become database rows?

#4. Multiple transactions
#   └── Does the array handling work?

#5. execute_task("scope2_from_utility_bills")
#   └── Does the whole backend pipeline work?

#6. execute_task("nonexistent_task")
#   └── Does error handling work?

#7. execute_task() with no relevant chunks
#   └── Does the empty case work?

#8. Real relevant PDF
#   └── Full extraction experiment

#9. Real irrelevant PDF
#   └── See whether model correctly produces zero/no transactions

from openai import OpenAI
import json
import os
from dotenv import load_dotenv
from supabase import create_client

import data_handlers
import estimation_algs
import LLM_call

def assert_key():
    assert os.getenv("OPENAI_API_KEY")

def test_task_scope2_from_utility_bill_returns_transaction(client, openai_client):

    document_name = "llm_test.pdf"
    chunk_no = 0

    data_handlers.add_chunk(
        client,
        document_name,
        "Test utility bill",
        1,
        chunk_no,
        "test-key",
        """
        British Gas electricity bill.
        Billing period: 1 January 2025 to 31 January 2025.
        Electricity consumption: 500 kWh.
        Amount due: £150.
        Site: Example Office.
        London.
        SW1A 1AA.
        """
    )

    transactions = LLM_call.task_scope2_from_utility_bills(
        document_name,
        chunk_no,
        openai_client,
        client
    )


    # Test the returned LLM output
    assert isinstance(transactions, list)
    assert len(transactions) >= 1

    transaction = transactions[0]
    print(transaction)

    assert isinstance(transaction, dict)

    assert "description" in transaction
    assert "date" in transaction
    assert "merchant_name" in transaction
    assert "product" in transaction
    assert "cost" in transaction
    assert "currency" in transaction
    assert "kwhs" in transaction
    assert "site_name" in transaction
    assert "site_location_city" in transaction
    assert "site_postcode" in transaction
    assert "start_date" in transaction
    assert "end_date" in transaction

    result = (
        client
        .table("scope2_transactions")
        .select("*")
        .eq("document_name", document_name)
        .eq("chunk_no_in_doc", chunk_no)
        .execute()
    )

    assert result.data is not None
    assert len(result.data) >= 1

    transaction = result.data[0]

    assert "merchant_name" in transaction
    assert "billing_period_start_date" in transaction
    assert "cost" in transaction
    assert "currency" in transaction

def test_task_scope2_allows_missing_fields(client, openai_client):

    document_name = "incomplete_bill.pdf"
    chunk_no = 0

    data_handlers.add_chunk(
        client,
        document_name,
        "Incomplete test document",
        1,
        chunk_no,
        "test-key",
        """
        Electricity payment to British Gas.
        Amount paid: £200.
        """
    )

    transactions = LLM_call.task_scope2_from_utility_bills(
        document_name,
        chunk_no,
        openai_client,
        client
    )

    assert isinstance(transactions, list)
    assert len(transactions) >= 1

    transaction = transactions[0]
    print(transaction)

    # All schema fields should still exist
    assert "merchant_name" in transaction
    assert "date" in transaction
    assert "cost" in transaction
    assert "currency" in transaction
    assert "site_name" in transaction
    assert "site_location_city" in transaction
    assert "site_postcode" in transaction
    assert "start_date" in transaction
    assert "end_date" in transaction

    result = (
        client
        .table("scope2_transactions")
        .select("*")
        .eq("document_name", document_name)
        .eq("chunk_no_in_doc", chunk_no)
        .execute()
    )

    assert len(result.data) >= 1

    transaction = result.data[0]

    # At least one of these should plausibly be absent
    # from the source text.
    assert transaction["site_city"] is None \
        or transaction["site_postcode"] is None \
        or transaction["billing_period_start_date"] is None \
        or transaction["billing_period_end_date"] is None

def test_task_scope2_can_return_multiple_transactions(client, openai_client):
    
    document_name = "multiple_transactions.pdf"
    chunk_no = 0

    data_handlers.add_chunk(
        client,
        document_name,
        "Multiple transaction test",
        1,
        chunk_no,
        "test-key",
        """
        British Gas electricity payment: £100.
        EDF electricity payment: £200.
        """
    )

    transactions = LLM_call.task_scope2_from_utility_bills(
        document_name,
        chunk_no,
        openai_client,
        client
    )
    print(transactions)

    assert isinstance(transactions, list)
    assert len(transactions) >= 1

    for transaction in transactions:
        assert isinstance(transaction, dict)

        assert "description" in transaction
        assert "date" in transaction
        assert "merchant_name" in transaction
        assert "product" in transaction
        assert "cost" in transaction
        assert "currency" in transaction
        assert "kwhs" in transaction
        assert "site_name" in transaction
        assert "site_location_city" in transaction
        assert "site_postcode" in transaction
        assert "start_date" in transaction
        assert "end_date" in transaction



def test_execute_task_scope2(client):

    document_name = "execute_task_test.pdf"
    chunk_no = 0

    data_handlers.add_chunk(
        client,
        document_name,
        "Test utility bill",
        1,
        chunk_no,
        "test-key",
        """
        Electricity bill from British Gas.
        Amount due: £150.
        Electricity consumption: 500 kWh.
        """
    )

    data_handlers.add_relevancy_to_chunk(
        client,
        document_name,
        chunk_no,
        "scope2_from_utility_bills"
    )

    result = LLM_call.execute_task("scope2_from_utility_bills")

    assert result["success"] is True
    assert result["error"] is None
    assert result["rows"] is not None
    assert isinstance(result["rows"], list)

def test_execute_task_unknown_task():
    result = LLM_call.execute_task("this_task_does_not_exist")

    assert result["success"] is False
    assert result["rows"] is None
    assert result["error"] == "Unknown task: this_task_does_not_exist"

def test_execute_task_with_no_relevant_chunks():
    result = LLM_call.execute_task("scope2_from_utility_bills")

    assert result["success"] is True
    assert result["error"] is None
    assert isinstance(result["rows"], list)



load_dotenv()

sb_url = os.getenv("SUPABASE_URL")
sb_key = os.getenv("SUPABASE_ADMIN_KEY")

client = create_client(
    sb_url,
    sb_key
)

client = create_client(
    sb_url,
    sb_key
)

key = os.getenv("OPENAI_API_KEY")
openai_client = OpenAI()

#assert_key()
#print("TEST PASSED")

#data_handlers.debug_reset_database(client)
#test_task_scope2_from_utility_bill_returns_transaction(client, openai_client)
#print("TEST PASSED")

#data_handlers.debug_reset_database(client)
#test_task_scope2_allows_missing_fields(client, openai_client)
#print("TEST PASSED")

#data_handlers.debug_reset_database(client)
#test_task_scope2_can_return_multiple_transactions(client, openai_client)
#print("TEST PASSED")

#data_handlers.debug_reset_database(client)
#test_execute_task_scope2(client)
#print("TEST PASSED")

#data_handlers.debug_reset_database(client)
#test_execute_task_unknown_task()
#print("TEST PASSED")

#data_handlers.debug_reset_database(client)
#test_execute_task_with_no_relevant_chunks()
#print("TEST PASSED")