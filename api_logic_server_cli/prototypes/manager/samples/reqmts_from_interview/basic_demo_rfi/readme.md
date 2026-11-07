---
title: Sample_Basic_Demo_RFI
do_process_code_block_titles: True
version: 1.00
source: docs/Sample-Basic-Demo-RFI
Propagation: see api_logic_server_cli/sample_mgr/create_readme.py
---
<style>
  -typeset h1,
  -content__button {
    display: none;
  }
</style>


&nbsp;
**Key Takeways - TL;DR - RFI: Requirements From Interview**
&nbsp;

    This illustrates you can supply incomplete requirements, and
    request that AI *interview* you to complete them and create a system.

    Here we create the basic demo for Customer and Orders,
    and request an interview for encouraging sales of *"green"* products.

&nbsp;

## Overview

This app illustrates *requirements from interview* (RFI). The prompt specifies the basic demo (Customers, Orders, Check Credit) in full, and asks AI to interview you only about one clause: encouraging sales of *"green"* products with a discount. AI interviews you on that clause, confirms its understanding, then builds the system.

&nbsp;

![running](https://raw.githubusercontent.com/ApiLogicServer/Docs/main/docs/images/exec_reqmts/rfi_with_int_bd.png)

Observe the hilit area: data model and logic changes for "green" products.

&nbsp;

## Creation and Setup

We created this system (api, logic, admin app) as follows:

![create_script](https://raw.githubusercontent.com/ApiLogicServer/Docs/main/docs/images/exec_reqmts/rfi_with_int_bd_rfi.png)
