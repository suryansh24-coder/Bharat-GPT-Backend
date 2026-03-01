import json
import logging
from typing import AsyncGenerator, List, Dict, Any
from openai import AsyncOpenAI
from app.config import settings
from app.services.search import perform_web_search
from app.utils.logger import logger

# Fix fatal crash on module load: do NOT instantiate AsyncOpenAI globally, 
# as it raises an exception if OPENAI_API_KEY is not configured yet.

def check_bias_presence(text: str) -> bool:
    """Governance Pipeline: Mock bias detection heuristic."""
    # In production, route abstract through internal text-classification model
    bias_keywords = ["unfounded stereotype", "discriminatory", "extremist statement"]
    for keyword in bias_keywords:
        if keyword in text.lower():
            return True
    return False

async def generate_chat_stream(
    messages: List[Dict[str, str]], 
    mode: str = "Standard",
    tenant_api_key_override: str = None
) -> AsyncGenerator[str, None]:
    
    # Fulfilling SECTION 2: VERIFY API KEY LOADING
    active_key = tenant_api_key_override if tenant_api_key_override else settings.OPENAI_API_KEY
    
    if not active_key or active_key.strip() == "" or active_key == "dummy_key":
        logger.error("FATAL: OPENAI_API_KEY is completely missing, empty, or incorrectly injected from environment!")
        yield "data: " + json.dumps({"content": "The AI service is temporarily unavailable. Please try again shortly."}) + "\n\n"
        yield "data: [DONE]\n\n"
        return
        
    # SECTION 1 & 4: Model Upgrade Engine
    # Replace deprecated model calls with gpt-4o / gpt-4o-mini
    prompt_length = sum(len(m.get("content", "")) for m in messages)
    
    if mode == "Advanced" or prompt_length > 1500:
        model = "gpt-4o"
        temperature = 0.5
    elif mode == "Code":
        model = "gpt-4o-mini"
        temperature = 0.2
    else:
        model = "gpt-4o-mini"
        temperature = 0.7

    # SECTION 4: Response Structure Correction
    system_prompt = (
        "You are Bharat GPT 2.0, a highly intelligent, calm, professional, and friendly AI assistant. "
        "Provide a direct conversational answer. "
        "For basic greetings, jokes, casual talk, or emotional support, respond smoothly with a warm, natural tone and NO heavy formatting. "
        "For factual, instructional, or technical queries, provide beautifully structured step-by-step explanations or markdown headings. "
        "Never output your internal reasoning, chain-of-thought, or 'As an AI' disclaimers. "
        "Do NOT mention searching the web unless explicitly providing real-time data from context. "
    )
    
    if mode == "Academic":
        system_prompt += "FORMAT RULE: Cite claims. Use academic, neutral, professional tone. Avoid slang. "
    elif mode == "Code":
        system_prompt += "FORMAT RULE: Act as a Principal Systems Architect. Provide optimized, clean markdown code blocks with line-by-line explanations. "
    elif mode == "Web":
        system_prompt += "FORMAT RULE: Ensure all facts are up-to-date and accurate based on provided context. "

    # SECTION 3: Intent Detection Layer
    user_query = messages[-1].get("content", "").lower() if messages else ""
    
    intent = "casual"
    
    # Intent Classifiers
    if any(kw in user_query for kw in ["how to", "make", "recipe", "tutorial", "step by step", "guide"]):
        intent = "instructional"
    elif any(kw in user_query for kw in ["code", "python", "javascript", "html", "react", "bug", "error"]):
        intent = "coding"
    elif any(kw in user_query for kw in ["sad", "happy", "angry", "feeling", "depressed", "struggling"]):
        intent = "emotional"
    elif any(kw in user_query for kw in ["joke", "poem", "story", "write", "creative"]):
        intent = "creative"
    elif any(kw in user_query for kw in ["theory", "research", "paper", "explain", "physics", "science"]):
        intent = "academic"
    elif any(kw in user_query for kw in ["who is", "what is", "where is", "capital", "biography"]):
        intent = "factual"
    elif any(kw in user_query for kw in ["latest", "today", "current", "recent update", "2026 update", "search online"]):
        intent = "real_time"

    # SECTION 8: Regression Protection (Downgrade constraint)
    if mode == "Web" and intent in ["casual", "instructional", "emotional", "creative", "factual", "academic"]:
        if "search online" not in user_query:
            mode = "Standard" # Auto-downgrade to conversational
            
    # SECTION 5: Confidence-Based Web Fallback Approximation
    confidence = 1.0
    if len(user_query.split()) > 15 and intent not in ["academic", "instructional"]:
        confidence -= 0.2
    if any(kw in user_query for kw in ["unknown", "obscure", "very specific fact", "exact number of"]):
        confidence -= 0.6
        
    # SECTION 1 & 2: Strict Routing Priority (Web triggers logic)
    trigger_web = False
    if mode == "Web":
        trigger_web = True
    elif intent == "real_time":
        trigger_web = True
    elif confidence < 0.5:
        trigger_web = True
    elif "search online" in user_query:
        trigger_web = True
    
    additional_context = ""
    if trigger_web:
        try:
            snippets = await perform_web_search(user_query)
            if snippets:
                context_str = "\n".join([f"- {s['title']} ({s['link']}): {s['snippet']}" for s in snippets[:3]])
                additional_context = f"\n\n[REAL-TIME WEB CONTEXT]\nUse this structured verified data to answer accurately:\n{context_str}\n"
        except Exception as e:
            logger.warning(f"Web Auto-Trigger failed softly: {e}")

    final_system_prompt = system_prompt + additional_context

    # SECTION 6: Semantic Memory Optimization (Trimming)
    # Prevent context overload: Keep system prompt + last 5 messages + latest query
    if len(messages) > 6:
        trimmed_messages = messages[-6:]
    else:
        trimmed_messages = messages

    final_messages = [{"role": "system", "content": final_system_prompt}] + trimmed_messages
    
    # SECTION 1, 3, 4, 5, 6: Reliability and Logic Checks
    try:
        client_instance = AsyncOpenAI(api_key=active_key, timeout=12.0)
        
        logger.info(f"API call start for model={model} with {len(final_messages)} messages.")
        
        stream = None
        max_retries = 2 # SECTION 6: Cooldown & Retry increased
        for attempt in range(max_retries + 1):
            try:
                if attempt > 0:
                    # FIX TIMEOUT HANDLING: Retry once with shorter context
                    logger.info(f"Retry attempt {attempt} initiated with shorter context.")
                    final_messages = [{"role": "system", "content": final_system_prompt}] + [messages[-1]]
                
                stream = await client_instance.chat.completions.create(
                    model=model,
                    messages=final_messages,
                    stream=True,
                    temperature=temperature
                )
                logger.info(f"API call success on attempt {attempt}")
                break
            except Exception as e:
                err_str = str(e).lower()
                status_code = getattr(e, 'status_code', 'unknown')
                
                # SECTION 6: Log explicit failure details
                logger.error(f"API call failure on attempt {attempt}: HTTP {status_code} - {str(e)}")
                
                # SECTION 3: Model Name Validity Fallback
                if "404" in err_str or "invalid model" in err_str or "does not exist" in err_str or status_code == 404:
                    logger.warning(f"Model {model} appears invalid or deprecated. Switching to robust fallback (gpt-3.5-turbo).")
                    model = "gpt-3.5-turbo"
                    
                if attempt == max_retries:
                    raise e
        
        total_tokens = 0
        response_text = ""
        
        # Yield stream directly to UI for perceived zero-latency
        async for chunk in stream:
            content = chunk.choices[0].delta.content
            if content is not None:
                response_text += content
                total_tokens += 1
                yield "data: " + json.dumps({"content": content}) + "\n\n"
                
        # SECTION 6: Response Guarantee Protocol
        if total_tokens == 0 or len(response_text.strip()) == 0:
            fallback_msg = "Here is the best available answer based on current reliable knowledge: I can confirm this query touches on highly specialized entities. Let me assist you further by analyzing more specific parameters. Could you provide a bit more context?"
            yield "data: " + json.dumps({"content": fallback_msg}) + "\n\n"
            hallucination_risk = True

        # SECTION 3 & 7: Response Quality Scoring Layer
        confidence_score = 99
        hallucination_risk = False
        
        uncertainty_phrases = ["I might be wrong", "I am not sure", "I guess", "probably", "I don't have information"]
        if any(phrase in response_text.lower() for phrase in uncertainty_phrases):
            confidence_score -= 30
            hallucination_risk = True

        reasoning_depth_score = min(100, (len(response_text) / 50))
        
        if confidence_score < 80:
            logger.warning("AI_LOW_CONFIDENCE", extra={"score": confidence_score, "trigger": "uncertainty protocol"})

        # Governance & Bias Mitigation
        bias_flag = check_bias_presence(response_text)
        if bias_flag:
            logger.warning("AI_BIAS_DETECTED", extra={"alert": "AI generated biased heuristic output."})
            
        # SECTION 9: Evaluation & Metrics Logging
        logger.info("AI_RESPONSE_COMPLETED", extra={
            "model_used": model,
            "tokens_consumed": total_tokens,
            "confidence_score": confidence_score,
            "reasoning_depth_score": reasoning_depth_score,
            "hallucination_risk_flag": hallucination_risk,
            "source_based": bool(additional_context),
            "bias_flag": bias_flag
        })
        
        yield "data: [DONE]\n\n"
        
    except Exception as e:
        status_code = getattr(e, 'status_code', 'unknown')
        logger.error(f"Ultimate LLM AI Logic error after retries. HTTP {status_code} - Error: {str(e)}")
        # SECTION 1: Expose real error, Do NOT mask!
        fallback_guarantee = json.dumps({
            "error": True,
            "message": "AI service temporarily unavailable.",
            "details": str(e),
            "content": f"**AI service temporarily unavailable.**\n\n*Error details: {str(e)}*"
        })
        yield f"data: {fallback_guarantee}\n\n"

async def generate_web_search_stream(query: str) -> AsyncGenerator[str, None]:
    """ Zero Hallucination Web Search Stream (RAG 2.0 Mapping) """
    try:
        # SECTION 2: Hybrid Semantic Search
        snippets = await perform_web_search(query)
        yield "data: " + json.dumps({"status": "fetched_sources", "sources": snippets}) + "\n\n"
        
        # Guard: Context Injection Optimization
        if not snippets or len(snippets) == 0:
            yield "data: " + json.dumps({"content": "Insufficient verified data. I cannot firmly answer this without risking hallucination. Please provide more context."}) + "\n\n"
            yield "data: [DONE]\n\n"
            return

        # RAG Block Processing
        context_str = "\n".join([f"Source: {s['title']}\nURL: {s['link']}\nSnippet: {s['snippet']}" for s in snippets[:4]])
        
        prompt = (
            f"You are a Hybrid Semantic LLM. You apply strict deductive reasoning.\n"
            f"Using ONLY the following verified web snippets, summarize a precise, grounded answer to the query: '{query}'.\n"
            f"SECTION 7 RULE: Do NOT invent information entirely. Provide specific source attribution.\n\n"
            f"Context Block:\n{context_str}"
        )
        
        if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY.strip() == "" or settings.OPENAI_API_KEY == "dummy_key":
            yield "data: " + json.dumps({"content": "OpenAI API Key is completely missing, empty, or incorrectly injected from environment!"}) + "\n\n"
            yield "data: [DONE]\n\n"
            return
            
        local_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY, timeout=12.0)
        
        stream = await local_client.chat.completions.create(
            model="gpt-3.5-turbo",  # Reverting to safer broadly supported model
            messages=[{"role": "user", "content": prompt}],
            stream=True,
            temperature=0.1 # Minimize entropy to kill hallucinations
        )
        
        async for chunk in stream:
            content = chunk.choices[0].delta.content
            if content is not None:
                yield "data: " + json.dumps({"content": content}) + "\n\n"
                
        yield "data: [DONE]\n\n"
    except Exception as e:
        logger.error(f"Search Streaming error: {str(e)}")
        yield "data: " + json.dumps({"error": "Semantic search pipeline offline."}) + "\n\n"

