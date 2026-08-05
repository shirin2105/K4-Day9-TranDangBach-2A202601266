import json
from pathlib import Path
from src.data_loader import DataLoader
from src.agents.triage_agent import ClaimTriageAgent
from src.agents.delivery_agent import DeliveryAgent
from src.agents.financial_agent import FinancialAgent
from src.agents.context_agent import ContextAgent
from src.agents.policy_agent import PolicyAgent
from src.agents.critic_agent import CriticAgent
from src.agents.resolution_agent import ResolutionAgent

class SupervisorAgent:
    """Agent 1 & Output Validator: Coordinates entire pipeline flow from Step 1 to Step 6."""

    def __init__(self):
        self.db = DataLoader()
        self.triage_agent = ClaimTriageAgent()
        self.delivery_agent = DeliveryAgent()
        self.financial_agent = FinancialAgent()
        self.context_agent = ContextAgent()
        self.policy_agent = PolicyAgent()
        self.critic_agent = CriticAgent()
        self.resolution_agent = ResolutionAgent()

    def process_case(self, input_filepath: Path) -> dict:
        with open(input_filepath, 'r', encoding='utf-8') as f:
            input_json = json.load(f)

        case_id = input_json.get("case_id")
        cust_req = input_json.get("customer_request", {})
        claimed_order_id = cust_req.get("claimed_order_id")

        # Step 2: Claim Triage Agent
        triage_res = self.triage_agent.analyze(cust_req)

        # Data Retrieval Tool
        order_data = self.db.get_order(claimed_order_id)
        customer_id = order_data.get("customer_id") if order_data else None
        items_data = self.db.get_order_items(claimed_order_id)
        payments_data = self.db.get_order_payments(claimed_order_id)

        # Step 3A: Delivery Agent
        delivery_res = self.delivery_agent.investigate(order_data, items_data)

        # Step 3B: Financial Agent
        financial_res = self.financial_agent.investigate(items_data, payments_data)

        # Step 3C: Context Agent
        context_res = self.context_agent.investigate(claimed_order_id, customer_id, items_data)

        # Step 4: Policy Adjudicator Agent
        policy_res = self.policy_agent.adjudicate(order_data, items_data, payments_data, delivery_res, financial_res, context_res)

        # Step 5: Critic Agent
        critic_res = self.critic_agent.review(claimed_order_id, items_data, payments_data, policy_res)
        if not critic_res["is_valid"]:
            policy_res = self.policy_agent.adjudicate(order_data, items_data, payments_data, delivery_res, financial_res, context_res)

        # Step 6: Resolution Agent
        resolution_res = self.resolution_agent.synthesize(case_id, claimed_order_id, triage_res, delivery_res, financial_res, context_res, policy_res, items_data)

        # Format arrays and limits strictly according to README.md lines 135-218
        item_ids = [f"{claimed_order_id}:{item.get('order_item_id')}" for item in items_data][:5]
        payment_ids = [f"{claimed_order_id}:{pay.get('payment_sequential')}" for pay in payments_data][:5]
        seller_ids = context_res["seller_ids"][:3]
        related_order_ids = context_res["customer_context"]["related_order_ids"][:5]
        product_ids = context_res["product_context"]["product_ids"][:5]
        category_names = context_res["product_context"]["category_names"][:5]
        
        # Hard gate requirement: case_status must be 'action_required' or 'no_action'
        case_status = "action_required" if policy_res["refund_type"] != "none" or policy_res["primary_issue"] in ["canceled_order_paid", "unavailable_order_paid", "late_delivery_seller", "late_delivery_logistics"] else "no_action"

        ranked_causes = [
            {"cause_code": policy_res["root_cause_code"], "rank": 1}
        ] if policy_res["root_cause_code"] else []
        ranked_causes = ranked_causes[:3]

        responsible_parties = policy_res["responsible_parties"][:3]
        evidence_ids = policy_res["evidence_ids"][:20]
        resolution_actions = policy_res["actions"][:5]

        # Exact schema matching README.md lines 135-208
        output_schema = {
            "case_id": case_id,
            "case_assessment": {
                "primary_issue": policy_res["primary_issue"],
                "secondary_issues": policy_res["secondary_issues"],
                "case_status": case_status,
                "confidence": resolution_res["confidence"]
            },
            "affected_entities": {
                "order_ids": [claimed_order_id][:5],
                "item_ids": item_ids,
                "seller_ids": seller_ids,
                "payment_ids": payment_ids
            },
            "customer_context": {
                "customer_unique_id": context_res["customer_context"]["customer_unique_id"],
                "related_order_ids": related_order_ids
            },
            "product_context": {
                "product_ids": product_ids,
                "category_names": category_names
            },
            "delivery_analysis": delivery_res,
            "payment_reconciliation": financial_res,
            "root_cause_analysis": {
                "ranked_causes": ranked_causes,
                "responsible_parties": responsible_parties
            },
            "evidence_ids": evidence_ids,
            "financial_resolution": {
                "currency": "BRL",
                "recommended_refund_brl": policy_res["refund_amount_brl"]
            },
            "resolution_actions": resolution_actions
        }

        return output_schema
