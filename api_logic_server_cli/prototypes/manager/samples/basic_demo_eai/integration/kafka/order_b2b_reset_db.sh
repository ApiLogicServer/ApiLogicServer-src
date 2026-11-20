#!/usr/bin/env bash
# integration/kafka/order_b2b_reset_db.sh — clear the order_b2b blob table (domain Orders are left alone:
# they belong to the Check Credit data).  Run from project root WITH THE SERVER STOPPED:
#     bash integration/kafka/order_b2b_reset_db.sh
set -e
sqlite3 database/db.sqlite "delete from order_b2b_message;"
echo "order_b2b_message cleared."
