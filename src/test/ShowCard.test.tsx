import { describe, it, expect } from "vitest";
import fs from "fs";
import path from "path";

describe("ShowCard Component Styles", () => {
  it("should use the large border radius variable", () => {
    const cssPath = path.resolve(__dirname, "../../src/components/ShowCard.module.css");
    const cssContent = fs.readFileSync(cssPath, "utf-8");

    expect(cssContent).toContain("border-radius: var(--border-radius-large)");
  });

  it("should use vibrant status colors or patterns", () => {
    const cssPath = path.resolve(__dirname, "../../src/components/ShowCard.module.css");
    const cssContent = fs.readFileSync(cssPath, "utf-8");

    // We want to see some vibrant status indicators
    expect(cssContent).toContain("var(--color-safe)");
    expect(cssContent).toContain("var(--color-caution)");
    expect(cssContent).toContain("var(--color-unsafe)");
  });
});
