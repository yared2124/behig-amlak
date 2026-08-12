# (feat): LangGraph legal reasoning engine.
# Description: Implements Issue Spotter -> RAG Retriever -> Structured Generator.
# Updated: sanitizes context, handles dict responses from issue spotter,
# improved prompt to force use of retrieved context.

import json
import re
from groq import Groq
from langgraph.graph import StateGraph, END
from app.core.config import settings
from app.services.rag_pipeline import rag
from app.models.schemas_court import CourtLetterSchema

llm = Groq(api_key=settings.groq_api_key)

class CourtLetterState(dict):
    narrative: str
    plaintiff: dict
    defendant: dict
    issues: list
    context: str
    final_json: dict

# ----- Node 1: Issue Spotter -----
def spot_legal_issues(state: CourtLetterState) -> CourtLetterState:
    prompt = f"""
    የሚከተለውን የተጠቃሚ ተረት አንብብ። በውስጡ ያሉትን 3-5 ቁልፍ የህግ ጉዳዮች (legal issues) ለይተህ አውጣ። 
    ልክ እንደ ጠበቃ አስብ። ለምሳሌ: "ያለፈቃድ መባረር", "የውል ጥሰት", "የንብረት ውርስ ክርክር".

    ተረት: {state["narrative"]}

    **አስፈላጊ:** ውጤቱን በትክክለኛው የJSON ቅርጸት ስጠኝ። መልሱ ቀላል የሆነ የጽሁፎች ዝርዝር (list of strings) መሆን አለበት። ለምሳሌ: ["ጉዳይ 1", "ጉዳይ 2", "ጉዳይ 3"]
    """
    response = llm.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        response_format={"type": "json_object"}
    )
    
    result = json.loads(response.choices[0].message.content)
    
    # ---- Handle different response formats ----
    if isinstance(result, list):
        issues = result
    elif isinstance(result, dict):
        # If keys are like "ጉዳይ 1", extract the "ጉዳይ" field from each value if present
        if all(k.startswith("ጉዳይ") for k in result.keys()):
            issues = []
            for key, value in result.items():
                if isinstance(value, dict) and "ጉዳይ" in value:
                    issues.append(value["ጉዳይ"])
                elif isinstance(value, str):
                    issues.append(value)
                else:
                    issues.append(key if isinstance(value, str) else str(value))
        else:
            # Generic dict: take values if they're strings, else keys
            if all(isinstance(v, str) for v in result.values()):
                issues = list(result.values())
            else:
                issues = list(result.keys())
    else:
        issues = []
    
    state["issues"] = issues
    print(f"✅ Issues extracted: {state['issues']}")
    return state

# ----- Node 2: RAG Retriever -----
def retrieve_laws(state: CourtLetterState) -> CourtLetterState:
    all_texts = []
    for issue in state["issues"]:
        results = rag.search(query=issue, top_k=4)
        all_texts.extend(results)
    unique_texts = list(dict.fromkeys(all_texts))
    state["context"] = "\n\n---\n\n".join(unique_texts)
    print(f"✅ Retrieved {len(unique_texts)} unique chunks.")
    if unique_texts:
        print(f"📄 First 200 chars of context: {state['context'][:200]}...")
    else:
        print("⚠️ No context retrieved!")
    return state

# ----- Node 3: Document Generator (with sanitization & improved prompt) -----
def generate_court_document(state: CourtLetterState) -> CourtLetterState:
    # --- Sanitize and truncate context ---
    raw_context = state.get('context', '')
    # Remove non-printable characters (keep newline, tab, and basic printable ASCII/UTF-8)
    sanitized_context = re.sub(r'[^\x09\x0A\x0D\x20-\x7E\x80-\xFF]', ' ', raw_context)
    # Collapse multiple spaces
    sanitized_context = re.sub(r'\s+', ' ', sanitized_context).strip()
    
    # Truncate to maximum 3000 characters to avoid token overflow
    if len(sanitized_context) > 3000:
        sanitized_context = sanitized_context[:3000] + "... [truncated]"
    print(f"📄 Sanitized context length: {len(sanitized_context)} chars")

    # --- IMPROVED PROMPT: Forces LLM to use the context ---
    prompt = f"""
    አንተ የበህግ አምላክ የህግ ረዳት ነህ። 
    የተጠቃሚውን ጉዳይ በመተንተን የፍርድ ቤት ክስ መግለጫ አዘጋጅ።

    **አስፈላጊ መመሪያ:**
    - ከታች የተሰጠውን የህግ ማጣቀሻ (context) በጥንቃቄ አንብብ።
    - መልስህን በዚህ የህግ ማጣቀሻ ላይ ብቻ መስረት።
    - ከህግ ማጣቀሻው ውጪ ያለ መረጃ አትጠቀም።
    - መልስህ ሙሉ በሙሉ በአማርኛ ይሁን።

    **የተጠቃሚ መረጃ:**
    - ከሳሽ: {state['plaintiff']['name']}
    - ከሳሽ አድራሻ: {state['plaintiff']['address']}
    - ተከሳሽ: {state['defendant']['name']}
    - ተከሳሽ አድራሻ: {state['defendant']['address']}

    **የተጠቃሚ ተረት:**
    {state['narrative']}

    **የህግ ማጣቀሻ (በዚህ ላይ ብቻ ተመሰረት):**
    {sanitized_context}

    **የሚጠበቀው ውጤት (JSON ቅርጸት):**
    ከላይ በተሰጠው የህግ ማጣቀሻ መሰረት የሚከተሉትን መስኮች ይዞ በትክክለኛው JSON ቅርጸት መልስ።
    ከህግ ማጣቀሻው ውስጥ ያሉትን የሕግ አንቀጾች በትክክል ጥቀስ።

    {{
        "case_summary": "የጉዳዩ አጭር ማጠቃለያ (በ3-4 ዓረፍተ ነገር)",
        "statement_of_facts": [
            "በቁጥር የተዘረዘሩ ከተረቱ የተወሰዱ የሐቁ መግለጫዎች",
            "ለምሳሌ: ፩. እኔ አበባቸው ገ/እግዚአብሔር የሟች ገ/ሥላሴ መኮንን ልጅ ነኝ።",
            "፪. ሟቹ በጥቅምት 15 ቀን 2015 ዓ.ም አረፉ።"
        ],
        "legal_grounds": [
            "ከህግ ማጣቀሻው ውስጥ የተወሰዱ የሕግ አንቀጾች እና ትርጉማቸው",
            "ለምሳሌ: በፍትሐ ብሔር ሕግ ቁጥር 842 መሠረት የውርስ መብት የሚከፈተው በሟች ሞት ነው።"
        ],
        "relief_sought": [
            "ፍርድ ቤት እንዲሰጥ የሚጠየቁት ውሳኔዎች",
            "ለምሳሌ: 1. ንብረቱ ለከሳሽ እንዲረከብ።"
        ],
        "pre_conditions": [
            "ክሱ ከመቅረቡ በፊት የተሟሉ ቅድመ ሁኔታዎች",
            "ለምሳሌ: በቀበሌ ደረጃ ለማስታረቅ መሞከር"
        ],
        "annexures": [
            "ከክሱ ጋር የሚቀርቡ ማስረጃዎች ዝርዝር"
        ],
        "verification": "የከሳሹ የማረጋገጫ መግለጫ"
    }}
    """
    
    # --- Call LLM with error handling ---
    try:
        response = llm.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        state["final_json"] = json.loads(response.choices[0].message.content)
        print(f"📦 Final JSON generated with {len(state['final_json'].get('statement_of_facts', []))} facts.")
    except Exception as e:
        print(f"❌ Error in generate_court_document: {e}")
        # Fallback to placeholder with error message
        state["final_json"] = {
            "case_summary": "ስህተት ተከስቷል። እባክዎን እንደገና ይሞክሩ።",
            "statement_of_facts": ["የህግ ማጣቀሻ አልተገኘም።"],
            "legal_grounds": ["የህግ ማጣቀሻ አልተገኘም።"],
            "relief_sought": ["ይቅርታ፣ አገልግሎቱ ጊዜያዊ ችግር አጋጥሞታል።"],
            "pre_conditions": [],
            "annexures": [],
            "verification": "የማረጋገጫ መግለጫ"
        }
    return state

# ----- Build and compile the LangGraph workflow -----
workflow = StateGraph(CourtLetterState)
workflow.add_node("spot_issues", spot_legal_issues)
workflow.add_node("retrieve_laws", retrieve_laws)
workflow.add_node("generate_document", generate_court_document)
workflow.set_entry_point("spot_issues")
workflow.add_edge("spot_issues", "retrieve_laws")
workflow.add_edge("retrieve_laws", "generate_document")
workflow.add_edge("generate_document", END)
app_graph = workflow.compile()

def generate_court_report(narrative: str, plaintiff: dict, defendant: dict) -> dict:
    initial_state = CourtLetterState(
        narrative=narrative,
        plaintiff=plaintiff,
        defendant=defendant,
        issues=[],
        context="",
        final_json={}
    )
    final_state = app_graph.invoke(initial_state)
    return final_state["final_json"]