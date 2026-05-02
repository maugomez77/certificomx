import anthropic

HAIKU = "claude-haiku-4-5-20251001"
SONNET = "claude-sonnet-4-20250514"

client = anthropic.Anthropic()


def suggest_career_path(worker: dict) -> dict:
    """Claude Sonnet: suggest 2-3 certification paths ranked by US placement probability."""
    prompt = f"""You are a Mexican trades career advisor specializing in US nearshoring placements.

Worker profile:
- Name: {worker.get('name')}
- Trade: {worker.get('trade')}
- Experience: {worker.get('experience_years')} years
- Education: {worker.get('education_level')}
- English level: {worker.get('english_level')}
- City: {worker.get('city')}, {worker.get('state')}

Suggest 2-3 certification paths that would maximize this worker's chances of US job placement.
For each path provide:
1. Certification name and authority (CONALEP/CONOCER/STPS/NOM)
2. US equivalent certification
3. Estimated timeline to complete
4. Expected US salary range after placement ($USD/year)
5. US placement probability (%)
6. Key steps to achieve it

Respond in JSON format:
{{
  "paths": [
    {{
      "name": "...",
      "authority": "...",
      "us_equivalent": "...",
      "timeline_months": N,
      "expected_salary_usd_min": N,
      "expected_salary_usd_max": N,
      "placement_probability_pct": N,
      "steps": ["step1", "step2", ...]
    }}
  ],
  "recommendation": "Overall recommendation in Spanish"
}}"""

    response = client.messages.create(
        model=SONNET,
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}],
    )
    import json
    text = response.content[0].text
    try:
        start = text.find("{")
        end = text.rfind("}") + 1
        return json.loads(text[start:end])
    except Exception:
        return {"paths": [], "recommendation": text}


def match_jobs(worker: dict, jobs: list) -> list:
    """Claude Haiku: score top 5 matching jobs with reasoning."""
    if not jobs:
        return []

    jobs_summary = "\n".join(
        f"ID {j.get('id')}: {j.get('title')} at {j.get('employer_id')} | "
        f"Trade: {j.get('trade')} | English: {j.get('required_english_level')} | "
        f"Salary: ${j.get('salary_usd_min')}-${j.get('salary_usd_max')}/yr | "
        f"Visa: {j.get('visa_sponsored')} | Location: {j.get('location_type')}"
        for j in jobs[:20]
    )

    prompt = f"""Worker profile: trade={worker.get('trade')}, english={worker.get('english_level')}, experience={worker.get('experience_years')}yrs

Available jobs:
{jobs_summary}

Return the top 5 best matches as JSON array:
[{{"job_id": N, "match_score": 0-100, "reasoning": "brief reason in Spanish"}}]
Only return the JSON array, nothing else."""

    response = client.messages.create(
        model=HAIKU,
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}],
    )
    import json
    text = response.content[0].text
    try:
        start = text.find("[")
        end = text.rfind("]") + 1
        return json.loads(text[start:end])
    except Exception:
        return []


def assess_english(question_answers: list) -> dict:
    """Claude Haiku: evaluate 5 Q&A pairs, return level + score."""
    qa_text = "\n".join(
        f"Q: {qa.get('question', '')}\nA: {qa.get('answer', '')}"
        for qa in question_answers
    )

    prompt = f"""Evaluate this English assessment. The worker answered 5 questions in English.

{qa_text}

Score each answer 0-20 points for grammar, vocabulary, and comprehension.
Return JSON:
{{
  "total_score": 0-100,
  "level": "none|basic|intermediate|advanced",
  "feedback_es": "Retroalimentación en español para el trabajador",
  "strengths": ["strength1", "strength2"],
  "areas_to_improve": ["area1", "area2"]
}}"""

    response = client.messages.create(
        model=HAIKU,
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}],
    )
    import json
    text = response.content[0].text
    try:
        start = text.find("{")
        end = text.rfind("}") + 1
        return json.loads(text[start:end])
    except Exception:
        return {"total_score": 0, "level": "none", "feedback_es": text}


def get_market_intel() -> dict:
    """Claude Haiku + DuckDuckGo: live market intelligence on nearshoring trades."""
    search_results = []
    try:
        from ddgs import DDGS
        with DDGS() as ddgs:
            results = list(ddgs.text(
                "Mexico nearshoring skilled trades US salary 2025 welding electrician automotive",
                max_results=5
            ))
            search_results = [r.get("body", "") for r in results]
    except Exception:
        pass

    context = "\n".join(search_results[:3]) if search_results else "No live data available."

    prompt = f"""You are an expert on Mexico-US nearshoring labor markets.

Recent market data:
{context}

Provide a market intelligence report covering:
1. Top 5 trades in demand for US nearshoring (ranked)
2. Average US salaries by trade (USD/year)
3. Key certifications US employers require
4. English level requirements trend
5. Best Mexican states/cities for skilled trade workers
6. 2025-2026 outlook

Return as JSON:
{{
  "top_trades": [{{"trade": "...", "demand": "high/medium/low", "avg_salary_usd": N, "growth": "..."}}],
  "salary_ranges": {{"welding": {{"min": N, "max": N}}, "electrical": {{"min": N, "max": N}}, ...}},
  "key_certifications": ["cert1", "cert2", ...],
  "english_trend": "...",
  "best_cities": ["city1", "city2", ...],
  "outlook": "...",
  "updated_at": "2026-05-01"
}}"""

    response = client.messages.create(
        model=HAIKU,
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}],
    )
    import json
    text = response.content[0].text
    try:
        start = text.find("{")
        end = text.rfind("}") + 1
        return json.loads(text[start:end])
    except Exception:
        return {"error": "Could not parse market intel", "raw": text}
