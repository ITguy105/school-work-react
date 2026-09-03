import { desc, eq } from "drizzle-orm";
import { drizzle } from "drizzle-orm/mysql2";
import { assignments, Assignment, InsertAssignment, InsertUser, users } from "../drizzle/schema";
import { ENV } from './_core/env';

let _db: ReturnType<typeof drizzle> | null = null;

// Lazily create the drizzle instance so local tooling can run without a DB.
export async function getDb() {
  if (!_db && process.env.DATABASE_URL) {
    try {
      _db = drizzle(process.env.DATABASE_URL);
    } catch (error) {
      console.warn("[Database] Failed to connect:", error);
      _db = null;
    }
  }
  return _db;
}

export async function upsertUser(user: InsertUser): Promise<void> {
  if (!user.openId) {
    throw new Error("User openId is required for upsert");
  }

  const db = await getDb();
  if (!db) {
    console.warn("[Database] Cannot upsert user: database not available");
    return;
  }

  try {
    const values: InsertUser = {
      openId: user.openId,
    };
    const updateSet: Record<string, unknown> = {};

    const textFields = ["name", "email", "loginMethod"] as const;
    type TextField = (typeof textFields)[number];

    const assignNullable = (field: TextField) => {
      const value = user[field];
      if (value === undefined) return;
      const normalized = value ?? null;
      values[field] = normalized;
      updateSet[field] = normalized;
    };

    textFields.forEach(assignNullable);

    if (user.lastSignedIn !== undefined) {
      values.lastSignedIn = user.lastSignedIn;
      updateSet.lastSignedIn = user.lastSignedIn;
    }
    if (user.role !== undefined) {
      values.role = user.role;
      updateSet.role = user.role;
    } else if (user.openId === ENV.ownerOpenId) {
      values.role = 'admin';
      updateSet.role = 'admin';
    }

    if (!values.lastSignedIn) {
      values.lastSignedIn = new Date();
    }

    if (Object.keys(updateSet).length === 0) {
      updateSet.lastSignedIn = new Date();
    }

    await db.insert(users).values(values).onDuplicateKeyUpdate({
      set: updateSet,
    });
  } catch (error) {
    console.error("[Database] Failed to upsert user:", error);
    throw error;
  }
}

export async function getUserByOpenId(openId: string) {
  const db = await getDb();
  if (!db) {
    console.warn("[Database] Cannot get user: database not available");
    return undefined;
  }

  const result = await db.select().from(users).where(eq(users.openId, openId)).limit(1);

  return result.length > 0 ? result[0] : undefined;
}

const seedAssignments: InsertAssignment[] = [
  { subject: "Literature", title: "The Odyssey reflection", dueDate: "2026-09-05", priority: "high", completed: 0 },
  { subject: "Physics", title: "Motion lab report", dueDate: "2026-09-06", priority: "medium", completed: 0 },
  { subject: "French", title: "Verb conjugation practice", dueDate: "2026-09-08", priority: "low", completed: 1 },
  { subject: "World History", title: "Industrial Revolution slides", dueDate: "2026-09-10", priority: "medium", completed: 0 },
];

export async function listAssignments(): Promise<Assignment[]> {
  const db = await getDb();
  if (!db) return seedAssignments.map((item, index) => ({ ...item, id: index + 1, createdAt: new Date() })) as Assignment[];

  let result = await db.select().from(assignments).orderBy(desc(assignments.dueDate), desc(assignments.id));
  if (result.length === 0) {
    await db.insert(assignments).values(seedAssignments);
    result = await db.select().from(assignments).orderBy(desc(assignments.dueDate), desc(assignments.id));
  }
  return result;
}

export async function createAssignment(input: InsertAssignment) {
  const db = await getDb();
  if (!db) return { ...input, id: Date.now(), createdAt: new Date() } as Assignment;
  const result = await db.insert(assignments).values(input);
  const created = await db.select().from(assignments).where(eq(assignments.id, result[0].insertId)).limit(1);
  return created[0];
}

export async function toggleAssignment(id: number) {
  const db = await getDb();
  if (!db) return true;
  const current = await db.select().from(assignments).where(eq(assignments.id, id)).limit(1);
  if (!current[0]) return false;
  await db.update(assignments).set({ completed: current[0].completed ? 0 : 1 }).where(eq(assignments.id, id));
  return true;
}

export async function deleteAssignment(id: number) {
  const db = await getDb();
  if (!db) return true;
  await db.delete(assignments).where(eq(assignments.id, id));
  return true;
}
