# Novelty Markers for DSLs

This document explains how to add and use novelty markers in TinyDSL grammars for contamination checking.

## Overview

Novelty markers are special comments in grammar files that declare which identifiers (keywords, units, features) are unique or post-cutoff for a DSL. These markers enable automated contamination checking to verify that DSLs are genuinely novel and weren't in model training data.

## Adding Novelty Markers

### Format

Add comments to your grammar file using this format:

```lark
// Post-cutoff <category>: identifier1, identifier2, identifier3
// Novel <category>: identifier1, identifier2
// Novel features: description of novel features
```

### Categories

The `<category>` can be any word that describes the type of identifiers:
- `keywords` - Language keywords
- `units` - Custom units (for TinyCalc)
- `identifiers` - Custom identifiers
- `tokens` - Custom tokens
- `commands` - Custom commands
- Any custom category you define

### Examples

**TinyCalc:**
```lark
// TinyCalc Grammar - Novel Unit Conversion DSL
// Post-cutoff units: flurb, grobble, zept, quib, voom
```

**Lexi:**
```lark
// Unified Lexi Grammar - Supports all V1 and V2 features
// Post-cutoff keywords: remember, recall, task, call, concat, substring, foreach, match
// Novel features: persistent memory (remember/recall), task definitions
```

**Gli:**
```lark
// Unified Gli Grammar - Supports all V1 and V2 features
// Post-cutoff keywords: draw, rotate, scale, translate, push, pop
// Novel features: procedural graphics DSL, transform stack operations
```

**TinySQL:**
```lark
// TinySQL Grammar - Simplified query DSL
// Post-cutoff keywords: load, filter, select, sort, limit, join
// Novel features: simplified SQL-like syntax for educational purposes
```

**TinyMath:**
```lark
// TinyMath Grammar - General-purpose arithmetic DSL
// Post-cutoff keywords: show
// Novel features: simplified arithmetic calculator with variable assignment
```

## Extensibility

The system is fully extensible - you can:

1. **Add custom categories:** Use any category name that makes sense for your DSL
   ```lark
   // Post-cutoff custom-operators: @, #, $
   // Novel data-types: tensor, matrix, vector
   ```

2. **Multiple marker lines:** Add as many marker lines as needed
   ```lark
   // Post-cutoff keywords: foo, bar, baz
   // Post-cutoff operators: <>, ~>, |>
   // Novel features: pipeline composition, lazy evaluation
   ```

3. **Case-insensitive:** Both `Post-cutoff` and `post-cutoff`, `Novel` and `novel` work

## How It Works

### Contamination Checker

The `ContaminationChecker` class automatically:

1. **Parses grammar comments** using flexible regex patterns
2. **Extracts identifiers** by category
3. **Verifies presence** in grammar and examples
4. **Generates reports** with:
   - List of novel identifiers found
   - Categories and their identifiers
   - Novel features descriptions
   - Uniqueness verdict

### KAIT Integration

The KAIT agent automatically runs contamination checks when initialized:

```python
from tinydsl.agent_tools.kait_agent import KAITAgent
from datetime import datetime

agent = KAITAgent(
    dsl_name="tinycalc",
    check_contamination=True,  # Default: True
    creation_date=datetime(2024, 10, 18),
    model_cutoff=datetime(2025, 1, 1)
)

# Contamination report is included in agent.contamination_report
# and in the final KAIT experiment report
```

## Testing

### Test Single DSL

```bash
python scripts/check_contamination.py
```

### Test All DSLs

```bash
python scripts/test_all_contamination.py
```

### Test KAIT Integration

```bash
python scripts/test_kait_contamination.py
```

## Output Format

Contamination reports include:

```json
{
  "dsl_name": "tinycalc",
  "post_cutoff": false,
  "uniqueness": {
    "novel_identifiers": ["flurb", "grobble", "zept", "quib", "voom"],
    "declared_in_grammar": ["flurb", "grobble", "zept", "quib", "voom"],
    "declared_by_category": {
      "units": ["flurb", "grobble", "zept", "quib", "voom"]
    },
    "novel_features": [],
    "count": 5,
    "unique": true
  },
  "verdict": {
    "contamination_likely": true,
    "novel": false,
    "confidence": "low"
  }
}
```

## Best Practices

1. **Document all novel identifiers:** Be thorough in listing unique keywords
2. **Use descriptive categories:** Help others understand what makes your DSL unique
3. **Add feature descriptions:** Explain conceptually novel aspects
4. **Verify in examples:** Ensure declared identifiers actually appear in your examples
5. **Update when adding features:** Keep markers in sync with grammar changes

## Benefits

- **Automated contamination checking** for KAIT experiments
- **Documentation** of what makes each DSL unique
- **Extensibility** for custom DSL designs
- **Reproducibility** of evaluation protocols
- **Transparency** about novelty claims

## References

- [KAIT Protocol Documentation](../README.md#kait-protocol)
- [Contamination Detection (arxiv:2311.09783)](https://arxiv.org/abs/2311.09783)
- [ContaminationChecker Implementation](../scripts/check_contamination.py)
