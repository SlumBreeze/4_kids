import { describe, it, expect } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import fs from "fs";
import path from "path";
import App from "../App";
import React from "react";

describe("Filter Components Styles", () => {
  it("AgeFilter should use the primary utility color", () => {
    const cssPath = path.resolve(__dirname, "../components/AgeFilter.module.css");
    const cssContent = fs.readFileSync(cssPath, "utf-8");

    expect(cssContent).toContain("var(--color-primary-blue)");
  });
});

describe("Filter Visual Feedback", () => {
  it("should apply dimmed style when searching", () => {
    render(<App />);
    
    const searchInput = screen.getByPlaceholderText(/Search shows/i);
    
    fireEvent.change(searchInput, { target: { value: "Bluey" } });
    
    // Check the container of the filters
    const section = screen.getByText(/Best matches for tonight/i).closest("section");
    expect(section?.className).toContain("searching");
  });
});
