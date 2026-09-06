from google import genai
import os
from dotenv import load_dotenv, find_dotenv
from app.schemas import STAGE_CONTEXT

load_dotenv(find_dotenv())
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


async def get_llm_explanation(
    predicted_stage: int,
    stage_label: str,
    top_features: list,
    confidence: float
) -> str | None:
    try:
        ctx = STAGE_CONTEXT[predicted_stage]

        features_text = ""
        for i, f in enumerate(top_features[:5], 1):
            direction = (
                "↑ increases CKD risk"
                if f["shap_value"] > 0
                else "↓ reduces CKD risk"
            )
            features_text += (
                f"{i}. {f['feature'].replace('_', ' ').title()}: "
                f"value = {f['value']:.3f} | {direction} "
                f"(SHAP: {f['shap_value']:+.4f})\n"
            )

        prompt = f"""
You are a medical AI assistant explaining a Chronic Kidney 
Disease (CKD) prediction result in simple, clear English.

PREDICTION SUMMARY:
- Stage: {predicted_stage} — {stage_label}
- Confidence: {confidence * 100:.1f}%
- Stage Summary: {ctx['summary']}

TOP 5 CONTRIBUTING FACTORS:
{features_text}
(↑ = increases CKD risk | ↓ = reduces CKD risk)

Write your response in this exact flow:

1. WHAT YOUR RESULTS SHOW
In 2-3 sentences, explain what this CKD stage means 
for this specific patient. Keep it simple and clear.

2. KEY FACTORS EXPLAINED
For the top 3 factors above, explain in 1 sentence each 
what that reading means for the patient's kidneys. 
Use plain language — no jargon.

3. IMMEDIATE ADVICE
Urgency level: {ctx['urgency']}
First steps: {ctx['advice']}
Based on the specific factors above, add 1-2 additional 
personalized lifestyle tips for this patient.

4. SEE A DOCTOR
Tell the patient clearly to consult a qualified 
nephrologist. One short sentence only.

Keep the full response under 250 words.
Do not add a long disclaimer — just end naturally.
"""

        
        response = await client.aio.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        return response.text

    except Exception as e:
        print(f"[LLM Error] {e}")
        return None