import { describe, it, expect } from "vitest";
import fs from "fs";
import path from "path";

describe("ShowDetailModal Component Styles", () => {
  it("should use the large border radius variable for the modal and cover image", () => {
    const cssPath = path.resolve(__dirname, "../../src/components/ShowDetailModal.module.css");
    const cssContent = fs.readFileSync(cssPath, "utf-8");

    expect(cssContent).toContain("border-radius: var(--border-radius-large)");
  });

  it("should have a white background for the modal content areas", () => {
    const cssPath = path.resolve(__dirname, "../../src/components/ShowDetailModal.module.css");
    const cssContent = fs.readFileSync(cssPath, "utf-8");

    expect(cssContent).toContain("background: white");
  });
});
