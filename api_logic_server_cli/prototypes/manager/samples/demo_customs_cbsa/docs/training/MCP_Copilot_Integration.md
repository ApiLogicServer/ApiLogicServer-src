# MCP Integration Guide for Copilot

## Overview

This GenAI-Logic project implements **MCP Server Executor** architecture - providing business logic services that AI assistants (like GitHub Copilot) can invoke to read and update database entities using natural language.

**Key Distinction**: GenAI-Logic is NOT a standard "MCP Protocol Server" (JSON-RPC over stdio). Instead, it's a **business logic microservice** that AI assistants interact with via authenticated REST API calls. This architecture is more scalable and enterprise-ready than stdio-based MCP servers.

## Architecture

```
┌─────────────────────────────────┐
│  GitHub Copilot / Claude        │  Natural language interface
│  (MCP Client / AI Assistant)    │
└────────────┬────────────────────┘
             │ HTTP REST API (JSON:API format)
             │ JWT Authentication
┌────────────▼────────────────────┐
│  GenAI-Logic Server             │  MCP Server Executor
│  (Flask + LogicBank)            │  - Business logic enforcement
│                                 │  - Constraint validation
│  Endpoints:                     │  - Declarative rules (44X reduction)
│  - /api/auth/login              │  - Schema metadata
│  - /api/{Entity}                │
│  - /.well-known/mcp.json        │
│  - /mcp                         │
└────────────┬────────────────────┘
             │
┌────────────▼────────────────────┐
│  Database (SQLAlchemy ORM)      │
└─────────────────────────────────┘
```

## How Copilot Acts as MCP Client

GitHub Copilot can serve as an interactive MCP client by:

1. **Authenticating** - Login to obtain JWT token
2. **Translating** - Convert natural language to API operations
3. **Executing** - Make authenticated HTTP calls
4. **Reporting** - Present results or explain constraint violations

## ⚠️ CRITICAL SAFETY RULES FOR COPILOT

**When acting as MCP client, Copilot MUST follow these rules:**

### Rule 1: NEVER Update Data Without Explicit Permission
- ❌ **WRONG**: User asks "update quantity to 100" → fails constraint → Copilot changes credit limit to make it work
- ✅ **CORRECT**: User asks "update quantity to 100" → fails constraint → Copilot reports the constraint violation and asks what to do

### Rule 2: Constraint Violations Are SUCCESS, Not Problems to Bypass
- When update returns error code 2001, this demonstrates business logic is **working correctly**
- **DO NOT** try to "fix" constraints by modifying other data
- **DO** report: "✅ Business logic prevented this operation because [reason]"

### Rule 3: Only Perform the Requested Operation
- If user asks to update Field A, **only update Field A**
- Do not modify Field B, Field C, or related entities to "help" the operation succeed
- Let business rules enforce constraints - that's their job!

### Rule 4: Ask Permission for Side Effects
- Before updating any data beyond what user explicitly requested, **ask first**
- Example: "The credit limit constraint is blocking this. Would you like me to increase the credit limit to allow it?"

### Rule 5: Read Operations Are Safe, Write Operations Require Care
- GET requests are safe to execute
- PATCH/POST/DELETE require user's explicit instruction for each field being modified

**Why These Rules Matter**: When demonstrating to customers, accidentally modifying their data (even to "help") destroys trust and demonstrates poor AI safety practices.

## Copilot Usage Pattern

### Step 1: Authentication

When user requests database operations, Copilot should first authenticate:

```bash
curl -X POST http://localhost:5656/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"p"}'
```

Response contains JWT token:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "Bearer"
}
```

### Step 2: Execute Operations

Use token for authenticated requests:

#### Read Operations (GET)
```bash
# List customers
curl -X GET http://localhost:5656/api/Customer/ \
  -H "Authorization: Bearer {token}"

# Get specific customer
curl -X GET http://localhost:5656/api/Customer/ALFKI/ \
  -H "Authorization: Bearer {token}"
```

#### Update Operations (PATCH)
```bash
# Update customer credit limit
curl -X PATCH http://localhost:5656/api/Customer/ALFKI/ \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/vnd.api+json" \
  -d '{
    "data": {
      "type": "Customer",
      "id": "ALFKI",
      "attributes": {
        "CreditLimit": 5000
      }
    }
  }'
```

#### Create Operations (POST)
```bash
# Create new customer
curl -X POST http://localhost:5656/api/Customer/ \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/vnd.api+json" \
  -d '{
    "data": {
      "type": "Customer",
      "attributes": {
        "Id": "NEWCO",
        "CompanyName": "New Company Inc",
        "ContactName": "John Doe",
        "CreditLimit": 1000
      }
    }
  }'
```

### Step 3: Handle Constraint Violations

**CRITICAL**: Constraint violations are SUCCESS demonstrations of business logic!

When an update violates business rules, the server returns error code 2001:

```json
{
  "error": {
    "code": 2001,
    "message": "balance (2102.00) exceeds credit (1000.00)"
  }
}
```

**Copilot should report this as**: "✅ Business logic working correctly - constraint prevented invalid update: balance exceeds credit limit"

Common constraint codes:
- **2001** - Business rule violation (the valuable demonstration!)
- **401** - Unauthorized (need to authenticate)
- **404** - Entity not found
- **422** - Validation error

## Natural Language → API Translation Examples

| User Request | Copilot Action | API Call |
|--------------|----------------|----------|
| "List all customers" | GET collection | `GET /api/Customer/` |
| "Show customer ALFKI" | GET single entity | `GET /api/Customer/ALFKI/` |
| "Update ALFKI credit to 5000" | PATCH entity | `PATCH /api/Customer/ALFKI/` with CreditLimit |
| "What's ALFKI's balance?" | GET entity, extract attribute | `GET /api/Customer/ALFKI/` → read Balance |
| "Increase ALFKI credit by 1000" | GET then PATCH | GET current → calculate → PATCH new value |
| "Create customer NEWCO" | POST entity | `POST /api/Customer/` with attributes |

## MCP Discovery Endpoints

The server exposes schema metadata for AI assistants:

### Well-Known Endpoint
```bash
curl http://localhost:5656/.well-known/mcp.json
```

Returns full schema including:
- Available entities (tables)
- Attributes and types
- Relationships
- Business rules documentation

### MCP Endpoint
```bash
curl http://localhost:5656/mcp
```

Same schema as well-known endpoint, alternate path for compatibility.

## Key Implementation Files

- **`api/api_discovery/mcp_discovery.py`** - MCP discovery endpoints
- **`integration/mcp/mcp_client_executor.py`** - Example MCP client script
- **`docs/mcp_learning/mcp_schema.json`** - Schema metadata
- **`logic/declare_logic.py`** - Declarative business rules (LogicBank)
- **`config/default.env`** - Server configuration (SECURITY_ENABLED)

## Testing Workflow for Copilot

When user says: "Can you query the database for me?"

1. **Acknowledge**: "I'll act as MCP client and query the server"
2. **Authenticate**: Login via `/api/auth/login` to get JWT token
3. **Execute**: Make appropriate GET/PATCH/POST call with Bearer token
4. **Present**: Format results or explain constraint violations as logic success
5. **Iterate**: Accept follow-up natural language requests

Example interaction:
```
User: "List customers with balance over 1000"
Copilot: 
  1. Login to get token
  2. GET /api/Customer/?filter[Balance]=>1000
  3. Present: "Found 3 customers: ALFKI (2102.00), ANATR (1500.50), ..."

User: "Try to set ALFKI credit to 500"
Copilot:
  1. PATCH /api/Customer/ALFKI/ with CreditLimit=500
  2. Receive error 2001: "balance (2102.00) exceeds credit (500.00)"
  3. Present: "✅ Business logic prevented this - ALFKI's balance of 2102.00 
     exceeds the proposed credit limit of 500.00. The system is correctly 
     enforcing the constraint that credit must be >= balance."
```

## Business Logic Layer (LogicBank)

The real power is in declarative business rules that auto-execute on all API operations:

```python
# From logic/declare_logic.py

# Constraint: Customer balance cannot exceed credit limit
Rule.constraint(validate=models.Customer,
    as_condition=lambda row: row.Balance <= row.CreditLimit,
    error_msg="balance ({row.Balance}) exceeds credit ({row.CreditLimit})")

# Sum rule: Customer balance = sum of unpaid order amounts
Rule.sum(derive=models.Customer.Balance, 
    as_sum_of=models.Order.AmountTotal,
    where=lambda row: row.ShippedDate is None)

# Formula: Order amount = sum of items
Rule.sum(derive=models.Order.AmountTotal,
    as_sum_of=models.OrderDetail.Amount)
```

These rules:
- Execute automatically on INSERT/UPDATE/DELETE
- Provide **44X code reduction** vs. traditional procedural code
- Enforce multi-table constraints
- Chain automatically (Order → Customer balance)

## Why This Architecture?

**GenAI-Logic's HTTP-based approach** vs **stdio-based MCP servers**:

| Aspect | GenAI-Logic (HTTP) | Stdio MCP |
|--------|-------------------|-----------|
| Transport | HTTP REST API | JSON-RPC over stdin/stdout |
| Authentication | JWT Bearer tokens | Process isolation |
| Scalability | Horizontal scaling | One process per client |
| Network | Works across machines | Same machine only |
| Protocol | JSON:API standard | Custom JSON-RPC |
| Enterprise Ready | ✅ Yes | ⚠️ Limited |

For Microsoft demo: Position GenAI-Logic as the **business logic layer** that any MCP client can invoke, rather than trying to fit into stdio-based protocol constraints.

## Optional: JSON-RPC Wrapper

If standard MCP protocol compatibility is desired, you could add a thin JSON-RPC wrapper:

```python
# Optional enhancement - not required for Copilot usage
@app.route('/mcp/jsonrpc', methods=['POST'])
def mcp_jsonrpc():
    """Translate JSON-RPC 2.0 to internal API calls"""
    request_data = request.json
    method = request_data.get('method')
    params = request_data.get('params', {})
    
    if method == 'customers/list':
        # Translate to GET /api/Customer/
        response = internal_api_call('GET', '/api/Customer/', params)
        return jsonify({'jsonrpc': '2.0', 'result': response, 'id': request_data['id']})
    # ... more method translations
```

**Effort estimate**: Half-day for experienced developer. But this is optional - Copilot can work directly with REST API.

## Demo Strategy

For Microsoft presentation:

1. **Position correctly**: "GenAI-Logic implements MCP Server Executor - the valuable business logic layer"
2. **Show constraint violations**: "Error 2001 is the success - logic is working!"
3. **Demonstrate declarative rules**: "44X code reduction with automatic multi-table chaining"
4. **Use Copilot as client**: "AI assistant translates natural language to authenticated API calls"
5. **Highlight enterprise architecture**: "HTTP-based, JWT auth, horizontally scalable"

The MCP discovery endpoints (`/.well-known/mcp.json` and `/mcp`) allow AI assistants to understand the schema and available operations, but the real innovation is the declarative business logic layer that enforces rules automatically.

## Quick Reference for Copilot

**Authentication**:
```bash
curl -X POST http://localhost:5656/api/auth/login -d '{"username":"admin","password":"p"}'
```

**Common operations**:
- List: `GET /api/{Entity}/` with Bearer token
- Read: `GET /api/{Entity}/{id}/` with Bearer token  
- Update: `PATCH /api/{Entity}/{id}/` with JSON:API payload and Bearer token
- Create: `POST /api/{Entity}/` with JSON:API payload and Bearer token

**Remember**: Constraint violations (code 2001) = business logic success! Report them positively.
