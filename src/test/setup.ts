import "@testing-library/jest-dom";
import { vi } from "vitest";

globalThis.fetch = vi.fn(
  () => new Promise<Response>(() => undefined),
) as unknown as typeof fetch;
