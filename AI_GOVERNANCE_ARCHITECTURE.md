# AI Governance & Compliance Architecture

## 1. Overview
Government-grade LLMs must be auditable, controllable, and deterministic. Bharat GPT 2.0 embeds strict Governance pipelines at the core `services.llm` router.

## 2. Tracking Dimensions
### Post-Generation Audit Logs
When a chat string resolves, the system securely caches the following attributes into JSON logging structures:
- `tokens_consumed`: Absolute cost analytics attached to tenant overrides.
- `model_used`: Hard tracks if the system utilized the internal fallback `gpt-3.5-turbo` or the advanced `gpt-4`.
- `confidence_score`: Natively mocks and prepares integration hooks to scale LLM self-evaluation routines.

### Bias Detection Pipelines
A strict pre/post heuristic filter sits on the output stream (`check_bias_presence()`). Currently implemented via strict lexical gating, the structural frame allows drop-in deployment of localized HuggingFace Zero-Shot classification models dynamically validating semantic outputs for "discrimination" without exposing the user to the raw feed. Any detection triggers the `AI_BIAS_DETECTED` system alert event implicitly bypassing normal operation stacks directly into Admin Audit Streams.

## 3. Multi-Tenancy Strictness
We added the `Organization` DB model dynamically isolating enterprise traffic. 
Organization configurations override the internal Application state holding independent `OPENAI_API_KEYS` guaranteeing exact financial mapping per sub-domain/sub-government division securely. 
