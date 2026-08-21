import uuid
import os
import boto3
from dotenv import load_dotenv
import tempfile
import asyncio
from supabase import create_client
from pypdf import PdfReader
from fastapi import APIRouter, Form, File, UploadFile, BackgroundTasks, HTTPException
from starlette.concurrency import run_in_threadpool
from typing import List
from reportlab.pdfgen import canvas
from unittest.mock import MagicMock, patch

import data_handlers
import parser

def two_page_pdf(tmp_path):
    pdf_path = tmp_path + "test.pdf"

    c = canvas.Canvas(str(pdf_path))

    c.drawString(100, 700, "Page one test content")
    c.showPage()

    c.drawString(100, 700, "Page two test content")
    c.showPage()

    c.save()

    return str(pdf_path)

def test_find_relevances_utility_bill(client):
    data_handlers.add_chunk(client, "test.pdf", "Utility bill", 0, 0, "", "Electricity consumption: 1000 kWh")
    parser.find_relevances(
        client,
        text="Electricity consumption: 1000 kWh",
        text_description="Utility bill",
        document_name="test.pdf",
        chunk_no=0,
        special_types=["utility_bill"],
    )

    result = (
        client
        .table("raw_chunk_relevances")
        .select("*")
        .execute()
    )

    assert len(result.data) == 1

    row = result.data[0]

    assert row["document_name"] == "test.pdf"
    assert row["chunk_no_in_doc"] == 0
    assert row["task_name"] == "scope2_from_utility_bills"

def test_find_relevances_no_matching_special_type(client):
    data_handlers.add_chunk(client, "test.pdf", "Utility bill", 0, 0, "", "Electricity consumption: 1000 kWh")
    parser.find_relevances(
        client,
        text="Some unrelated text",
        text_description="Other document",
        document_name="test.pdf",
        chunk_no=0,
        special_types=["something_else"],
    )

    result = (
        client
        .table("raw_chunk_relevances")
        .select("*")
        .execute()
    )

    assert result.data == []

def test_parse_pdf_to_chunks(client, pdf_path):
    parser.parse_pdf_to_chunks(
        pdf_path=pdf_path,
        document_name="test.pdf",
        document_desc="Test document",
        special_types=["utility_bill"],
        db_connection=client,
        bucket=None,
        bucket_key="test-key",
    )

    chunks = (
        client
        .table("raw_text_cache")
        .select("*")
        .order("chunk_no_in_doc")
        .execute()
    )

    assert len(chunks.data) == 2

    assert chunks.data[0]["document_name"] == "test.pdf"
    assert chunks.data[0]["page_no"] == 1
    assert chunks.data[0]["chunk_no_in_doc"] == 0

    assert chunks.data[1]["document_name"] == "test.pdf"
    assert chunks.data[1]["page_no"] == 2
    assert chunks.data[1]["chunk_no_in_doc"] == 1

def test_parse_pdf_to_chunks_creates_relevances(client, pdf_path):
    parser.parse_pdf_to_chunks(
        pdf_path=pdf_path,
        document_name="test.pdf",
        document_desc="Test document",
        special_types=["utility_bill"],
        db_connection=client,
        bucket=None,
        bucket_key="test-key",
    )

    relevances = (
        client
        .table("raw_chunk_relevances")
        .select("*")
        .order("chunk_no_in_doc")
        .execute()
    )

    assert len(relevances.data) == 2

    assert relevances.data[0]["chunk_no_in_doc"] == 0
    assert relevances.data[0]["task_name"] == "scope2_from_utility_bills"

    assert relevances.data[1]["chunk_no_in_doc"] == 1
    assert relevances.data[1]["task_name"] == "scope2_from_utility_bills"


sb_url = os.getenv("SUPABASE_URL")
sb_key = os.getenv("SUPABASE_ADMIN_KEY")

client = create_client(
    sb_url,
    sb_key
)

#cache_path = os.getenv("CACHE_PATH")
#two_page_pdf(cache_path)

#data_handlers.debug_reset_database(client)

#test_find_relevances_utility_bill(client)
#print("TESTS PASSED")

#data_handlers.debug_reset_database(client)

#test_find_relevances_no_matching_special_type(client)
#print("TESTS PASSED")

data_handlers.debug_reset_database(client)

pdf_path = "cache/test.pdf"

#test_parse_pdf_to_chunks(client, pdf_path)
#print("TESTS PASSED")

#data_handlers.debug_reset_database(client)

#test_parse_pdf_to_chunks_creates_relevances(client, pdf_path)
#print("TESTS PASSED")

#data_handlers.debug_reset_database(client)

document_name = "test.pdf"
description = "Test document"
special_types = ["utility_bill"]

parser.main_orchestrator(pdf_path, document_name, description, special_types)

print("CHECK DB")

# main orchestrator test
# full parser test