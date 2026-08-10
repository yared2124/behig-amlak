import json
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

# Node 1: Issue Spotter
def spot_legal_issues(state: CourtLetterState) -> CourtLetterState:
    prompt = f"""
    የሚከተለውን የተጠቃሚ ተረት አንብብ። በውስጡ ያሉትን 3-5 ቁልፍ የህግ ጉዳዮች (legal issues) ለይተህ አውጣ። 
    ልክ እንደ ጠበቃ አስብ። ለምሳሌ: "ያለፈቃድ መባረር", "የውል ጥሰት", "የንብረት ውርስ ክርክር".

    ተረት: {state["narrative"]}

    ውጤቱን በዚህ ቅርጸት ስጠኝ: ["ጉዳይ 1", "ጉዳይ 2", "ጉዳይ 3"]
    ሌላ ምንም ነገር አትጨምር። በትክክለኛው የJSON ቅርጸት ብቻ መልስ።
    """
    response = llm.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        response_format={"type": "json_object"}
    )
    issues_list = json.loads(response.choices[0].message.content)
    state["issues"] = issues_list if isinstance(issues_list, list) else []
    return state

# Node 2: RAG Retriever
def retrieve_laws(state: CourtLetterState) -> CourtLetterState:
    all_texts = []
    for issue in state["issues"]:
        results = rag.search(query=issue, top_k=3)
        all_texts.extend(results)
    unique_texts = list(dict.fromkeys(all_texts))
    state["context"] = "\n\n---\n\n".join(unique_texts)
    return state

# Node 3: Document Generator
def generate_court_document(state: CourtLetterState) -> CourtLetterState:
    prompt = f"""
    አንተ የበህግ አምላክ የህግ ረዳት ነህ። 
    ከታች ያለውን የህግ ማጣቀሻ (context) እና የተጠቃሚውን ተረት ተጠቅመህ የፍርድ ቤት ክስ መግለጫ አዘጋጅ።

    **የተጠቃሚ መረጃ:**
    - ከሳሽ: {state['plaintiff']['name']}, አድራሻ: {state['plaintiff']['address']}
    - ተከሳሽ: {state['defendant']['name']}, አድራሻ: {state['defendant']['address']}

    **የህግ ማጣቀሻ (በዚህ ላይ ብቻ ተመሰረት):**
    {state['context']}

    **የተጠቃሚ ተረት:**
    {state['narrative']}

    **የሚጠበቀው ውጤት (JSON ቅርጸት):**
    በትክክለኛው JSON ቅርጸት የሚከተሉትን መስኮች ይዞ መልስ፦
    {{
        "case_summary": "የጉዳዩ አጭር ማጠቃለያ",
        "statement_of_facts": ["በቁጥር የተዘረዘሩ የሐቁ መግለጫዎች 1", "ሐቅ 2"],
        "legal_grounds": ["በፍትሐ ብሔር ሕግ ቁጥር XXX መሠረት...", "ሕግ 2"],
        "relief_sought": ["ፍርድ ቤት እንዲሰጥ የምጠይቀው 1", "ጥያቄ 2"],
        "pre_conditions": ["ቅድመ ሁኔታ 1", "ሁኔታ 2"],
        "annexures": ["የማያያዣ ሰነድ 1", "ሰነድ 2"],
        "verification": "የማረጋገጫ መግለጫ"
    }}
    """
    response = llm.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        response_format={"type": "json_object"}
    )
    state["final_json"] = json.loads(response.choices[0].message.content)
    return state

# Build and compile the LangGraph workflow
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