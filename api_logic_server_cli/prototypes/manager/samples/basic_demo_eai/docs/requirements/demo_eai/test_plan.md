# Test plan: demo_eai

One row per rule (and per rule-less requirement), with the scenarios the coverage matrix in `docs/training/testing.md`
requires. Each scenario creates fresh data (timestamped names). Product prices verified with sqlite3: Widget 90, Gadget 150.
Daily totals are checked as changes to today's `/order_flow/daily` figures, so the seeded history does not matter.

| Rule / requirement | Requirement | Scenarios | Covered by |
|---|---|---|---|
| Customer.balance <= credit_limit (constraint) | Check Credit | accepted; accepted at boundary; rejected | Good Order Placed; Order At Credit Limit Accepted; Order Exceeding Credit Rejected |
| Customer.balance = sum(Order.amount_total where date_shipped is None) | Check Credit | create; change; delete; move to another customer; leaves where (ship); enters where (unship) | Good Order Placed; Item Quantity Changed; Order Deleted Leaves Balance; Order Moved To Another Customer; Shipped Order Leaves Balance; Unshipped Order Enters Balance |
| Order.amount_total = sum(Item.amount) | Check Credit | create; change; delete; move to another order | Good Order Placed; Item Quantity Changed; Item Deleted Reduces Order; Item Moved To Another Order |
| Item.amount = quantity * unit_price | Check Credit | change quantity; change unit_price | Item Quantity Changed; Item Product Changed |
| Item.unit_price = copy of Product.unit_price | Check Credit | create; change product_id | Good Order Placed; Item Product Changed |
| OrderB2B custom API + request log | B2B Order Integration | accepted (request recorded, processed); unknown account rejected; rejected request recorded with its error | Partner Order Accepted; Unknown Account Rejected; Accepted Request Is Recorded; Rejected Request Is Recorded |
| OrderB2bMessage bridge (order_b2b) | Kafka Subscribe Order Integration | message creates the order; unknown account rejected; rejected message keeps its error (live only) | Order Message Delivered; Unknown Account Message Rejected; Rejected Message Keeps Its Error (live Kafka only) |
| Order publish (order_shipping) | Kafka Publish Shipping Notification | fires when shipped; not when unshipped | Shipping Notification Published; Unshipped Order Not Published |
| Customer grants for role sales | Row-Level Security | sales sees only credit_limit >= 3000 or balance > 0 | Sales Role Sees Limited Customers |
| Stamping: CreatedOn if empty, CreatedOnDay | Order Flow Dashboard | placed without a date: today; placed with a date: keeps it | Order Placed Is Dated Today; Order With Its Own Date Keeps It |
| DailyFlow.order_count / order_amount (count, sum, insert_parent) | Order Flow Dashboard | create; change value; delete; move to another day | New Order Counts In Daily Totals; Changed Item Adjusts Daily Amount; Deleted Order Leaves Daily Totals; Order Moved To Another Day |
| DailyFlow.message_* (counts with where, stuck formula) | Order Flow Dashboard | received + processed (enters where); failed (live only); stuck stays 0 | Delivered Message Counts In Daily Totals; Rejected Message Counts In Daily Totals (live Kafka only) |
| DailyFlow.request_* (counts with where, stuck formula) | Order Flow Dashboard | accepted: received + processed; rejected: received + failed | Accepted Request Is Recorded; Rejected Request Is Recorded |
| Dashboard (reads DailyFlow, no cache) | Order Flow Dashboard | serves the three charts with current data | Dashboard Shows Current Data |

- NOT covered: 0 rows. Two scenarios are live-only (skipped, as not verified, when no broker answers). Moving a row to a day with no DailyFlow row is not tested: it fails in LogicBank 1.34.04 (see ad-libs).
