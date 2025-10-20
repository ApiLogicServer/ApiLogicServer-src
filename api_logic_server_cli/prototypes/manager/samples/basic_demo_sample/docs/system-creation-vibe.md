---
title: Vibe MCP / Microservice
do_process_code_block_titles: True
version: 0.23 from docsite 7/11/2025
---
<style>
  .md-typeset h1,
  .md-content__button {
    display: none;
  }
</style>

<< Under Construction >>

# Vibe an MCP Microservice

See the Readme for detailed walk through.

Scenario: we have an existing database (customers, order, items and product), and we require:

* An MCP-enabled API, for integration
* MCP client support to send emails for overdue orders
* Business Logic to check credit by rolling up Items and Orders.

This is a record of how we created the system using CoPilot Chat (*Vibe*).

<br>

## Initialize CoPilot

```
Please find and read `.github/.copilot-instructions.md`.
```

<br>

## Create the System

```bash title="Create a project from an existing database"
# in the GenAI-Logic Manager:
Create a database project from samples/dbs/basic_demo.sqlite
```

<br>

## Verify the API and Admin App

The project should automatically open a new window in VSCode.  Again, open CoPilot and bootstrap it with: <br>

```bash title="Initialize CoPilot"
Please find and read `.github/.copilot-instructions.md`**.
```

Verify it as follows:

* **Click F5** to start server, open app at http://localhost:5656/
* **Verify API:** filtering, sorting, pagination, optimistic locking and related data access - see the Swagger
* **Verify Admin App:** multi-page, multi-table, automatic joins, lookups, cascade add - collaboration-ready

<br>

## Create a Custom React App

```bash title="Create a custom react app"
Create a react app.
```

<br>

```txt title='Customize using Natural Language - Add Cards'
In the ui/react app, update the Product list to provide users an option to see results in a list,
or in cards.
```
<br>

todo - diagram 

**Test: verify option for cards on `http://localhost:3000`**

<br>

## MCP Client - Overdue Orders

**Stop the Server**

<br>

``` bash title="Add a Table to Track Sent Emails"
Create a table SysEmail in `database/db.sqlite` as a child of customer, 
with columns id, message, subject, customer_id and CreatedOn.
```
Follow the suggestions to update the admin app.

<br>

<br>

``` bash title="Create MCP Executor: process request - invokes the LLM to obtain a series of API calls to run, and runs them"
Create the mcp client executor
```

<br>

``` bash title="Create the email service using SysEmail as a Request Table"
Add an after_flush event on SysEmail to produce a log message "email sent",
unless the customer has opted out.
```

<br>

```bash title="Business Logic to Honor Email Opt-out"
Add an after_flush event on SysEmail to produce a log message "email sent",
unless the customer has opted out.
```

<br>

```text title="Test the MCP Client: Click SysMCP >> Create New, and enter"
List the orders date_shipped is null and CreatedOn before 2023-07-14, 
and send a discount email (subject: 'Discount Offer') to the customer for each one.
```

<br>
todo - diagram 

**Use the Admin App to Verify the first customer has an email**

<br>

## Check Credit Business Logic

**1. Stop the Server** (Red Stop button, or Shift-F5 -- see Appendix)

**2. Add Business Logic**

```bash title="Check Credit Logic (instead of 220 lines of code)"
Use case: Check Credit    
    1. The Customer's balance is less than the credit limit
    2. The Customer's balance is the sum of the Order amount_total where date_shipped is null
    3. The Order's amount_total is the sum of the Item amount
    4. The Item amount is the quantity * unit_price
    5. The Item unit_price is copied from the Product unit_price

Use case: App Integration
    1. Send the Order to Kafka topic 'order_shipping' if the date_shipped is not None.
```

To test the logic:

**1. Use the Admin App to access the first order for `Customer Alice`**

**2. Edit its first item to a very high quantity**

todo - diagram 

The update is properly rejected because it exceeds the credit limit.  Observe the rules firing in the console log - see Logic In Action, below.

<br>
