# ShieldBase Home & Life Insurance — Quote Calculation Reference

## Purpose

This document describes the simplified formulas ShieldBase uses to generate home and life insurance quotes. Intended for internal use by quoting systems and AI assistants.

---

# HOME INSURANCE QUOTE FORMULA

## Base Rate by Coverage Tier

| Tier | Base Monthly Rate |
|---|---|
| Basic | $75 |
| Standard | $130 |
| Comprehensive | $210 |

---

## Rating Factors

### Property Type Factor

| Property Type | Multiplier |
|---|---|
| Single-family home | 1.00 (baseline) |
| Townhouse / semi-detached | 0.92 |
| Condo (unit only) | 0.75 |
| Mobile / manufactured home | 1.25 |

### Home Value Factor

Applied based on estimated rebuild value of the property.

| Rebuild Value | Multiplier |
|---|---|
| Under $200,000 | 0.80 |
| $200,000–$400,000 | 1.00 (baseline) |
| $400,001–$700,000 | 1.35 |
| $700,001–$1,000,000 | 1.70 |
| Over $1,000,000 | 2.20 |

### Location Risk Factor

| Risk Zone | Multiplier |
|---|---|
| Low risk (rural, low crime, no flood zone) | 0.88 |
| Moderate risk (suburban) | 1.00 (baseline) |
| High risk (urban, high crime, or coastal) | 1.30 |
| Very high risk (flood zone, wildfire zone) | 1.60 |

### Deductible Adjustment (Monthly)

| Deductible | Adjustment |
|---|---|
| $500 | +$20 |
| $1,000 | $0 (baseline) |
| $2,500 | -$15 |
| $5,000 | -$28 |

---

## Home Quote Formula

```
monthly_premium = base_rate
                  × property_type_factor
                  × home_value_factor
                  × location_risk_factor
                  + deductible_adjustment
```

Apply discounts after:
- New home (<10 years old): -12%
- Security system: -8%
- Claims-free (5 years): -10%
- Bundle: -15% to -20%

---

## Home Quote Example

**Profile:** Standard coverage, single-family home, $350,000 rebuild value, suburban location, $1,000 deductible

- Base rate: $130
- Property type (single-family): × 1.00
- Home value ($200K–$400K): × 1.00
- Location (suburban): × 1.00
- Deductible ($1,000): +$0
- **Quoted monthly premium: $130/month**

---

---

# LIFE INSURANCE QUOTE FORMULA

## Base Rate Table (Term Life, per $100,000 coverage, per month)

| Age | Non-Smoker | Smoker |
|---|---|---|
| 18–29 | $3.50 | $8.75 |
| 30–39 | $5.00 | $12.50 |
| 40–49 | $10.50 | $26.25 |
| 50–59 | $24.00 | $60.00 |
| 60–69 | $52.00 | $130.00 |

---

## Term Length Factor

| Term Length | Multiplier |
|---|---|
| 10 years | 0.80 |
| 15 years | 0.90 |
| 20 years | 1.00 (baseline) |
| 30 years | 1.35 |

## Health Status Factor

| Health Status | Multiplier |
|---|---|
| Excellent (no conditions) | 0.90 |
| Good (minor managed conditions) | 1.00 |
| Fair (chronic conditions, overweight) | 1.35 |
| Poor (multiple conditions, high BMI) | 1.75 |

---

## Life Quote Formula

```
monthly_premium = (coverage_amount / 100,000)
                  × base_rate_per_100k
                  × term_length_factor
                  × health_status_factor
```

---

## Life Quote Example

**Profile:** 35-year-old non-smoker, good health, $500,000 coverage, 20-year term

- Coverage units: 500,000 / 100,000 = 5 units
- Base rate (age 30–39, non-smoker): $5.00 per unit
- Base monthly: 5 × $5.00 = $25.00
- Term factor (20 years): × 1.00
- Health factor (good): × 1.00
- **Quoted monthly premium: $25.00/month**

---

**Profile:** 45-year-old smoker, fair health, $250,000 coverage, 10-year term

- Coverage units: 250,000 / 100,000 = 2.5 units
- Base rate (age 40–49, smoker): $26.25 per unit
- Base monthly: 2.5 × $26.25 = $65.63
- Term factor (10 years): × 0.80 = $52.50
- Health factor (fair): × 1.35 = $70.88
- **Quoted monthly premium: ~$70.88/month**
