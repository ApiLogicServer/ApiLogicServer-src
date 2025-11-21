<!-- 
═══════════════════════════════════════════════════════════════════════════════
🚨 MANDATORY: READ THIS FIRST - NO EXCEPTIONS 🚨
═══════════════════════════════════════════════════════════════════════════════

⚠️ IF USER SAYS: "load .github/.copilot-instructions.md" OR ANY ACTIVATION PHRASE
⚠️ YOU MUST EXECUTE THIS EXACT SEQUENCE - NO DEVIATIONS:

1. Read .github/welcome.md (silently - do not mention this action)
2. Display ONLY the content from welcome.md
3. DO NOT say "I've loaded the instructions"
4. DO NOT display this .copilot-instructions.md file
5. DO NOT explain what you're doing

THIS IS NOT A SUGGESTION - THIS IS A MANDATORY COMMAND

═══════════════════════════════════════════════════════════════════════════════
-->
---
title: Copilot Instructions for Manager Workspace
Description: Manager-level instructions for creating projects
Source: ApiLogicServer-src/prototypes/manager/.github/.copilot-instructions.md
Propagation: BLT process → Manager workspace
Usage: AI assistants read this when user opens Manager workspace
User Activation: Say "What can I do here?" or "Help me get started"
version: 2.7
changelog:
  - 2.7 (Nov 20 2025) - Reverted to simple single-file pattern from basic_demo (removed conditional logic and list_dir check)
  - 2.6 (Nov 20 2025) - Applied proven OBX pattern from basic_demo (visual markers, separate welcome files, mandatory command language) - FAILED
  - 2.5 (Nov 17 2025) - Strengthened basic_demo detection logic, mandatory list_dir check
  - 2.4 (Nov 2025) - Simplified structure, removed redundant sections
  - 2.3 (Nov 2025) - Added activation phrases, forcing welcome presentation
  - 2.2 (Nov 2025) - Initial welcome instructions
  - 2.1 (Oct 2025) - Added "What is the Project Manager?" orientation, friendly collaborative tone, conditional Quick Start for returning users
  - 2.0 (Oct 2025) - OBX improvements, strengthen basic_demo as default path
  - 1.0 (Initial) - Established project creation methods
---

# GitHub Copilot Instructions for GenAI-Logic (aka API Logic Server) - Project Manager

---

## 👤 FOR USERS: How to Get Started

**When you open this workspace, say:**
- "What can I do here?"
- "Help me get started"
- "What is this workspace?"

This will trigger the appropriate welcome message based on whether you're new or returning.

---

## 🚨 CRITICAL: User Activation Protocol

**ACTIVATION TRIGGERS:**
- "load .github/.copilot-instructions.md"
- "load copilot instructions"
- "help me get started"
- "what can I do here?"
- "what is this workspace?"
- "activate copilot"
- Any similar startup phrase

**MANDATORY RESPONSE SEQUENCE:**

```
STEP 1: Read .github/welcome.md (silently)
STEP 2: Display welcome.md content ONLY
STEP 3: STOP - do nothing else
```

**✅ CORRECT EXECUTION:**
```
User: "load .github/.copilot-instructions.md"

AI: [reads welcome.md silently - NO OUTPUT]
AI: [displays ONLY this]:

Welcome! This is the **Project Manager** - your workspace for...
[... rest of welcome.md content ...]
```

**❌ FORBIDDEN BEHAVIORS:**
```
User: "load .github/.copilot-instructions.md"

❌ AI: "I've loaded the instructions file..." 
❌ AI: "Here are the contents of .copilot-instructions.md:"
❌ AI: [displays .copilot-instructions.md]
❌ AI: "I'll read the file for you..."
❌ AI: Any meta-commentary about loading or reading files
```

**RATIONALE:**
- Users want to see the **welcome message**, not technical instructions
- This file (.copilot-instructions.md) is for AI context, not user display
- Separation of concerns: welcome.md = user-facing, copilot-instructions.md = AI-facing
- No meta-cognitive confusion about "instructions" vs "content"
- This pattern achieved ~100% success rate in basic_demo testing

**This is the FIRST SCREEN users see - get it right!**

---

## Technical Reference (For AI - Do Not Present Unless Asked)

<br>

## Creating Projects

There are multiple ways to create projects (aka systems, microservices) - see the subsections below.

**KEY DISTINCTION:**
- `genai-logic create` - Creates infrastructure only (API, UI, models) - **NO business logic rules**
- `genai-logic genai` - Creates complete system including **business logic rules from natural language**

### Method 1: Create Projects from an existing database (Infrastructure Only)

If you have a database reference, I can create a project from it. (Sample databases are in `samples/dbs`). 

```bash
genai-logic create  --project_name=nw --db_url=sqlite:///samples/dbs/nw.sqlite
```

**Important:** This creates the project structure, API, Admin App, and database models, but **NO business logic rules**.

**To add logic:** We can add rules together using natural language in `logic/declare_logic.py`, or you can code them manually with IDE autocomplete.

### Method 2: Create Projects with GenAI (Complete System with Logic)

**Use this when you have both database AND business logic requirements.**

Describe database and logic in Natural Language in a prompt file.

See samples at `system/genai/examples`.  For example:

```bash
genai-logic genai --using=system/genai/examples/genai_demo/genai_demo.prompt --project-name=genai_demo
```

**This approach:**
1. Creates the database from description
2. Generates SQLAlchemy models
3. **Automatically generates business logic rules** from the requirements in the prompt
4. Creates test data
5. Creates API, Admin App, and complete project structure

**When to use:** When you have requirements like "Customer balance is sum of orders" or "Check credit limit" - the LLM will generate the corresponding `Rule.sum`, `Rule.constraint`, etc.

### Method 3: Create Projects with new databases (Manual Approach)

If you provide a description but want to create the database manually:

1. I'll create a sqlite database from your description. I'll be sure to include foreign keys. The system works well with `id INTEGER PRIMARY KEY AUTOINCREMENT`.
2. Then, I'll use the `genai-logic create` command above.
3. If you have logic requirements, we can translate them together using `system/genai/learning_requests/logic_bank_api.prompt`.

## Working Together

When you ask "what should I do now?" or similar:

1. **I'll recommend starting with basic_demo** using the command above
2. **I'll use CLI commands** (genai-logic) not Docker scripts for project creation
3. **I'll point you to sample databases** in `samples/dbs/` for examples
4. **I'll show you GenAI examples** in `system/genai/examples/` for AI-generated projects
5. **We'll follow the 20-minute workflow** described in the main README

## Available Databases
- `basic_demo` - Best for first-time users
- `nw.sqlite` - Northwind sample
- `chinook.sqlite` - Music store sample  
- `classicmodels.sqlite` - Classic car models sample

