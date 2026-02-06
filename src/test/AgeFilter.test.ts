import { describe, it, expect } from "vitest";
import { AGE_BUCKETS } from "../components/AgeFilter";

describe("Age Buckets Configuration", () => {
  it("should have exactly 4 specific buckets", () => {
    expect(AGE_BUCKETS.length).toBe(4);
  });

  it("should have 'Toddlers (3mo–2yr)' as the first bucket", () => {
    expect(AGE_BUCKETS[0].label).toBe("Toddlers (3mo–2yr)");
    expect(AGE_BUCKETS[0].min).toBe(0.3);
    expect(AGE_BUCKETS[0].max).toBe(2);
  });

  it("should have 'Preschoolers (3–5yr)' as the second bucket", () => {
    expect(AGE_BUCKETS[1].label).toBe("Preschoolers (3–5yr)");
    expect(AGE_BUCKETS[1].min).toBe(3);
    expect(AGE_BUCKETS[1].max).toBe(5);
  });

  it("should have 'School Age (6–9yr)' as the third bucket", () => {
    expect(AGE_BUCKETS[2].label).toBe("School Age (6–9yr)");
    expect(AGE_BUCKETS[2].min).toBe(6);
    expect(AGE_BUCKETS[2].max).toBe(9);
  });

  it("should have 'Pre-Teens (10–12yr)' as the fourth bucket", () => {
    expect(AGE_BUCKETS[3].label).toBe("Pre-Teens (10–12yr)");
    expect(AGE_BUCKETS[3].min).toBe(10);
    expect(AGE_BUCKETS[3].max).toBe(12);
  });

  it("should not contain 'All Ages'", () => {
    const hasAllAges = AGE_BUCKETS.some(b => b.label === "All Ages");
    expect(hasAllAges).toBe(false);
  });
});