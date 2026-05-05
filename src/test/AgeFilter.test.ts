import { describe, it, expect } from "vitest";
import { AGE_BUCKETS } from "../components/AgeFilter";

describe("Age Buckets Configuration", () => {
  it("should have exactly 2 specific buckets", () => {
    expect(AGE_BUCKETS.length).toBe(2);
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

  it("should not contain 'All Ages'", () => {
    const hasAllAges = AGE_BUCKETS.some(b => b.label === "All Ages");
    expect(hasAllAges).toBe(false);
  });

  it("should not contain age buckets above 5 years", () => {
    const hasOlderBuckets = AGE_BUCKETS.some(b => b.min >= 6 || b.max > 5);
    expect(hasOlderBuckets).toBe(false);
  });
});
