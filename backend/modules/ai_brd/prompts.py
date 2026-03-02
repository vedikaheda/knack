BRD_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "document_info": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "title": {"type": "string"},
                "version": {"type": "string"},
                "date": {"type": "string"},
                "engagement_model": {"type": ["string", "null"]},
            },
            "required": ["title", "version", "date", "engagement_model"],
        },
        "executive_summary": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "overview": {"type": "string"},
                "phases": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "name": {"type": "string"},
                            "summary": {"type": "string"},
                            "key_features": {"type": ["array", "null"], "items": {"type": "string"}},
                        },
                        "required": ["name", "summary", "key_features"],
                    },
                },
            },
            "required": ["overview", "phases"],
        },
        "business_objectives": {"type": "array", "items": {"type": "string"}},
        "scope": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "in_scope": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "name": {"type": "string"},
                            "details": {"type": ["array", "null"], "items": {"type": "string"}},
                            "phase": {"type": ["string", "null"]},
                        },
                        "required": ["name", "details", "phase"],
                    },
                },
                "out_of_scope": {"type": ["array", "null"], "items": {"type": "string"}},
            },
            "required": ["in_scope", "out_of_scope"],
        },
        "platforms": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "name": {"type": "string"},
                    "type": {"type": "string"},
                    "notes": {"type": ["string", "null"]},
                    "phase": {"type": ["string", "null"]},
                },
                "required": ["name", "type", "notes", "phase"],
            },
        },
        "personas": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "name": {"type": "string"},
                    "description": {"type": ["string", "null"]},
                },
                "required": ["name", "description"],
            },
        },
        "functional_requirements": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "name": {"type": "string"},
                    "features": {"type": "array", "items": {"type": "string"}},
                    "phase": {"type": ["string", "null"]},
                },
                "required": ["name", "features", "phase"],
            },
        },
        "non_functional_requirements": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "category": {"type": "string"},
                    "requirements": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["category", "requirements"],
            },
        },
        "technical_requirements": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "category": {"type": "string"},
                    "requirements": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["category", "requirements"],
            },
        },
        "integrations": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "name": {"type": "string"},
                    "purpose": {"type": ["string", "null"]},
                    "notes": {"type": ["string", "null"]},
                },
                "required": ["name", "purpose", "notes"],
            },
        },
        "data_requirements": {"type": ["array", "null"], "items": {"type": "string"}},
        "ui_ux_requirements": {"type": ["array", "null"], "items": {"type": "string"}},
        "reporting_analytics": {"type": ["array", "null"], "items": {"type": "string"}},
        "support_requirements": {"type": ["array", "null"], "items": {"type": "string"}},
        "assumptions": {"type": ["array", "null"], "items": {"type": "string"}},
        "dependencies": {"type": ["array", "null"], "items": {"type": "string"}},
        "risks": {"type": ["array", "null"], "items": {"type": "string"}},
        "constraints": {"type": ["array", "null"], "items": {"type": "string"}},
        "change_control": {"type": ["array", "null"], "items": {"type": "string"}},
        "compliance_security": {"type": ["array", "null"], "items": {"type": "string"}},
    },
    "required": [
        "document_info",
        "executive_summary",
        "business_objectives",
        "scope",
        "platforms",
        "personas",
        "functional_requirements",
        "non_functional_requirements",
        "technical_requirements",
        "integrations",
        "data_requirements",
        "ui_ux_requirements",
        "reporting_analytics",
        "support_requirements",
        "assumptions",
        "dependencies",
        "risks",
        "constraints",
        "change_control",
        "compliance_security",
    ],
}

SYSTEM_PROMPT = (
    "You are a strict BRD generator. Output ONLY valid JSON that matches the schema. "
    "Do not include extra keys or commentary."
)

USER_PROMPT_TEMPLATE = (
    "Generate a Business Requirements Document from the transcript below. "
    "Follow the provided JSON schema strictly and include all required fields. "
    "Use concise, factual language and avoid marketing copy.\\n\\n"
    "Transcript:\\n{transcript}"
)
