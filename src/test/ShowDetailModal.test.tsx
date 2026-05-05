import { afterEach, describe, it, expect, vi } from "vitest";
import { render, cleanup } from "@testing-library/react";
import React from "react";
import fs from "fs";
import path from "path";
import { ShowDetailModal } from "../components/ShowDetailModal";
import { Show } from "../types";

const modalShow: Show = {
  id: "frog-and-toad",
  title: "Frog and Toad",
  synopsis: "Two friends navigate quiet adventures together.",
  coverImage: "/cover.png",
  cast: ["Nat Faxon"],
  tags: ["Educational"],
  rating: "Safe",
  reasoning: "Gentle pacing and low-stakes conflict.",
  ageRecommendation: "2-8",
  minAge: 2,
  maxAge: 8,
  releaseYear: "2023-Present",
  runtime: "23 min",
  stimulationLevel: "Low",
};

afterEach(() => {
  cleanup();
  document.body.removeAttribute("style");
  vi.restoreAllMocks();
});

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

  it("should lock background scroll while open and restore it on close", () => {
    Object.defineProperty(window, "scrollY", {
      configurable: true,
      value: 320,
    });
    const scrollTo = vi.spyOn(window, "scrollTo").mockImplementation(() => {});

    const { unmount } = render(
      <ShowDetailModal show={modalShow} onClose={() => undefined} />,
    );

    expect(document.body.style.position).toBe("fixed");
    expect(document.body.style.top).toBe("-320px");
    expect(document.body.style.overflow).toBe("hidden");

    unmount();

    expect(document.body.style.position).toBe("");
    expect(document.body.style.top).toBe("");
    expect(document.body.style.overflow).toBe("");
    expect(scrollTo).toHaveBeenCalledWith(0, 320);
  });
});
