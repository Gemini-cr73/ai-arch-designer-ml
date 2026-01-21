def architecture_prompt(project_json: str) -> str:
    return f"""
You are a senior cloud architect.

Given the following project description in JSON:

{project_json}

Return a system architecture as STRICT JSON with these keys:
- pattern
- services (list of {{name, responsibility, technologies}})
- data_flows (list of {{source, destination, description}})
- storage (list)
- risks (list)

Return ONLY valid JSON. No explanations.
"""
