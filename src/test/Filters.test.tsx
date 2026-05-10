import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
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
  it("should send search and age filters to the API", async () => {
    render(<App />);

    const fetchMock = vi.mocked(fetch);
    fetchMock.mockClear();

    const searchInput = screen.getByPlaceholderText(/Search shows/i);

    fireEvent.change(searchInput, { target: { value: "Bluey" } });

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(
        "/api/shows?q=Bluey&minAge=0.3&maxAge=2&limit=25&offset=0",
        expect.objectContaining({ signal: expect.any(AbortSignal) }),
      );
    });
  });
});
