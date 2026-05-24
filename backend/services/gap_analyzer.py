import uuid
from datetime import datetime, timedelta
from services.rag_engine import RAGEngine
from services.slm_engine import SLMEngine
from services.rule_engine import RuleEngine
from services.vector_store import VectorStore
from models.schemas import (
    Violation, Severity, AnalysisResponse, DashboardMetrics, AuditResponse
)


class GapAnalyzer:
    _violations_store: list[dict] = []

    def __init__(self):
        self.rag_engine = RAGEngine()
        self.slm_engine = SLMEngine()
        self.rule_engine = RuleEngine()
        self.vector_store = VectorStore()

    def analyze(
        self,
        regulation_id: str | None = None,
        policy_id: str | None = None,
        query: str | None = None,
    ) -> AnalysisResponse:
        """Run full compliance gap analysis combining RAG + SLM + Rule Engine."""
        analysis_id = str(uuid.uuid4())

        search_query = query or "digital lending compliance requirements KYC grievance redressal"
        regulation_chunks, policy_chunks = self.rag_engine.retrieve_for_analysis(search_query)

        all_violations = []

        # Rule-based analysis on policy text
        if policy_chunks:
            combined_policy_text = " ".join([c["text"] for c in policy_chunks])
            rule_findings = self.rule_engine.evaluate(combined_policy_text)
            all_violations.extend(rule_findings)

        # AI-based analysis via SLM (optional; rule engine works without it)
        if self.slm_engine.enabled and regulation_chunks and policy_chunks:
            prompt = self.rag_engine.build_compliance_prompt(regulation_chunks, policy_chunks)
            ai_findings = self.slm_engine.analyze_compliance(prompt)

            if "violations" in ai_findings:
                for v in ai_findings["violations"]:
                    v["source"] = "ai_engine"
                    all_violations.append(v)

        # Deduplicate and assign IDs
        violations = self._deduplicate_violations(all_violations)
        violation_objects = []
        for i, v in enumerate(violations):
            violation = Violation(
                violation_id=f"V-{analysis_id[:8]}-{i+1:03d}",
                violation_detected=v.get("violation_detected", "Unknown violation"),
                affected_department=v.get("affected_department", "General"),
                severity=self._normalize_severity(v.get("severity", "MEDIUM")),
                regulation_reference=v.get("regulation_reference", "N/A"),
                missing_requirement=v.get("missing_requirement", "Not specified"),
                explanation=v.get("explanation", "No explanation available"),
                recommendation=v.get("recommendation", "Manual review required"),
                confidence_score=v.get("confidence_score", 0.75),
                detected_at=datetime.now(),
            )
            violation_objects.append(violation)

        GapAnalyzer._violations_store.extend(
            [v.model_dump(mode="json") for v in violation_objects]
        )

        compliance_score = self._calculate_compliance_score(violation_objects)
        critical_count = sum(1 for v in violation_objects if v.severity == Severity.CRITICAL)
        high_count = sum(1 for v in violation_objects if v.severity == Severity.HIGH)
        medium_count = sum(1 for v in violation_objects if v.severity == Severity.MEDIUM)
        low_count = sum(1 for v in violation_objects if v.severity == Severity.LOW)
        total_rules = len(self.rule_engine.rules)
        failed_rules = len({v.get("rule_id") for v in violations if v.get("rule_id")})
        rules_passed = max(0, total_rules - failed_rules)

        return AnalysisResponse(
            analysis_id=analysis_id,
            violations=violation_objects,
            compliance_score=compliance_score,
            summary=f"Analysis complete. Found {len(violation_objects)} compliance gaps. "
                    f"Critical: {critical_count}, High: {high_count}, Medium: {medium_count}, Low: {low_count}. "
                    f"Regulatory checks passed: {rules_passed}/{total_rules}.",
            total_violations=len(violation_objects),
            critical_count=critical_count,
            high_count=high_count,
            medium_count=medium_count,
            low_count=low_count,
            regulatory_checks_passed=rules_passed,
            regulatory_checks_total=total_rules,
        )

    def query_knowledge_base(self, question: str) -> AuditResponse:
        """Answer compliance questions using RAG."""
        reg_chunks = self.rag_engine.retrieve_relevant_regulations(question)
        policy_chunks = self.rag_engine.retrieve_relevant_policies(question)
        all_chunks = reg_chunks + policy_chunks

        if not all_chunks:
            return AuditResponse(
                answer="No relevant documents found in the knowledge base. Please upload regulatory circulars and policy documents first.",
                sources=[],
                confidence=0.0,
            )

        sources = [
            {
                "filename": c["metadata"].get("filename", "Unknown"),
                "page": c["metadata"].get("page_number", 0),
                "relevance": round(c.get("relevance_score", 0), 3),
                "snippet": c["text"][:200],
            }
            for c in all_chunks[:5]
        ]

        avg_relevance = sum(c.get("relevance_score", 0) for c in all_chunks[:5]) / max(
            len(all_chunks[:5]), 1
        )

        if self.slm_engine.enabled:
            prompt = self.rag_engine.build_audit_query_prompt(question, all_chunks)
            answer = self.slm_engine.answer_query(prompt)
        else:
            snippets = "\n\n".join(
                f"[{c['metadata'].get('filename', 'Unknown')}, p.{c['metadata'].get('page_number', '?')}]\n{c['text'][:400]}"
                for c in all_chunks[:3]
            )
            answer = (
                f"Relevant excerpts for: {question}\n\n{snippets}\n\n"
                "(Enable USE_SLM=true for AI-generated answers.)"
            )

        return AuditResponse(
            answer=answer,
            sources=sources,
            confidence=round(avg_relevance, 3),
        )

    def get_violations(
        self,
        severity: Severity | None = None,
        department: str | None = None,
        limit: int = 50,
    ) -> list[Violation]:
        """Retrieve stored violations with optional filtering."""
        violations = [
            self._normalize_stored_violation(v) for v in GapAnalyzer._violations_store
        ]

        if severity:
            violations = [v for v in violations if v["severity"] == severity.value]
        if department:
            violations = [v for v in violations if department.lower() in v["affected_department"].lower()]

        violations = violations[:limit]
        return [Violation(**v) for v in violations]

    def _normalize_stored_violation(self, v: dict) -> dict:
        """Ensure stored violations are JSON-serializable (handles legacy datetime objects)."""
        out = dict(v)
        detected = out.get("detected_at")
        if isinstance(detected, datetime):
            out["detected_at"] = detected.isoformat()
        severity = out.get("severity")
        if hasattr(severity, "value"):
            out["severity"] = severity.value
        return out

    def get_dashboard_metrics(self) -> DashboardMetrics:
        """Calculate dashboard metrics from stored data."""
        violations = [
            self._normalize_stored_violation(v) for v in GapAnalyzer._violations_store
        ]
        reg_count = self.vector_store.get_collection_count("regulations")
        policy_count = self.vector_store.get_collection_count("policies")

        risk_distribution = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
        department_risks: dict[str, list[float]] = {}

        for v in violations:
            sev = v.get("severity", "MEDIUM")
            risk_distribution[sev] = risk_distribution.get(sev, 0) + 1

            dept = v.get("affected_department", "General")
            if dept not in department_risks:
                department_risks[dept] = []
            severity_score = {"CRITICAL": 1.0, "HIGH": 0.75, "MEDIUM": 0.5, "LOW": 0.25}
            department_risks[dept].append(severity_score.get(sev, 0.5))

        dept_avg_risks = {
            dept: round(sum(scores) / len(scores) * 100, 1)
            for dept, scores in department_risks.items()
        } if department_risks else {"No Data": 0}

        total_violations = len(violations)
        total_rules = len(self.rule_engine.rules)
        failed_rule_ids = {v["rule_id"] for v in violations if v.get("rule_id")}
        rules_passed = max(0, total_rules - len(failed_rule_ids))
        compliance_score = self._score_from_violation_dicts(violations)

        # Generate trend data
        violation_trends = self._generate_trend_data(violations)

        recent = violations[-10:] if violations else []
        recent_violations = [Violation(**v) for v in recent]

        return DashboardMetrics(
            overall_compliance_score=round(compliance_score, 1),
            total_documents=reg_count + policy_count,
            total_regulations=reg_count,
            total_policies=policy_count,
            total_violations=total_violations,
            regulatory_checks_passed=rules_passed,
            regulatory_checks_total=total_rules,
            risk_distribution=risk_distribution,
            department_risks=dept_avg_risks,
            recent_violations=recent_violations,
            violation_trends=violation_trends,
        )

    def _score_from_violation_dicts(self, violations: list[dict]) -> float:
        """
        Compliance score = % of RBI rule checks passed (10 rules in engine).
        AI-only findings (no rule_id) apply a small extra penalty (max 15 points).
        """
        total_rules = len(self.rule_engine.rules)
        if not violations:
            return 100.0

        failed_rule_ids = {v["rule_id"] for v in violations if v.get("rule_id")}
        rules_passed = max(0, total_rules - len(failed_rule_ids))
        base_score = 100.0 * rules_passed / total_rules

        ai_extras = sum(1 for v in violations if not v.get("rule_id"))
        extra_penalty = min(15.0, ai_extras * 5.0)

        return max(0.0, round(base_score - extra_penalty, 1))

    def _calculate_compliance_score(self, violations: list[Violation]) -> float:
        if not violations:
            return 100.0
        dicts = [v.model_dump(mode="json") for v in violations]
        return self._score_from_violation_dicts(dicts)

    def _normalize_severity(self, severity: str) -> Severity:
        mapping = {
            "CRITICAL": Severity.CRITICAL,
            "HIGH": Severity.HIGH,
            "MEDIUM": Severity.MEDIUM,
            "LOW": Severity.LOW,
        }
        return mapping.get(severity.upper(), Severity.MEDIUM)

    def _deduplicate_violations(self, violations: list[dict]) -> list[dict]:
        """Remove duplicate violations based on detected text similarity."""
        seen = set()
        unique = []
        for v in violations:
            key = v.get("violation_detected", "")[:50].lower()
            if key not in seen:
                seen.add(key)
                unique.append(v)
        return unique

    def _violation_date_key(self, violation: dict) -> str | None:
        """Normalize detected_at to YYYY-MM-DD for trend grouping."""
        detected = violation.get("detected_at")
        if isinstance(detected, datetime):
            return detected.strftime("%Y-%m-%d")
        if isinstance(detected, str) and detected:
            return detected[:10]
        return None

    def _generate_trend_data(self, violations: list[dict]) -> list[dict]:
        """Generate violation trend data for the last 7 days."""
        trends = []
        today = datetime.now()
        for i in range(6, -1, -1):
            date = today - timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            count = sum(
                1 for v in violations if self._violation_date_key(v) == date_str
            )
            trends.append({
                "date": date_str,
                "day": date.strftime("%a"),
                "violations": count,
            })
        return trends
