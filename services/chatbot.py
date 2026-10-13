"""
AI Traffic Rules Assistant Service (services/chatbot.py)
Handles natural language reasoning on Indian traffic rules, Motor Vehicles Act 1988 / 2019 penalties,
sign interpretation, detection context grounding, and fallback offline responses.
"""

import os
import re
import logging
from sign_info import get_sign_info, SIGN_INFO
from legal_knowledge import get_legal_info, INDIA_CODE_URL, MORTH_URL

logger = logging.getLogger("TrafficChatbot")


class TrafficChatbot:
    def __init__(self):
        """Initializes Gemini AI model or prepares rule-based knowledge fallback."""
        self.api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        self.gemini_model = None
        self.init_llm()

    def init_llm(self):
        """Attempts to initialize Gemini generative model if API key is present."""
        if not self.api_key:
            logger.info("No GEMINI_API_KEY detected in environment. Using Knowledge-Base fallback engine.")
            return

        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            # Try supported flash models
            for model_name in ["gemini-2.5-flash", "gemini-flash-latest", "gemini-2.5-flash-lite"]:
                try:
                    self.gemini_model = genai.GenerativeModel(model_name)
                    logger.info(f"Gemini LLM initialized successfully with model: {model_name}")
                    break
                except Exception as m_err:
                    logger.warning(f"Could not initialize {model_name}: {m_err}")
        except Exception as e:
            logger.warning(f"Failed to configure google.generativeai ({e}). Chatbot will use Knowledge-Base fallback.")
            self.gemini_model = None

    def chat(self, user_message: str, history: list = None, context: dict = None) -> dict:
        """
        Processes a user question, incorporating detection context, conversation history,
        and verified Indian traffic laws.
        Returns:
            {
                "response": str (markdown formatted response),
                "source": "gemini" | "knowledge_base",
                "detected_sign_used": bool,
                "legal_sources": list of dicts
            }
        """
        if history is None:
            history = []
        if context is None:
            context = {}

        # Extract context
        detected_sign_name = context.get("detected_sign")
        detected_class = context.get("class_name")
        confidence = context.get("confidence")
        confidence_pct = context.get("confidence_pct")
        other_detections = context.get("all_detections", [])

        # Retrieve sign knowledge if sign is detected
        sign_meta = {}
        legal_meta = {}
        if detected_class or detected_sign_name:
            search_key = detected_class or detected_sign_name
            sign_meta = get_sign_info(search_key)
            legal_meta = get_legal_info(search_key)

        # Check if user mentioned another sign specifically in their message
        user_sign_key = self._extract_sign_from_query(user_message)
        if user_sign_key and (not detected_class or user_sign_key != detected_class):
            target_sign_meta = get_sign_info(user_sign_key)
            target_legal_meta = get_legal_info(user_sign_key)
        else:
            target_sign_meta = sign_meta
            target_legal_meta = legal_meta

        # Attempt LLM generation first if available
        if self.gemini_model:
            try:
                response_text = self._generate_with_gemini(
                    user_message=user_message,
                    history=history,
                    context=context,
                    target_sign_meta=target_sign_meta,
                    target_legal_meta=target_legal_meta
                )
                return {
                    "response": response_text,
                    "source": "gemini",
                    "detected_sign_used": bool(detected_sign_name),
                    "legal_sources": self._get_sources_list(target_legal_meta)
                }
            except Exception as err:
                logger.error(f"Gemini generation error: {err}. Falling back to knowledge-base engine.")

        # Fallback to local rule-based engine
        fallback_text = self._generate_fallback_response(
            user_message=user_message,
            history=history,
            context=context,
            target_sign_meta=target_sign_meta,
            target_legal_meta=target_legal_meta
        )

        return {
            "response": fallback_text,
            "source": "knowledge_base",
            "detected_sign_used": bool(detected_sign_name),
            "legal_sources": self._get_sources_list(target_legal_meta)
        }

    def _generate_with_gemini(self, user_message: str, history: list, context: dict,
                              target_sign_meta: dict, target_legal_meta: dict) -> str:
        """Constructs prompt grounded in verified legal facts and calls Gemini."""
        prompt = self._build_system_prompt(context, target_sign_meta, target_legal_meta)

        # Convert history to Gemini conversation format or context string
        history_context = ""
        if history:
            history_context = "\n--- PREVIOUS CONVERSATION ---\n"
            for turn in history[-6:]:  # Keep last 6 turns for context
                role = "User" if turn.get("role") == "user" else "Assistant"
                history_context += f"{role}: {turn.get('content', '')}\n"

        full_prompt = f"{prompt}\n\n{history_context}\n--- CURRENT USER QUESTION ---\nUser: {user_message}\n\nAssistant Response:"
        
        response = self.gemini_model.generate_content(full_prompt)
        return response.text.strip()

    def _build_system_prompt(self, context: dict, sign_meta: dict, legal_meta: dict) -> str:
        """Builds grounded system prompt with verified Indian legal knowledge."""
        detected_sign = context.get("detected_sign")
        conf_pct = context.get("confidence_pct", "")
        conf_val = context.get("confidence", 0.0)

        context_snippet = ""
        if detected_sign:
            context_snippet = f"""
[CURRENT MODEL DETECTION CONTEXT]
- Detected Traffic Sign: {detected_sign}
- Detection Model: YOLOv8 Fine-Tuned Object Detector
- Raw Confidence Score: {conf_val} ({conf_pct})
- Note on Uncertainty: The confidence score indicates the model's bounding box and classification confidence for this media frame, not an absolute ground-truth calibration. Acknowledge this honestly if asked.
"""
        else:
            context_snippet = """
[CURRENT MODEL DETECTION CONTEXT]
- No image or video is currently loaded in this chat session.
- Do NOT fabricate that you have detected any sign. If the user asks 'What sign is detected?', explain that no detection is currently loaded and guide them to upload an image or ask general questions.
"""

        legal_snippet = ""
        if legal_meta:
            legal_snippet = f"""
[VERIFIED INDIAN TRAFFIC LAW KNOWLEDGE BASE]
- Applicable Offence: {legal_meta.get('offence', 'N/A')}
- Governing Statute: {legal_meta.get('statute', 'The Motor Vehicles Act, 1988 (amended 2019)')}
- Specific Sections: {legal_meta.get('sections', 'N/A')}
- Verified Penalties: {legal_meta.get('penalties', {})}
- Jurisdiction & State Power: {legal_meta.get('jurisdiction', '')}
- Exceptions/Conditions: {legal_meta.get('conditions', '')}
- Official Statutory Source: [{legal_meta.get('source_title', 'India Code - MVA 1988')}]({legal_meta.get('source_url', INDIA_CODE_URL)})
- MoRTH Official Portal: [MoRTH Official Portal]({MORTH_URL})
"""

        sign_snippet = ""
        if sign_meta:
            sign_snippet = f"""
[SIGN SPECIFICATIONS]
- Name: {sign_meta.get('name')}
- Category: {sign_meta.get('category')} (Mandatory/Regulatory, Cautionary/Warning, or Informatory)
- Legal Meaning: {sign_meta.get('meaning')}
- Risk Severity: {sign_meta.get('risk')}
- Recommended Driver Action: {sign_meta.get('action')}
"""

        return f"""You are the AI Traffic Rules & Road Safety Assistant for an Indian road safety project.
Your goal is to assist Indian drivers, students, and citizens in understanding traffic signs, driving regulations, and legal penalties under Indian law.

{context_snippet}
{sign_snippet}
{legal_snippet}

CRITICAL INSTRUCTIONS & ACCURACY RULES:
1. INDIAN LAW & ACCURACY:
   - Base all legal sections and penalties strictly on The Motor Vehicles Act, 1988 (as amended by the Motor Vehicles Amendment Act, 2019) and Central Motor Vehicles Rules, 1989.
   - NEVER invent or hallucinate legal sections or fines. If a penalty is not explicitly verified, clearly state that it cannot be verified in the statutory database and direct the user to verify at official sources:
     * [India Code (MVA 1988)]({INDIA_CODE_URL})
     * [Ministry of Road Transport and Highways (MoRTH)]({MORTH_URL})
   - Explain that State Governments in India possess compounding powers under Section 200 of the Motor Vehicles Act to adjust certain fines within prescribed ranges.

2. TRAFFIC SIGN DETAILS TO EXPLAIN WHEN ASKED:
   - Meaning & Purpose: Why the sign exists and its legal status (Mandatory/Prohibitory, Cautionary/Warning, or Informatory).
   - Driver Action: Immediate action required (braking, lane positioning, speed control).
   - Potential Hazards: Road collisions, pedestrian risks, rollover hazards.
   - Practical Indian Road Scenarios: Mixed traffic, monsoon driving, night conditions, school zones, ghat roads, unscientific speed breakers.
   - Damaged / Obscured Signs: If a sign is faded, damaged, or partially covered, advise the driver to exercise maximum caution, assume the stricter safety rule, slow down, and report the hazard via local traffic police apps or helplines.
   - Distinguishing Similar Signs: When asked, clearly contrast similar signs (e.g. Stop vs Yield, No Parking vs No Stopping).

3. TONE & FORMAT:
   - Professional, authoritative, helpful, concise.
   - Use clean Markdown formatting with bullet points and bold headers.
   - Provide clickable markdown links for India Code and MoRTH whenever discussing legal penalties.
"""

    def _generate_fallback_response(self, user_message: str, history: list, context: dict,
                                     target_sign_meta: dict, target_legal_meta: dict) -> str:
        """
        Reliable rule-based knowledge engine when LLM API is unavailable.
        Provides detailed, legally verified answers without hallucination.
        """
        q = user_message.lower().strip()
        detected_sign = context.get("detected_sign")
        conf_pct = context.get("confidence_pct", "")
        conf_val = context.get("confidence", 0.0)

        # 1. Check if user is asking about the detected sign
        if any(w in q for w in ["what did you detect", "what is detected", "which sign", "what sign"]):
            if detected_sign:
                return (
                    f"### Detected Sign: **{detected_sign}**\n\n"
                    f"- **Model Detection**: YOLOv8 Object Detector\n"
                    f"- **Confidence Score**: **{conf_pct}** (raw: `{conf_val}`)\n"
                    f"- **Category**: {target_sign_meta.get('category', 'Regulatory')}\n"
                    f"- **Meaning**: {target_sign_meta.get('meaning', '')}\n\n"
                    f"> **Note on Uncertainty**: This confidence score indicates YOLOv8's feature detection confidence. "
                    f"It does not guarantee 100% real-world truth, so drivers should always visually confirm roadside conditions."
                )
            else:
                return (
                    "No traffic sign image or video is currently uploaded in this session. "
                    "Please upload a road image or video above, or ask me any general question about Indian traffic signs, road rules, and legal fines under the Motor Vehicles Act!"
                )

        # 2. Questions about fines, penalties, law, section
        if any(w in q for w in ["fine", "penalty", "law", "challan", "section", "mva", "act", "punishment", "legal"]):
            if target_legal_meta:
                penalties_str = ""
                for k, v in target_legal_meta.get("penalties", {}).items():
                    penalties_str += f"- **{k.replace('_', ' ').title()}**: {v}\n"

                return (
                    f"### ⚖️ Legal Provisions & Penalties in India\n\n"
                    f"**Offence**: {target_legal_meta.get('offence')}\n\n"
                    f"**Applicable Statute & Sections**:\n"
                    f"- **{target_legal_meta.get('statute')}**\n"
                    f"- **Provision**: `{target_legal_meta.get('sections')}`\n\n"
                    f"**Verified Penalties (Central Act)**:\n"
                    f"{penalties_str}\n"
                    f"**Jurisdiction & State Variations**:\n"
                    f"{target_legal_meta.get('jurisdiction')}\n\n"
                    f"**Exceptions / Conditions**:\n"
                    f"{target_legal_meta.get('conditions')}\n\n"
                    f"**Authoritative Official Sources**:\n"
                    f"- [India Code - The Motor Vehicles Act, 1988]({INDIA_CODE_URL})\n"
                    f"- [Ministry of Road Transport and Highways (MoRTH)]({MORTH_URL})"
                )
            else:
                return (
                    "### ⚖️ Indian Traffic Legal Rules\n\n"
                    "Under **The Motor Vehicles Act, 1988 (amended in 2019)**:\n"
                    "- **Section 119**: Imposes a mandatory duty on every driver to obey traffic signs.\n"
                    "- **Section 177 & 177A**: Provide general penalties (₹500 for first offence, ₹1,500 for repeat) for contravening traffic regulations where no specific fine is stated.\n"
                    "- **Section 184**: Covers dangerous or reckless driving (₹1,000 to ₹5,000 fine and/or jail).\n\n"
                    "For verified statutory text, consult:\n"
                    f"- [India Code (MVA 1988)]({INDIA_CODE_URL})\n"
                    f"- [MoRTH Official Portal]({MORTH_URL})"
                )

        # 3. Questions about driver action / what should I do
        if any(w in q for w in ["action", "what should i do", "what to do", "how to drive", "precaution"]):
            action_text = target_sign_meta.get("action", "Drive with caution and obey road regulations.")
            sign_name = target_sign_meta.get("name", detected_sign or "the traffic sign")
            return (
                f"### 🚗 Recommended Driver Action for **{sign_name}**\n\n"
                f"- **Immediate Action**: {action_text}\n"
                f"- **Hazard Awareness**: Check rearview and side mirrors before decelerating or changing lanes.\n"
                f"- **Indian Road Conditions**: Watch for sudden two-wheeler movements, jaywalking pedestrians, and auto-rickshaws.\n"
                f"- **Adverse Weather / Rain**: Increase following distance to at least 4-5 seconds and avoid sudden braking."
            )

        # 4. Questions about damaged or unclear signs
        if any(w in q for w in ["damaged", "unclear", "broken", "obscured", "hidden", "faded", "not clear"]):
            return (
                "### ⚠️ Protocol for Damaged or Obscured Traffic Signs in India\n\n"
                "If a traffic sign is damaged, defaced, covered by foliage, or partially visible:\n"
                "1. **Adopt the Safest Assumption**: Always slow down and assume the stricter regulatory rule (e.g. assume a Stop or Yield requirement at junctions).\n"
                "2. **Look for Secondary Clues**: Look for road surface markings, traffic flow, intersection geometries, or kerb paintings.\n"
                "3. **Do Not Rush**: Never accelerate through an uncontrolled or ambiguously marked intersection.\n"
                "4. **Citizen Reporting**: Report the damaged signage to the local municipal corporation, traffic police helpline, or via the MoRTH Citizen App."
            )

        # 5. Sign meaning / general description
        if target_sign_meta:
            sign_name = target_sign_meta.get("name", detected_sign or "Traffic Sign")
            meaning = target_sign_meta.get("meaning", "Follow standard Indian road regulations.")
            category = target_sign_meta.get("category", "Regulatory")
            risk = target_sign_meta.get("risk", "Medium")
            action = target_sign_meta.get("action", "")

            return (
                f"### 🛑 Traffic Sign Information: **{sign_name}**\n\n"
                f"- **Category**: **{category}** (Mandatory / Regulatory signs must be obeyed under Section 119 MVA)\n"
                f"- **Risk Level**: **{risk} Risk**\n"
                f"- **Legal Meaning**: {meaning}\n"
                f"- **Recommended Action**: {action}\n\n"
                f"Feel free to ask about the **applicable fines in India**, **hazards**, or **practical driving tips**!"
            )

        # 6. Default greeting & guidance
        return (
            "### 🚦 AI Traffic Rules & Safety Assistant\n\n"
            "I can assist you with:\n"
            "1. **Traffic Sign Interpretations**: Meaning, category (Mandatory, Cautionary, Informatory), and hazards.\n"
            "2. **Indian Traffic Laws & Fines**: Verified sections under **The Motor Vehicles Act, 1988 (2019 Amendment)**.\n"
            "3. **Driver Assistance**: Recommended driver actions on Indian highways and urban roads.\n"
            "4. **Damaged / Unclear Sign Protocols**: How to drive safely when signage is obscured.\n\n"
            f"Official Statutory Reference: [India Code - Motor Vehicles Act 1988]({INDIA_CODE_URL})\n\n"
            "How can I help you today?"
        )

    def _extract_sign_from_query(self, query: str) -> str:
        """Detects if a specific traffic sign name is mentioned in user's query."""
        q = query.lower()
        for key in SIGN_INFO.keys():
            readable = key.replace("_", " ")
            if readable in q or key in q:
                return key

        if "stop" in q: return "stop"
        if "yield" in q: return "yield"
        if "parking" in q: return "no_parking"
        if "pedestrian" in q or "zebra" in q: return "pedestrian_crossing"
        if "speed" in q: return "speed_limit_50"
        if "overtake" in q or "passing" in q: return "no_overtaking"
        if "school" in q: return "school_zone"
        if "u-turn" in q or "u turn" in q: return "no_u_turn"
        if "red light" in q or "signal" in q: return "traffic_signals"
        return None

    def _get_sources_list(self, legal_meta: dict) -> list:
        """Returns structured sources list for frontend citation cards."""
        sources = [
            {
                "title": "India Code - The Motor Vehicles Act, 1988",
                "url": INDIA_CODE_URL,
                "authority": "Legislative Department, Ministry of Law and Justice, Govt of India"
            },
            {
                "title": "Ministry of Road Transport and Highways (MoRTH)",
                "url": MORTH_URL,
                "authority": "Government of India"
            }
        ]
        if legal_meta and legal_meta.get("sections"):
            sources.insert(0, {
                "title": f"MVA 1988 - {legal_meta.get('sections')}",
                "url": legal_meta.get("source_url", INDIA_CODE_URL),
                "authority": legal_meta.get("statute", "The Motor Vehicles Act, 1988")
            })
        return sources
