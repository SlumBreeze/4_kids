import { describe, it, expect } from "vitest";
import fs from "fs";
import path from "path";

describe("Filter Components Styles", () => {
  it("AgeFilter should use vibrant colors and rounded edges", () => {
    const cssPath = path.resolve(__dirname, "../../src/components/AgeFilter.module.css");
    const cssContent = fs.readFileSync(cssPath, "utf-8");

    expect(cssContent).toContain("var(--color-primary-blue)");
    expect(cssContent).toContain("border-radius: var(--border-radius-large)");
  });

  it("StimulationFilter should use vibrant colors and rounded edges", () => {
    const cssPath = path.resolve(__dirname, "../../src/components/StimulationFilter.module.css");
    const cssContent = fs.readFileSync(cssPath, "utf-8");

    expect(cssContent).toContain("var(--color-primary-blue)");
    expect(cssContent).toContain("border-radius: var(--border-radius-large)");
  });
});
