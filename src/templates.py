from __future__ import annotations

STUDENT_TEMPLATE = {
    "pages": [
        "cover",
        "incident_report",
        "evidence_log",
        "investigation_plan",
        "evidence_analysis",
        "final_report",
    ]
}

TEACHER_TEMPLATE = {
    "sections": [
        "case_overview",
        "learning_objectives",
        "materials_list",
        "setup_instructions",
        "timeline",
        "expected_solution",
        "debrief_questions",
        "real_world_connection",
        "safety_notes",
    ]
}

FIELD_DEFAULTS = {
    "case_id": "CSI-000",
    "title": "Caso senza titolo",
    "age_group": "",
    "physics_topic": "",
    "cover_image": "",
    "mystery": "",
    "story_intro": "",
    "scene_evidence": "",
    "witness_1": "",
    "witness_2": "",
    "witness_3": "",
    "mission": "",
    "hypothesis_1": "",
    "hypothesis_2": "",
    "hypothesis_3": "",
    "variable_changed": "",
    "quantity_measured": "",
    "expected_graph": "",
    "graph_shape": "",
    "materials": "",
    "teacher_solution": "",
    "educational_message": "",
    "real_world_connection": "",
    "step_1_observe": "",
    "step_2_hypothesize": "",
    "step_3_experiment": "",
    "step_4_record_data": "",
    "step_5_build_graph": "",
    "step_6_conclusion": "",
}


def normalize_case(raw: dict[str, object]) -> dict[str, str]:
    case = dict(FIELD_DEFAULTS)
    for key in FIELD_DEFAULTS:
        value = raw.get(key, "")
        case[key] = "" if value is None else str(value).strip()
    return case
