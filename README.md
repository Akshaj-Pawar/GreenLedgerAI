# GreenLedgerAI
AI pipeline for Green Ledger Internship

Tasks To Implement Basic System Plan:
•⁠  ⁠PDF / Spreadsheet to Text Parse, Document upload form 
•⁠  ⁠Per task extraction prompt (first task: extract energy bill figures for scope 2 estimation: ‘for each separate energy bill in this document, return a JSON document containing the supplier name, location and cost / energy units used’ (plus potentially more))
•⁠  ⁠Implement LLM API Call (run per selected task and per relevant document)
•⁠  ⁠per document candidate rows uploaded into a SQL cache for human review


Done:
•⁠  ⁠Relevance Function (currently just asks the user to declare the document type - defines which documents get sent to the LLM for each separate task)
•⁠  ⁠Dummy ‘estimation algorithm’. Which will be subbed out for the real algorithm in production. This is not an AI phase


Commands:
create api route: uvicorn main:app --reload
curl post test: curl -X POST http://localhost:8000/static/documents \
  -F "document_name=test doc" \
  -F "description=a test" \
  -F "file=@/path/to/file.pdf"