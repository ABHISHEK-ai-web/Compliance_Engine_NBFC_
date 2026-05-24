from services.embedding_service import EmbeddingService
from services.vector_store import VectorStore
from config import settings


COMPLIANCE_ANALYSIS_PROMPT = """You are a regulatory compliance expert analyzing banking regulations and internal policies.

CONTEXT - REGULATORY REQUIREMENTS:
{regulation_context}

CONTEXT - INTERNAL POLICY/SOP:
{policy_context}

TASK: Analyze the internal policy against the regulatory requirements and identify compliance gaps.

For each gap found, provide your analysis in the following JSON format:
{{
    "violations": [
        {{
            "violation_detected": "<brief description of the violation>",
            "affected_department": "<department impacted>",
            "severity": "<CRITICAL|HIGH|MEDIUM|LOW>",
            "regulation_reference": "<specific regulation section>",
            "missing_requirement": "<what is missing>",
            "explanation": "<detailed explanation of why this is a violation>",
            "recommendation": "<actionable remediation step>"
        }}
    ],
    "compliance_score": <0-100>,
    "summary": "<overall compliance assessment>"
}}

Analyze thoroughly and identify ALL compliance gaps. Be specific with references."""


AUDIT_QUERY_PROMPT = """You are a regulatory compliance assistant for banking operations.

RELEVANT CONTEXT:
{context}

USER QUESTION: {question}

Provide a detailed, accurate answer based on the context above. Cite specific sections and clauses.
If the context doesn't contain enough information to fully answer, state what is known and what requires further investigation.

ANSWER:"""


CLAUSE_EXTRACTION_PROMPT = """Extract all regulatory obligations and compliance requirements from the following text.

TEXT:
{text}

For each obligation found, provide:
- Clause reference
- Requirement description
- Compliance action needed
- Applicable department

Format as JSON array."""


class RAGEngine:
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStore()

    def retrieve_relevant_regulations(self, query: str, n_results: int = None) -> list[dict]:
        """Retrieve relevant regulation chunks for a query."""
        n_results = n_results or settings.top_k_results
        query_embedding = self.embedding_service.generate_query_embedding(query)
        results = self.vector_store.query(
            collection_name="regulations",
            query_embedding=query_embedding,
            n_results=n_results,
        )
        return self._format_results(results)

    def retrieve_relevant_policies(self, query: str, n_results: int = None) -> list[dict]:
        """Retrieve relevant policy chunks for a query."""
        n_results = n_results or settings.top_k_results
        query_embedding = self.embedding_service.generate_query_embedding(query)
        results = self.vector_store.query(
            collection_name="policies",
            query_embedding=query_embedding,
            n_results=n_results,
        )
        return self._format_results(results)

    def build_compliance_prompt(self, regulation_chunks: list[dict], policy_chunks: list[dict]) -> str:
        """Construct the compliance analysis prompt with retrieved context."""
        reg_context = "\n\n".join([
            f"[Source: {c['metadata'].get('filename', 'Unknown')}, Page {c['metadata'].get('page_number', '?')}]\n{c['text']}"
            for c in regulation_chunks
        ])
        policy_context = "\n\n".join([
            f"[Source: {c['metadata'].get('filename', 'Unknown')}, Page {c['metadata'].get('page_number', '?')}]\n{c['text']}"
            for c in policy_chunks
        ])
        return COMPLIANCE_ANALYSIS_PROMPT.format(
            regulation_context=reg_context,
            policy_context=policy_context,
        )

    def build_audit_query_prompt(self, question: str, context_chunks: list[dict]) -> str:
        """Construct the audit query prompt."""
        context = "\n\n".join([
            f"[{c['metadata'].get('filename', 'Unknown')}, Page {c['metadata'].get('page_number', '?')}]\n{c['text']}"
            for c in context_chunks
        ])
        return AUDIT_QUERY_PROMPT.format(context=context, question=question)

    def retrieve_for_analysis(self, query: str = None) -> tuple[list[dict], list[dict]]:
        """Retrieve both regulation and policy chunks for compliance analysis."""
        search_query = query or "compliance requirements obligations regulatory guidelines"
        regulation_chunks = self.retrieve_relevant_regulations(search_query)
        policy_chunks = self.retrieve_relevant_policies(search_query)
        return regulation_chunks, policy_chunks

    def _format_results(self, results: dict) -> list[dict]:
        """Format ChromaDB results into structured list."""
        formatted = []
        if not results or not results.get("documents"):
            return formatted

        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]

        for doc, meta, dist in zip(documents, metadatas, distances):
            formatted.append({
                "text": doc,
                "metadata": meta,
                "relevance_score": 1 - dist,
            })
        return formatted
