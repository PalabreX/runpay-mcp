"""
run.pay Python SDK
==================
Official Python SDK for the run.pay marketplace.
AI agents can discover and purchase API services automatically via Stripe.

Installation:
    pip install requests

Usage:
    from runpay import RunPay
    
    rp = RunPay(agent_id="my-agent-001")
    result = rp.call("d5ff985c-e50a-431a-84f1-b339ae0700b8", {"phone": "+33612345678"})
"""

import requests
import json
from typing import Optional, Dict, Any, List


class RunPayError(Exception):
    """Base exception for run.pay errors"""
    def __init__(self, message: str, status_code: int = None, refunded: bool = False):
        self.message = message
        self.status_code = status_code
        self.refunded = refunded
        super().__init__(message)


class RunPay:
    """
    run.pay Python SDK
    
    Args:
        agent_id (str): Unique identifier for your AI agent
        base_url (str): API base URL (default: production)
        sandbox (bool): Use sandbox mode (no real payments)
        timeout (int): Request timeout in seconds (default: 30)
    
    Example:
        rp = RunPay(agent_id="my-agent-001")
        
        # List available services
        services = rp.list_services()
        
        # Call a service
        result = rp.call("SERVICE_ID", {"phone": "+33612345678"})
    """
    
    BASE_URL = "https://runpay-backend-visibility-production.up.railway.app"
    
    # Service IDs constants
    PHONE_VALIDATOR = "d5ff985c-e50a-431a-84f1-b339ae0700b8"
    PHONE_VALIDATOR_BATCH = "c84bd36b-7ff1-4427-9fca-4d47eca445d3"
    WEB_SCRAPER = "f4da1369-7ac7-48b0-8ca9-d8223e162080"
    WEB_SCRAPER_BATCH = "83f40c2b-a581-4ae2-b73f-112e9a1e24a9"
    PDF_GENERATOR = "461d5316-a2e7-4cc7-b462-72ae086344e5"
    SCREENSHOT = "705f576d-aab8-4394-9cdd-ff64aadb3d58"
    
    def __init__(
        self, 
        agent_id: str, 
        base_url: str = None,
        sandbox: bool = False,
        timeout: int = 30
    ):
        if not agent_id:
            raise ValueError("agent_id is required")
        
        self.agent_id = agent_id
        self.base_url = (base_url or self.BASE_URL).rstrip('/')
        self.sandbox = sandbox
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': f'runpay-python-sdk/1.0.0 agent/{agent_id}'
        })
    
    def _request(self, method: str, path: str, **kwargs) -> Dict:
        """Make an API request"""
        url = f"{self.base_url}{path}"
        try:
            response = self.session.request(
                method, url, 
                timeout=self.timeout,
                **kwargs
            )
            data = response.json()
            
            if not response.ok:
                raise RunPayError(
                    message=data.get('error', f'HTTP {response.status_code}'),
                    status_code=response.status_code,
                    refunded=data.get('refunded', False)
                )
            return data
        except requests.exceptions.Timeout:
            raise RunPayError("Request timed out", status_code=408)
        except requests.exceptions.ConnectionError:
            raise RunPayError("Connection error — check your internet connection")
        except json.JSONDecodeError:
            raise RunPayError("Invalid response from server")
    
    def list_services(self, category: str = None, search: str = None) -> List[Dict]:
        """
        List all available services on the marketplace.
        
        Args:
            category: Filter by category (DATA, AI, MEDIA, SEARCH)
            search: Search by name or description
        
        Returns:
            List of service dictionaries
        
        Example:
            services = rp.list_services(category="DATA")
            for s in services:
                print(f"{s['name']} — ${s['price_per_call']}/call")
        """
        params = {}
        if category:
            params['category'] = category
        if search:
            params['search'] = search
        
        if self.sandbox:
            data = self._request('GET', '/api/sandbox/services', params=params)
        else:
            data = self._request('GET', '/api/marketplace', params=params)
        
        return data.get('services', [])
    
    def get_service(self, service_id: str) -> Dict:
        """
        Get details of a specific service.
        
        Args:
            service_id: The service UUID
        
        Returns:
            Service dictionary with name, price, description, etc.
        """
        return self._request('GET', f'/api/marketplace/{service_id}')
    
    def call(self, service_id: str, payload: Dict = None) -> Dict:
        """
        Call a service and pay automatically via Stripe.
        
        Args:
            service_id: The service UUID (use RunPay.PHONE_VALIDATOR etc.)
            payload: Data to send to the service
        
        Returns:
            Dict with 'result' key containing the service response
        
        Raises:
            RunPayError: If payment fails or service is unavailable
        
        Example:
            # Validate a phone number
            result = rp.call(RunPay.PHONE_VALIDATOR, {"phone": "+33612345678"})
            print(result['result']['country'])  # France
            
            # Scrape a website
            result = rp.call(RunPay.WEB_SCRAPER, {"url": "https://example.com"})
            print(result['result']['title'])
        """
        endpoint = '/api/sandbox/call' if self.sandbox else '/api/call'
        
        return self._request('POST', f'{endpoint}/{service_id}', json={
            'agent_id': self.agent_id,
            'payload': payload or {}
        })
    
    # ─── CONVENIENCE METHODS ──────────────────────────────────────────────────
    
    def validate_phone(self, phone: str) -> Dict:
        """
        Validate a phone number.
        
        Args:
            phone: Phone number in E164 format (e.g. "+33612345678")
        
        Returns:
            Dict with is_valid, country, line_type, e164, local_format, risk_level
        
        Example:
            result = rp.validate_phone("+33612345678")
            if result['is_valid']:
                print(f"Valid {result['line_type']} in {result['country']}")
        """
        response = self.call(self.PHONE_VALIDATOR, {"phone": phone})
        return response.get('result', response)
    
    def validate_phones_batch(self, phones: List[str]) -> Dict:
        """
        Validate up to 1000 phone numbers in one call.
        
        Args:
            phones: List of phone numbers
        
        Returns:
            Dict with total, valid, invalid, by_country, results
        
        Example:
            result = rp.validate_phones_batch(["+33612345678", "+1234567890"])
            print(f"{result['valid']}/{result['total']} valid numbers")
        """
        response = self.call(self.PHONE_VALIDATOR_BATCH, {"phones": phones})
        return response.get('result', response)
    
    def scrape(self, url: str, extract: List[str] = None) -> Dict:
        """
        Scrape a website and extract content.
        
        Args:
            url: URL to scrape
            extract: Fields to extract (title, description, content, links, images, emails, og)
        
        Returns:
            Dict with title, content, links, images, emails, language, etc.
        
        Example:
            result = rp.scrape("https://example.com")
            print(result['title'])
            print(result['emails'])  # Any emails found on the page
        """
        payload = {"url": url}
        if extract:
            payload["extract"] = extract
        response = self.call(self.WEB_SCRAPER, payload)
        return response.get('result', response)
    
    def scrape_batch(self, urls: List[str], extract: List[str] = None) -> Dict:
        """
        Scrape up to 10 URLs in parallel.
        
        Args:
            urls: List of URLs (max 10)
            extract: Fields to extract for each URL
        
        Returns:
            Dict with total, successful, failed, results
        
        Example:
            result = rp.scrape_batch(["https://site1.com", "https://site2.com"])
            for r in result['results']:
                print(r['url'], r['title'])
        """
        payload = {"urls": urls}
        if extract:
            payload["extract"] = extract
        response = self.call(self.WEB_SCRAPER_BATCH, payload)
        return response.get('result', response)
    
    def generate_pdf(
        self, 
        title: str, 
        content: str = None, 
        doc_type: str = "document",
        data: Dict = None,
        theme: str = "default",
        language: str = "en"
    ) -> Dict:
        """
        Generate a professional PDF document.
        
        Args:
            title: Document title
            content: Text content
            doc_type: Document type (document, invoice, report, contract)
            data: Structured data (for invoices, reports, etc.)
            theme: Visual theme (default, dark, blue, minimal)
            language: Language for date formatting (en, fr)
        
        Returns:
            Dict with html, html_base64, size_bytes
        
        Example:
            # Generate an invoice
            result = rp.generate_pdf(
                title="Invoice #001",
                doc_type="invoice",
                language="fr",
                data={
                    "client": "Acme Corp",
                    "invoice_number": "INV-001",
                    "tax_rate": 20,
                    "items": [
                        {"description": "Service", "qty": 1, "price": 100}
                    ]
                }
            )
            # Save the HTML as PDF using any HTML-to-PDF library
            with open("invoice.html", "w") as f:
                f.write(result['html'])
        """
        response = self.call(self.PDF_GENERATOR, {
            "title": title,
            "content": content,
            "type": doc_type,
            "data": data,
            "theme": theme,
            "language": language
        })
        return response.get('result', response)
    
    def screenshot(self, url: str, width: int = 1280, height: int = 800, mobile: bool = False) -> Dict:
        """
        Capture a website screenshot.
        
        Args:
            url: URL to screenshot
            width: Viewport width (default: 1280)
            height: Viewport height (default: 800)
            mobile: Use mobile viewport (default: False)
        
        Returns:
            Dict with screenshot_url, thumbnail_url, site_info, usage (embed HTML/Markdown)
        
        Example:
            result = rp.screenshot("https://example.com")
            print(result['screenshot_url'])  # Direct image URL
            print(result['usage']['embed'])  # HTML img tag
        """
        response = self.call(self.SCREENSHOT, {
            "url": url,
            "width": width,
            "height": height,
            "mobile": mobile
        })
        return response.get('result', response)
    
    def setup_wallet(self) -> Dict:
        """
        Register this agent and get a Stripe setup intent to attach a payment card.
        
        Returns:
            Dict with wallet_id, agent_id, client_secret (for Stripe.js)
        
        Note:
            After getting client_secret, use Stripe.js to confirm the card setup,
            then call confirm_card() with the payment method ID.
        """
        return self._request('POST', '/api/agents/register', json={
            'agent_id': self.agent_id
        })
    
    def get_wallet(self) -> Dict:
        """
        Get wallet information for this agent.
        
        Returns:
            Dict with agent_id, stripe_payment_method_id, total_spent, card info
        """
        return self._request('GET', f'/api/agents/wallet?agent_id={self.agent_id}')
    
    def __repr__(self):
        mode = "SANDBOX" if self.sandbox else "PRODUCTION"
        return f"RunPay(agent_id='{self.agent_id}', mode={mode})"


# ─── USAGE EXAMPLES ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("run.pay Python SDK — Examples")
    print("=" * 40)
    
    # Initialize in sandbox mode (no real payments)
    rp = RunPay(agent_id="my-agent-001", sandbox=True)
    print(f"SDK initialized: {rp}")
    
    # List available services
    print("\n📋 Available services:")
    try:
        services = rp.list_services()
        for s in services:
            print(f"  • {s['name']} — ${s['price_per_call']}/call [{s['category']}]")
    except RunPayError as e:
        print(f"  Error: {e}")
    
    print("\n✅ SDK ready. Set sandbox=False for production.")
    print("\nQuick start:")
    print("  rp = RunPay(agent_id='my-agent-001')")
    print("  result = rp.validate_phone('+33612345678')")
    print("  result = rp.scrape('https://example.com')")
    print("  result = rp.screenshot('https://example.com')")
