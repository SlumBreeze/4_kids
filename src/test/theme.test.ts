import { describe, it, expect } from "vitest";
import fs from "fs";
import path from "path";

describe("Theme Variables", () => {
  it("should have the correct color and border-radius variables in index.css", () => {
    const cssPath = path.resolve(__dirname, "../../src/index.css");
    const cssContent = fs.readFileSync(cssPath, "utf-8");

    // Primary Colors
    expect(cssContent).toContain("--color-primary-yellow");
    expect(cssContent).toContain("--color-primary-blue");
    expect(cssContent).toContain("--color-primary-purple");
    
    // Status Colors
    expect(cssContent).toContain("--color-safe");
    expect(cssContent).toContain("--color-caution");
    expect(cssContent).toContain("--color-unsafe");

    // Border Radius
    expect(cssContent).toContain("--border-radius-large");
    expect(cssContent).toMatch(/--border-radius-large:\s*8px/);

    // Typography
    expect(cssContent).toMatch(/font-family:\s*Inter/);
  });
});
