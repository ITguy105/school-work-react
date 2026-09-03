import { COOKIE_NAME } from "@shared/const";
import { z } from "zod";
import { getSessionCookieOptions } from "./_core/cookies";
import { systemRouter } from "./_core/systemRouter";
import { publicProcedure, router } from "./_core/trpc";
import { createAssignment, deleteAssignment, listAssignments, toggleAssignment } from "./db";

export const appRouter = router({
    // if you need to use socket.io, read and register route in server/_core/index.ts, all api should start with '/api/' so that the gateway can route correctly
  system: systemRouter,
  auth: router({
    me: publicProcedure.query(opts => opts.ctx.user),
    logout: publicProcedure.mutation(({ ctx }) => {
      const cookieOptions = getSessionCookieOptions(ctx.req);
      ctx.res.clearCookie(COOKIE_NAME, { ...cookieOptions, maxAge: -1 });
      return {
        success: true,
      } as const;
    }),
  }),
  assignments: router({
    list: publicProcedure.query(() => listAssignments()),
    create: publicProcedure
      .input(z.object({
        subject: z.string().trim().min(1).max(80),
        title: z.string().trim().min(1).max(255),
        dueDate: z.string().min(1).max(32),
        priority: z.enum(["low", "medium", "high"]),
      }))
      .mutation(({ input }) => createAssignment({ ...input, completed: 0 })),
    toggle: publicProcedure.input(z.object({ id: z.number().int().positive() })).mutation(({ input }) => toggleAssignment(input.id)),
    remove: publicProcedure.input(z.object({ id: z.number().int().positive() })).mutation(({ input }) => deleteAssignment(input.id)),
  }),
});

export type AppRouter = typeof appRouter;
