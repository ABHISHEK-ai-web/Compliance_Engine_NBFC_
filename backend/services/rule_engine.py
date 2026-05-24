from dataclasses import dataclass
from typing import Callable


@dataclass
class ComplianceRule:
    rule_id: str
    name: str
    description: str
    regulation_reference: str
    severity: str
    affected_department: str
    condition: Callable[[str], bool]
    recommendation: str


class RuleEngine:
    def __init__(self):
        self.rules = self._initialize_rules()

    def _initialize_rules(self) -> list[ComplianceRule]:
        """Define deterministic compliance rules for RBI Digital Lending Guidelines."""
        return [
            ComplianceRule(
                rule_id="DL-001",
                name="Key Fact Statement (KFS) Disclosure",
                description="Lender must provide KFS to borrower before loan execution",
                regulation_reference="RBI/2022-23/DL Guidelines, Section 3.2",
                severity="HIGH",
                affected_department="Lending Operations",
                condition=lambda text: not any(
                    term in text.lower()
                    for term in ["key fact statement", "kfs", "key facts"]
                ),
                recommendation="Implement mandatory KFS disclosure step with borrower acknowledgment before loan disbursement.",
            ),
            ComplianceRule(
                rule_id="DL-002",
                name="Cooling-Off Period",
                description="Borrower must be given a cooling-off/look-up period to exit without penalty",
                regulation_reference="RBI/2022-23/DL Guidelines, Section 4.1",
                severity="HIGH",
                affected_department="Lending Operations",
                condition=lambda text: not any(
                    term in text.lower()
                    for term in ["cooling off", "cooling-off", "look-up period", "exit without penalty"]
                ),
                recommendation="Add cooling-off period clause (minimum 3 days) allowing borrower exit without penalty.",
            ),
            ComplianceRule(
                rule_id="DL-003",
                name="Grievance Redressal Mechanism",
                description="Must have a documented grievance redressal mechanism with escalation matrix",
                regulation_reference="RBI/2022-23/DL Guidelines, Section 6",
                severity="CRITICAL",
                affected_department="Customer Service",
                condition=lambda text: not any(
                    term in text.lower()
                    for term in ["grievance", "redressal", "complaint mechanism", "escalation matrix"]
                ),
                recommendation="Establish grievance redressal mechanism with defined TAT and escalation to RBI Ombudsman.",
            ),
            ComplianceRule(
                rule_id="DL-004",
                name="Data Privacy and Storage",
                description="Borrower data must not be stored beyond purpose; need-to-know access only",
                regulation_reference="RBI/2022-23/DL Guidelines, Section 5.3",
                severity="CRITICAL",
                affected_department="IT/Data Governance",
                condition=lambda text: not any(
                    term in text.lower()
                    for term in ["data retention", "data deletion", "need-to-know", "data minimization", "purpose limitation"]
                ),
                recommendation="Implement data retention policy with automatic deletion post purpose completion and access controls.",
            ),
            ComplianceRule(
                rule_id="DL-005",
                name="Transparent Pricing Disclosure",
                description="All-inclusive annual percentage rate (APR) must be disclosed",
                regulation_reference="RBI/2022-23/DL Guidelines, Section 3.4",
                severity="HIGH",
                affected_department="Product/Pricing",
                condition=lambda text: not any(
                    term in text.lower()
                    for term in ["annual percentage rate", "apr", "all-inclusive cost", "total cost of borrowing"]
                ),
                recommendation="Display APR prominently including all fees, charges, and interest in standardized format.",
            ),
            ComplianceRule(
                rule_id="DL-006",
                name="Third-Party LSP Oversight",
                description="Regulated entity remains responsible for LSP actions; must have oversight mechanism",
                regulation_reference="RBI/2022-23/DL Guidelines, Section 2.2",
                severity="HIGH",
                affected_department="Vendor Management",
                condition=lambda text: not any(
                    term in text.lower()
                    for term in ["lsp oversight", "service provider", "lsp monitoring", "outsourcing", "third party oversight"]
                ),
                recommendation="Implement LSP monitoring framework with periodic audits and customer complaint tracking.",
            ),
            ComplianceRule(
                rule_id="DL-007",
                name="Disbursement to Borrower Account",
                description="Loan must be disbursed directly to borrower's bank account",
                regulation_reference="RBI/2022-23/DL Guidelines, Section 4.3",
                severity="MEDIUM",
                affected_department="Operations",
                condition=lambda text: not any(
                    term in text.lower()
                    for term in ["direct disbursement", "borrower account", "borrower's bank account", "direct credit"]
                ),
                recommendation="Ensure loan amount is credited directly to borrower's verified bank account only.",
            ),
            ComplianceRule(
                rule_id="DL-008",
                name="Automatic Repayment Consent",
                description="Auto-debit/repayment setup must have explicit borrower consent",
                regulation_reference="RBI/2022-23/DL Guidelines, Section 4.5",
                severity="MEDIUM",
                affected_department="Collections",
                condition=lambda text: not any(
                    term in text.lower()
                    for term in ["explicit consent", "auto-debit consent", "repayment consent", "e-mandate", "nach consent"]
                ),
                recommendation="Implement explicit consent mechanism for auto-debit setup with revocation option.",
            ),
            ComplianceRule(
                rule_id="KYC-001",
                name="Video-KYC Compliance",
                description="V-CIP process must follow RBI KYC guidelines for digital onboarding",
                regulation_reference="RBI/KYC Directions 2016, Amendment 2020",
                severity="HIGH",
                affected_department="Onboarding/KYC",
                condition=lambda text: not any(
                    term in text.lower()
                    for term in ["video kyc", "v-cip", "video verification", "video-based identification"]
                ),
                recommendation="Implement V-CIP process adhering to RBI KYC Directions with proper audit trail.",
            ),
            ComplianceRule(
                rule_id="FAIR-001",
                name="Fair Practices Code",
                description="Fair practices code must be documented and accessible to borrowers",
                regulation_reference="RBI Fair Practices Code, 2003 (Updated)",
                severity="MEDIUM",
                affected_department="Compliance",
                condition=lambda text: not any(
                    term in text.lower()
                    for term in ["fair practices", "fair practice code", "fpc", "code of conduct"]
                ),
                recommendation="Publish Fair Practices Code on website and provide copy to all borrowers at onboarding.",
            ),
        ]

    def evaluate(self, policy_text: str) -> list[dict]:
        """Evaluate policy text against all compliance rules."""
        findings = []
        for rule in self.rules:
            if rule.condition(policy_text):
                findings.append({
                    "rule_id": rule.rule_id,
                    "violation_detected": f"{rule.name} - {rule.description}",
                    "affected_department": rule.affected_department,
                    "severity": rule.severity,
                    "regulation_reference": rule.regulation_reference,
                    "missing_requirement": rule.description,
                    "explanation": f"The policy document does not contain provisions for: {rule.name}. "
                                   f"This is required under {rule.regulation_reference}.",
                    "recommendation": rule.recommendation,
                    "source": "rule_engine",
                })
        return findings

    def get_applicable_rules(self) -> list[dict]:
        """Return all configured rules for display."""
        return [
            {
                "rule_id": r.rule_id,
                "name": r.name,
                "description": r.description,
                "regulation_reference": r.regulation_reference,
                "severity": r.severity,
                "affected_department": r.affected_department,
            }
            for r in self.rules
        ]
