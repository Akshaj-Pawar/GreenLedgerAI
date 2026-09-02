# GreenLedgerAI
AI pipeline for Green Ledger Internship

To start:

1. Create a cache folder within the main project directory, alongside the main scripts

2. Create an AWS cloud account with 3 bucket setup and store the API key

3. Set up env file with the following fields, spelled correctly:

  AWS_ACCESS_KEY_ID
  AWS_SECRET_ACCESS_KEY
  AWS_DEFAULT_REGION
  - use details from AWS cloud account with a S3 bucket set up
  
  CACHE_PATH = "cache/"  (can be overridden to wherever it is convenient for you the user to cache the tmp files of uploaded documents)
  
  SUPABASE_PASSWORD
  SUPABASE_URL
  SUPABASE_ANON_KEY
  SUPABASE_ADMIN_KEY
  - see accompanying word doc
  
  OPENAI_API_KEY 
  - get from personal OPENAI_API account
  
  CORS_ALLOWED_ORIGINS=["http://localhost:8000"] (can be overridden)

4. Download Dependencies in requirements.txt
   Run commands:
   python -m venv .venv
   source .venv/bin/activate (macOS) or .venv\Scripts\Activate.ps1 (Linux / Windows)
   pip install -r requirements.txt
   
   
6. Run Command: uvicorn main:app --reload

7. Follow the link in the terminal


To test the sign in / sign up: 
curl -X POST 'https://<SUPABASE_URL>.supabase.co/auth/v1/token?grant_type=password' \
  -H "apikey: <supabase-anon-key>" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpassword"}'

And then (where access token is the output of the previous): 
curl http://localhost:8000/documents -H "Authorization: Bearer <access_token>"