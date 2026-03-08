"""
CBSA Steel Derivative Goods Surtax — Custom API Endpoint
PC Number: 2025-0917 | Program Code: 25267A

Endpoint: GET /api/cbsa/surtax-summary/<entry_id>
Returns a formatted duty/tax breakdown for a given customs entry.

Auto-discovered via api/api_discovery/auto_discovery.py
"""
import logging
from flask import jsonify, request
from safrs import jsonapi_rpc
from database.models import CustomsEntry, SurtaxLineItem, HsCodeRate, CountryOrigin, Province
import safrs

app_logger = logging.getLogger(__name__)


def add_service(app, api, project_dir, swagger_host: str, PORT: str, method_decorators=None):
    """Register CBSA surtax custom endpoints"""

    @app.route("/api/cbsa/surtax-summary/<int:entry_id>", methods=["GET"])
    def cbsa_surtax_summary(entry_id: int):
        """
        GET /api/cbsa/surtax-summary/<entry_id>

        Returns a detailed duty and tax breakdown for a customs entry.
        Includes per-line and entry-level totals with surtax applicability.
        """
        session = safrs.DB.session
        entry = session.query(CustomsEntry).filter_by(id=entry_id).first()
        if not entry:
            return jsonify({"error": f"CustomsEntry {entry_id} not found"}), 404

        province = session.query(Province).filter_by(id=entry.province_id).first()

        line_items = []
        for item in entry.SurtaxLineItemList:
            hs = session.query(HsCodeRate).filter_by(id=item.hs_code_id).first()
            country = session.query(CountryOrigin).filter_by(id=item.country_origin_id).first()
            line_items.append({
                "id": item.id,
                "description": item.description,
                "hs_code": hs.hs_code if hs else None,
                "hs_description": hs.description if hs else None,
                "country_of_origin": country.country_name if country else None,
                "country_code": country.country_code if country else None,
                "quantity": item.quantity,
                "customs_value_cad": float(item.customs_value or 0),
                "base_duty_rate_pct": round(float(item.base_duty_rate or 0) * 100, 4),
                "surtax_rate_pct": round(float(item.surtax_rate or 0) * 100, 4),
                "surtax_applicable": bool(item.surtax_applicable),
                "base_duty_amount_cad": float(item.base_duty_amount or 0),
                "surtax_amount_cad": float(item.surtax_amount or 0),
                "duty_paid_value_cad": float(item.duty_paid_value or 0),
                "provincial_tax_amount_cad": float(item.provincial_tax_amount or 0),
                "line_total_cad": float(item.line_total or 0),
            })

        result = {
            "cbsa_programme": {
                "order":        "Steel Derivative Goods Surtax Order",
                "pc_number":    entry.sys_config.order_reference if entry.sys_config else "PC 2025-0917",
                "program_code": entry.sys_config.program_code if entry.sys_config else "25267A",
                "effective_date": entry.surtax_effective_date,
            },
            "entry": {
                "id":            entry.id,
                "entry_number":  entry.entry_number,
                "importer_name": entry.importer_name,
                "ship_date":     entry.ship_date,
                "province":      province.province_name if province else None,
                "province_code": province.province_code if province else None,
                "province_tax_rate_pct": round(float(entry.province_tax_rate or 0) * 100, 4),
                "surtax_active": bool(entry.surtax_active),
                "notes":         entry.notes,
            },
            "line_items": line_items,
            "totals": {
                "total_customs_value_cad":  float(entry.total_customs_value or 0),
                "total_base_duty_cad":      float(entry.total_base_duty or 0),
                "total_surtax_cad":         float(entry.total_surtax or 0),
                "total_provincial_tax_cad": float(entry.total_provincial_tax or 0),
                "grand_total_duties_cad":   float(entry.grand_total_duties or 0),
            },
        }
        return jsonify(result)

    @app.route("/api/cbsa/surtax-entries", methods=["GET"])
    def cbsa_surtax_entries():
        """
        GET /api/cbsa/surtax-entries?province=ON&country=US

        List all customs entries with optional filtering by province_code or country_code.
        Returns summary rows suitable for a dashboard or report.
        """
        session = safrs.DB.session
        province_filter = request.args.get("province")
        country_filter  = request.args.get("country")

        query = session.query(CustomsEntry)

        if province_filter:
            prov = session.query(Province).filter_by(province_code=province_filter.upper()).first()
            if prov:
                query = query.filter(CustomsEntry.province_id == prov.id)

        entries = query.order_by(CustomsEntry.ship_date.desc()).all()

        rows = []
        for entry in entries:
            # Optional filter by country through line items
            if country_filter:
                countries = session.query(CountryOrigin).filter_by(
                    country_code=country_filter.upper()
                ).first()
                if countries:
                    has_country = any(
                        item.country_origin_id == countries.id
                        for item in entry.SurtaxLineItemList
                    )
                    if not has_country:
                        continue

            province = session.query(Province).filter_by(id=entry.province_id).first()
            rows.append({
                "id":            entry.id,
                "entry_number":  entry.entry_number,
                "importer_name": entry.importer_name,
                "ship_date":     entry.ship_date,
                "province":      province.province_code if province else None,
                "surtax_active": bool(entry.surtax_active),
                "line_count":    len(entry.SurtaxLineItemList),
                "total_customs_value_cad":  float(entry.total_customs_value or 0),
                "total_surtax_cad":         float(entry.total_surtax or 0),
                "grand_total_duties_cad":   float(entry.grand_total_duties or 0),
            })

        return jsonify({"entries": rows, "count": len(rows)})
