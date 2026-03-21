# ShieldBase Auto Insurance — Quote Calculation Reference

## Purpose

This document describes the simplified formula ShieldBase uses to generate auto insurance quotes. It is intended for internal use by quoting systems and AI assistants.

---

## Base Rate by Coverage Tier

| Tier | Base Monthly Rate |
|---|---|
| Basic | $62 |
| Standard | $118 |
| Comprehensive | $189 |

---

## Rating Factors (Multipliers)

### Driver Age Factor

| Age Range | Multiplier |
|---|---|
| 16–20 | 1.85 |
| 21–24 | 1.40 |
| 25–34 | 1.00 (baseline) |
| 35–54 | 0.92 |
| 55–64 | 0.95 |
| 65–74 | 1.05 |
| 75+ | 1.20 |

### Driving History Factor

| History | Multiplier |
|---|---|
| Clean (no incidents in 3 years) | 1.00 |
| 1 minor violation (speeding ticket) | 1.15 |
| 1 at-fault accident | 1.30 |
| 2+ violations or accidents | 1.55 |
| DUI/DWI (within 5 years) | 2.10 |

### Vehicle Year Factor

| Vehicle Age | Multiplier |
|---|---|
| 0–2 years (new) | 1.20 |
| 3–5 years | 1.10 |
| 6–10 years | 1.00 (baseline) |
| 11–15 years | 0.90 |
| 16+ years | 0.80 |

### Deductible Adjustment

| Deductible | Monthly Adjustment |
|---|---|
| $250 | +$18 |
| $500 | $0 (baseline) |
| $1,000 | -$22 |

---

## Quote Formula

```
monthly_premium = base_rate
                  × age_factor
                  × history_factor
                  × vehicle_year_factor
                  + deductible_adjustment
```

Then apply any applicable discounts:
- Safe driver (clean history): -15%
- Multi-vehicle: -10%
- Bundle (with home or life): -15% to -20%
- Good student: -8%

---

## Example Calculation

**Profile:** 28-year-old, clean record, 2018 Honda Civic, Standard coverage, $500 deductible

- Base rate: $118
- Age factor (25–34): × 1.00
- History factor (clean): × 1.00
- Vehicle year factor (6–10 years): × 1.00
- Deductible ($500): +$0
- **Quoted monthly premium: $118/month**

---

**Profile:** 20-year-old, 1 speeding ticket, 2022 Toyota Camry, Comprehensive, $1,000 deductible

- Base rate: $189
- Age factor (16–20): × 1.85 = $349.65
- History factor (1 violation): × 1.15 = $402.10
- Vehicle year factor (0–2 years): × 1.20 = $482.52
- Deductible ($1,000): -$22 = $460.52
- **Quoted monthly premium: ~$461/month**
