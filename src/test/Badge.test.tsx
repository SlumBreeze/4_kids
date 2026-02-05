import { describe, it, expect } from "vitest";
import fs from "fs";
import path from "path";

describe("Shared Badge Component Styles", () => {
  it("should have vibrant status color variables", () => {
    const cssPath = path.resolve(__dirname, "../../src/components/Badge.module.css");
    const cssContent = fs.readFileSync(cssPath, "utf-8");
    expect(cssContent).toContain("var(--color-safe)");
    expect(cssContent).toContain("var(--color-caution)");
    expect(cssContent).toContain("var(--color-unsafe)");
  });
});