# run.pay — Agent Marketplace

Stripe-native marketplace where AI agents autonomously discover and purchase API services. Pay-per-call, no accounts needed.

## MCP Endpoint
https://runpay-backend-visibility-production.up.railway.app/mcp

## Connect your agent
Add to your MCP config:
```json
{"mcpServers": {"runpay": {"url": "https://runpay-backend-visibility-production.up.railway.app/mcp"}}}
```

## Available tools
- **list_services** — Browse all available services and prices
- **call_service** — Call a service and pay automatically via Stripe

## How it works
1. Sellers publish any API function and set a price per call
2. AI agents discover services via MCP protocol
3. Stripe charges the agent per call automatically
4. Sellers receive payouts via Stripe Connect

## Links
- 🌐 Site: https://graceful-crepe-eb5d0f.netlify.app
- 📝 Sell your API: https://graceful-crepe-eb5d0f.netlify.app/signup.html
- 📊 Dashboard: https://playful-arithmetic-66a284.netlify.app
