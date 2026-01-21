from __future__ import annotations

import random
from pathlib import Path

import pandas as pd

# Output path: data/processed/training.csv
ROOT = Path(__file__).resolve().parents[3]  # .../ai-arch-designer-ml
OUT = ROOT / "data" / "processed" / "training.csv"

random.seed(42)

DOMAINS = ["HR Tech", "FinTech", "EdTech", "Health", "E-commerce", "GovTech", "Cybersecurity"]
SCALES = ["prototype", "startup", "enterprise"]
BUDGETS = ["low", "medium", "high"]
PATTERNS = ["monolith", "microservices", "event-driven", "serverless"]

# Simple rule-based generator (we’ll later replace with real labels or improved heuristics)
def choose_pattern(domain: str, scale: str, budget: str, users: int, compliance_count: int) -> str:
    if scale == "enterprise" and users >= 100000:
        return "event-driven" if budget in ("medium", "high") else "microservices"
    if budget == "low" and scale == "prototype":
        return "monolith"
    if domain in ("FinTech", "Cybersecurity") and compliance_count >= 2:
        return "microservices"
    if scale == "startup" and budget == "high":
        return "microservices"
    return random.choice(PATTERNS)

def choose_components(pattern: str) -> str:
    base = ["api", "db"]
    if pattern in ("microservices", "event-driven"):
        base += ["queue", "worker"]
    if pattern == "event-driven":
        base += ["stream"]
    if pattern == "serverless":
        base += ["functions"]
    # add ML optional pieces
    if random.random() < 0.7:
        base += ["ml-service"]
    if random.random() < 0.4:
        base += ["vector-db"]
    # unique + deterministic order
    base = list(dict.fromkeys(base))
    return ",".join(base)

def risk_score(scale: str, users: int, compliance_count: int, pattern: str) -> float:
    score = 0.10
    if scale == "startup":
        score += 0.15
    if scale == "enterprise":
        score += 0.35
    score += min(users / 1_000_000, 0.25)
    score += min(compliance_count * 0.08, 0.24)
    if pattern == "event-driven":
        score += 0.10
    if pattern == "microservices":
        score += 0.07
    if pattern == "serverless":
        score += 0.05
    return max(0.0, min(score, 0.99))

def main(n_rows: int = 250) -> None:
    rows = []
    for _ in range(n_rows):
        domain = random.choice(DOMAINS)
        scale = random.choice(SCALES)
        budget = random.choice(BUDGETS)
        users = random.choice([50, 200, 1000, 5000, 20000, 100000, 500000])
        compliance_count = random.choice([0, 0, 1, 1, 2, 3])  # biased towards lower
        pattern = choose_pattern(domain, scale, budget, users, compliance_count)
        components = choose_components(pattern)
        r = risk_score(scale, users, compliance_count, pattern)

        rows.append(
            {
                "domain": domain,
                "scale": scale,
                "budget": budget,
                "users": users,
                "compliance_count": compliance_count,
                "pattern": pattern,
                "components": components,
                "risk_score": round(r, 3),
            }
        )

    df = pd.DataFrame(rows)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False)
    print(f"✅ Wrote {len(df)} rows to: {OUT}")

if __name__ == "__main__":
    main()
