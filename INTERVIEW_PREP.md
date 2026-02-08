# Interview Prep - Claims Processing Pipeline

## If Asked: "How did you build this?"

**Good Answer:**
"I used Amazon Q to scaffold the boilerplate code and validate my regex patterns, then I refined the routing logic, prioritized the business rules based on risk management principles, and added comprehensive test cases including edge cases like low-value injury claims."

**Avoid:**
"Amazon Q built everything" or "I wrote it all from scratch"

## If Asked: "Is this production-ready?"

**Good Answer:**
"It's a production-oriented prototype that demonstrates the core logic. For actual production, I'd add structured logging, comprehensive unit tests, schema validation, and externalize the routing rules to a config file for easier maintenance."

**Avoid:**
"Yes, it's production-ready" (invites criticism)

## If Asked: "Why this routing priority?"

**Answer:**
"The priority follows risk management principles: Risk → Completeness → Specialization → Speed.

1. Fraud overrides everything (risk management)
2. Missing data blocks automation (completeness required)
3. Injury needs specialists even if cheap (specialization trumps efficiency)
4. Fast-track only when clean (efficiency optimization)

For example, a $4,500 injury claim routes to Specialist Queue, not Fast-track, because medical expertise is required regardless of claim value."

## If Asked: "What are the limitations?"

**Answer:**
"Three main limitations:

1. **Field extraction** assumes consistent FNOL labels - real systems would need schema normalization or ML-assisted entity extraction
2. **No semantic validation** - doesn't check if incident date is within policy period or validate policy number formats
3. **Fixed rules** - can't adapt to new patterns without code changes. In production, I'd externalize rules to JSON/YAML for easier updates."

## If Asked: "How would you scale this?"

**Answer:**
"Three phases:

**Short-term**: Add date validation, externalize rules to config, implement structured logging

**Medium-term**: Add batch processing with parallel execution, REST API wrapper, database integration for claim tracking

**Long-term**: Integrate ML for entity extraction (NER), add anomaly detection for fraud, implement confidence scoring for routing decisions"

## Key Strengths to Highlight

✅ **Deterministic & Explainable** - Every decision has clear reasoning
✅ **Conflict Resolution** - Strict priority order handles edge cases (e.g., low-value injury)
✅ **Test Coverage** - 6 samples covering all routing scenarios
✅ **Junior-Appropriate** - Clean, commented, no overengineering
✅ **Self-Aware** - Acknowledges limitations and scaling path

## Red Flags to Avoid

❌ Don't claim it's "production-ready"
❌ Don't say "AI built everything"
❌ Don't oversell the regex extraction accuracy
❌ Don't ignore the conflict case question

## Test Results Summary

All 6 test cases pass:
- Fast-track: $8,500 property damage
- Specialist Queue: $18,000 injury (medium value)
- Specialist Queue: $4,500 injury (conflict case - proves priority works)
- Investigation Flag: fraud keywords detected
- Manual Review: missing claim_type field
- Manual Review: $125,000 high-value claim
