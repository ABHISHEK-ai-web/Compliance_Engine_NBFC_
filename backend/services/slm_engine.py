import json
import logging
import re

from config import settings

logger = logging.getLogger(__name__)


class SLMEngine:
    _instance = None
    _model = None
    _tokenizer = None
    _load_failed = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @property
    def enabled(self) -> bool:
        return settings.use_slm

    def _load_model(self):
        if not settings.use_slm:
            return None, None
        if self._load_failed:
            return None, None
        if self._model is not None:
            return self._model, self._tokenizer

        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer

            logger.info("Loading SLM: %s (first run downloads from HuggingFace)", settings.model_name)
            self._tokenizer = AutoTokenizer.from_pretrained(
                settings.model_name,
                trust_remote_code=True,
            )
            self._model = AutoModelForCausalLM.from_pretrained(
                settings.model_name,
                torch_dtype=torch.float32,
                device_map="cpu",
                trust_remote_code=True,
                low_cpu_mem_usage=True,
            )
            if self._tokenizer.pad_token is None:
                self._tokenizer.pad_token = self._tokenizer.eos_token
            logger.info("SLM loaded successfully")
        except Exception as exc:
            logger.warning("SLM load failed, rule-engine-only mode: %s", exc)
            self._load_failed = True
            return None, None

        return self._model, self._tokenizer

    def generate(self, prompt: str, max_new_tokens: int = None) -> str:
        """Generate text completion from the SLM."""
        if not settings.use_slm:
            return ""

        model, tokenizer = self._load_model()
        if model is None or tokenizer is None:
            return ""

        import torch

        max_tokens = max_new_tokens or settings.max_new_tokens
        prompt = prompt[: settings.slm_max_input_chars]

        inputs = tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=1024,
        )

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                temperature=0.3,
                top_p=0.9,
                do_sample=True,
                repetition_penalty=1.1,
                pad_token_id=tokenizer.pad_token_id,
            )

        generated_ids = outputs[0][inputs["input_ids"].shape[1] :]
        return tokenizer.decode(generated_ids, skip_special_tokens=True).strip()

    def analyze_compliance(self, prompt: str) -> dict:
        """Run compliance analysis and parse structured output."""
        raw_output = self.generate(prompt)
        if not raw_output:
            return {"violations": [], "compliance_score": 100, "summary": "SLM disabled or unavailable."}
        return self._parse_compliance_output(raw_output)

    def answer_query(self, prompt: str) -> str:
        """Generate answer for an audit query."""
        answer = self.generate(prompt, max_new_tokens=200)
        if answer:
            return answer
        return "SLM is disabled or still loading. Use rule-engine analysis or enable USE_SLM=true."

    def _parse_compliance_output(self, raw_output: str) -> dict:
        """Parse the SLM output into structured compliance findings."""
        try:
            json_match = re.search(r"\{[\s\S]*\}", raw_output)
            if json_match:
                parsed = json.loads(json_match.group())
                if "violations" in parsed:
                    return parsed
        except (json.JSONDecodeError, AttributeError):
            pass

        return self._fallback_parse(raw_output)

    def _fallback_parse(self, raw_output: str) -> dict:
        """Fallback parsing when JSON extraction fails."""
        violations = []
        severity_keywords = {
            "CRITICAL": ["critical", "severe", "mandatory", "must"],
            "HIGH": ["high", "significant", "required", "shall"],
            "MEDIUM": ["medium", "moderate", "should", "recommended"],
            "LOW": ["low", "minor", "advisory", "may"],
        }

        paragraphs = raw_output.split("\n\n")
        for para in paragraphs:
            if not para.strip():
                continue

            detected_severity = "MEDIUM"
            para_lower = para.lower()
            for severity, keywords in severity_keywords.items():
                if any(kw in para_lower for kw in keywords):
                    detected_severity = severity
                    break

            if any(
                term in para_lower
                for term in ["violation", "gap", "missing", "non-compliance", "risk"]
            ):
                violations.append(
                    {
                        "violation_detected": para.strip()[:200],
                        "affected_department": "Compliance",
                        "severity": detected_severity,
                        "regulation_reference": "Requires manual review",
                        "missing_requirement": para.strip()[:150],
                        "explanation": para.strip(),
                        "recommendation": "Review and update internal policy to address this gap.",
                    }
                )

        if not violations:
            violations.append(
                {
                    "violation_detected": "Analysis completed - review raw output",
                    "affected_department": "Compliance",
                    "severity": "MEDIUM",
                    "regulation_reference": "See full analysis",
                    "missing_requirement": "Automated parsing incomplete",
                    "explanation": raw_output[:500],
                    "recommendation": "Manual review of AI output recommended.",
                }
            )

        return {
            "violations": violations,
            "compliance_score": max(0, 100 - len(violations) * 15),
            "summary": raw_output[:300],
        }
