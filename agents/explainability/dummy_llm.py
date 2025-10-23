import random
_rng = random.Random(11)

def _choice(xs): return xs[_rng.randrange(len(xs))]

def precedent_opinion(clause: str) -> str:
    cases = [
        "Alpha v. Beta (2011)", "Gamma v. Delta (2019)", "Smith v. Jones (2004)",
        "R. v. Orion (2020)", "Horizon v. Northstar (2017)"
    ]
    return (f"Precedent Agent → For '{clause}'. Likely relevant cases: "
            f"{', '.join(_rng.sample(cases, 2))}. Rule: liability caps must be conspicuous.")

def compliance_opinion(clause: str) -> str:
    flags = ["consumer cap conflict", "missing definition of 'Losses'",
             "unclear carve-outs for fraud", "OK vs policy"]
    return f"Compliance Agent → For '{clause}'. Finding: {_choice(flags)}."

def drafting_suggestion(clause: str) -> str:
    rewrites = [
        "Cap liability at $25 000 or 1× fees; exclude fraud / gross negligence.",
        "Limit indirect damages; define 'Losses' precisely.",
        "Cap excludes confidentiality and data breach claims."
    ]
    return f"Drafting Agent → Suggestion: {_choice(rewrites)}"

def risk_analysis(_: str) -> str:
    risks = ["uncapped indemnity exposure", "ambiguous consequential damages",
             "unenforceable cap for consumers", "no survival period set"]
    return f"Risk Agent → Risks: {', '.join(_rng.sample(risks, 2))}."

def language_quality(_: str) -> str:
    issues = ["passive voice", "undefined terms", "mixed jurisdiction language"]
    fixes = ["shorter sentences", "define terms", "align terminology with Ontario law"]
    return f"Language Quality Agent → Issues: {', '.join(_rng.sample(issues, 2))}. Tips: {', '.join(_rng.sample(fixes, 2))}."
