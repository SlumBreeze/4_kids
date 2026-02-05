import { describe, it, expect } from "vitest";
import { AGE_BUCKETS } from "../components/AgeFilter";

describe("Age Buckets Configuration", () => {
  it("should have 'Toddlers (3mo–2yr)' as the first bucket", () => {
    expect(AGE_BUCKETS[0].label).toBe("Toddlers (3mo–2yr)");
    expect(AGE_BUCKETS[0].min).toBe(0.3);
    expect(AGE_BUCKETS[0].max).toBe(2);
  });
});
