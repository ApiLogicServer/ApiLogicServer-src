from behave import *
import requests
import test_utils
import json
import datetime

# All WHEN steps are defined in check_credit.py
# This file only needs THEN steps specific to app_integration if any

# The app_integration.feature scenarios reuse steps from check_credit.py:
# - @when('Order date_shipped set to today') - already in check_credit.py
# - @when('Order date_shipped set to None') - already in check_credit.py
# - @then('Kafka message sent to order_shipping topic') - already in check_credit.py
# - @then('No Kafka message sent') - already in check_credit.py

# No additional steps needed - all are shared!
