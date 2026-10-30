"""
Feature: Credit Limit Maintenance

* **Copy from group**: an action on a Customer replaces its credit-limit rows with copies of its Customer Group's rows (company, `credit_limit`, flag).
"""
from flask import request, jsonify
import logging
import safrs
from database import models

app_logger = logging.getLogger("api_logic_server_app")


def add_service(app, api, project_dir, swagger_host: str, PORT: str, method_decorators=[]):

    def copy_credit_limits_from_group():
        """API service CopyCreditLimitsFromGroup: replaces a Customer's credit-limit rows with copies of its Customer Group's
        rows (company, credit_limit, flag); the deletes and inserts go through the rules (uniqueness, limit >= outstanding).

        POST /copy_credit_limits_from_group   {"customer_id": 1}
        """
        session = safrs.DB.session
        payload = request.get_json(silent=True) or {}
        customer_id = payload.get("customer_id") or request.args.get("customer_id")
        customer = session.get(models.Customer, int(customer_id)) if customer_id is not None else None
        if customer is None:
            return jsonify({"error": f"customer {customer_id} not found"}), 404
        try:
            for each_row in list(customer.CustomerCreditLimitList):
                session.delete(each_row)
            session.flush()                       # deletes first: the new rows reuse the same (customer, company) keys
            group_rows = session.query(models.CustomerGroupCreditLimit).filter_by(customer_group_id=customer.customer_group_id).all()
            for each_group_row in group_rows:
                session.add(models.CustomerCreditLimit(customer_id=customer.id,
                                                       company_id=each_group_row.company_id,
                                                       credit_limit=each_group_row.credit_limit,
                                                       bypass_credit_limit_check=each_group_row.bypass_credit_limit_check))
            session.commit()
        except Exception as e:
            session.rollback()
            app_logger.info(f"copy_credit_limits_from_group rejected: {e}")
            return jsonify({"error": str(e)}), 400
        return jsonify({"customer_id": customer.id, "rows_copied": len(group_rows)})

    service = copy_credit_limits_from_group
    from flask_jwt_extended import jwt_required
    from config.config import Config
    import os
    security_enabled = str(os.getenv("SECURITY_ENABLED", getattr(Config, "SECURITY_ENABLED", False))).lower() not in ["false", "no", "0"]
    if security_enabled:
        service = jwt_required()(service)
    app.add_url_rule('/copy_credit_limits_from_group', 'copy_credit_limits_from_group', service, methods=['POST'])
