run.pay — Agent Marketplace

Stripe-native marketplace where AI agents autonomously discover and purchase API services. Pay-per-call, no accounts needed.

MCP Endpoint
https://runpay-backend-visibility-production.up.railway.app/mcp
Connect your agent
Claude Desktop
Add to ~/Library/Application Support/Claude/claude_desktop_config.json:
json{
  "mcpServers": {
    "runpay": {
      "url": "https://runpay-backend-visibility-production.up.railway.app/mcp"
    }
  }
}
Cursor
Add to .cursor/mcp.json:
json{
  "mcpServers": {
    "runpay": {
      "url": "https://runpay-backend-visibility-production.up.railway.app/mcp",
      "transport": "http"
    }
  }
}
Available tools
ToolDescriptionlist_servicesBrowse all available services and pricescall_serviceCall a service and pay automatically via Stripe
Available services
ServicePriceDescriptionPhone Validator$0.60/callValidate phone numbers worldwide. Returns country, line type, E164 formatPhone Validator Batch$5.00/batchValidate up to 1000 numbers in one callWeb Scraper Pro$0.60/callExtract title, content, links, emails from any URLWeb Scraper Batch$3.00/batchScrape up to 10 URLs in parallelPDF Generator$0.60/callGenerate professional PDFs (invoices, reports, contracts)Screenshot API$0.60/callCapture any website as PNG with site accessibility check
Python SDK
pythonpip install requests
pythonfrom runpay_sdk import RunPay

# Initialize (sandbox=True for testing without payment)
rp = RunPay(agent_id="my-agent-001", sandbox=False)

# Validate a phone number — $0.60
result = rp.validate_phone("+33612345678")
print(result['country'])     # France
print(result['line_type'])   # mobile
print(result['is_valid'])    # True

# Validate 1000 numbers in one call — $5.00
result = rp.validate_phones_batch(["+33612345678", "+1234567890"])
print(f"{result['valid']}/{result['total']} valid")

# Scrape a website — $0.60
result = rp.scrape("https://example.com")
print(result['title'])
print(result['emails'])

# Scrape 10 URLs in parallel — $3.00
result = rp.scrape_batch(["https://site1.com", "https://site2.com"])

# Generate an invoice PDF — $0.60
result = rp.generate_pdf(
    title="Invoice #001",
    doc_type="invoice",
    language="fr",
    data={
        "client": "Acme Corp\n123 Rue de Paris",
        "invoice_number": "INV-001",
        "tax_rate": 20,
        "items": [
            {"description": "Web Scraping", "qty": 10, "price": 0.60}
        ]
    }
)
with open("invoice.html", "w") as f:
    f.write(result['html'])

# Take a screenshot — $0.60
result = rp.screenshot("https://example.com")
print(result['screenshot_url'])
print(result['usage']['embed'])  # <img> tag ready to use
Download SDK: runpay_sdk.py
How it works

Sellers publish any API function and set a price per call
AI agents discover services via MCP protocol automatically
Stripe charges the agent per call automatically
Sellers receive payouts directly via Stripe Connect

Sandbox mode (test without payment)
python# No real payment — perfect for development
rp = RunPay(agent_id="my-agent-001", sandbox=True)
result = rp.validate_phone("+33612345678")
Or via API directly:
bashcurl -X POST https://runpay-backend-visibility-production.up.railway.app/api/sandbox/call/SERVICE_ID \
  -H "Content-Type: application/json" \
  -d '{"agent_id":"my-agent","payload":{"phone":"+33612345678"}}'
Setup your agent wallet
Before calling paid services, your agent needs a payment card attached.
👉 Setup Agent Wallet
Sell your API
Publish any function and earn per agent call via Stripe.
👉 Become a seller
Links
🌐 Sitegetrunpay.com📖 Docsgetrunpay.com/docs.html📝 Sell your APIgetrunpay.com/signup.html🤖 Agent Setupgetrunpay.com/agent-setup.html📊 Dashboardplayful-arithmetic-66a284.netlify.app🔍 Smitherysmithery.ai/servers/runpay/marketplace
