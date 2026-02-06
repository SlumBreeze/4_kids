import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import App from "../App";
import React from "react";

describe("App Component Defaults", () => {
  it("should initialize with 'Toddlers (3mo–2yr)' selected", () => {
    render(<App />);
    const activeFilter = screen.getByText("Toddlers (3mo–2yr)");
    // The filter has the 'active' class when selected.
    // Based on AgeFilter.tsx: className={`${styles.pill} ${selectedLabel === bucket.label ? styles.active : ""}`}
    expect(activeFilter.className).toContain("active");
  });

  it("should not show 'All Ages' filter", () => {
    render(<App />);
    const allAgesFilter = screen.queryByText("All Ages");
    expect(allAgesFilter).toBeNull();
  });
});
