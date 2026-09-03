import { describe, expect, it } from "vitest";
import { appRouter } from "./routers";
import type { TrpcContext } from "./_core/context";

function createContext(): TrpcContext {
  return {
    user: null,
    req: {} as TrpcContext["req"],
    res: {} as TrpcContext["res"],
  };
}

describe("assignments router", () => {
  it("rejects an assignment without a subject or title", async () => {
    const caller = appRouter.createCaller(createContext());

    await expect(caller.assignments.create({
      subject: "",
      title: "",
      dueDate: "2026-09-12",
      priority: "medium",
    })).rejects.toThrow();
  });

  it("rejects invalid assignment IDs", async () => {
    const caller = appRouter.createCaller(createContext());

    await expect(caller.assignments.toggle({ id: 0 })).rejects.toThrow();
    await expect(caller.assignments.remove({ id: -1 })).rejects.toThrow();
  });
});
