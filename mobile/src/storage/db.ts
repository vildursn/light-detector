import * as SQLite from 'expo-sqlite';
import type { Detection } from '../analysis/types';

let db: SQLite.SQLiteDatabase | null = null;

async function getDb(): Promise<SQLite.SQLiteDatabase> {
  if (!db) {
    db = await SQLite.openDatabaseAsync('detections.db');
    await db.execAsync(`
      CREATE TABLE IF NOT EXISTS detections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp INTEGER NOT NULL,
        bearing REAL NOT NULL,
        color TEXT NOT NULL,
        confidence REAL NOT NULL
      );
    `);
  }
  return db;
}

export async function insertDetection(d: Detection): Promise<void> {
  const database = await getDb();
  await database.runAsync(
    'INSERT INTO detections (timestamp, bearing, color, confidence) VALUES (?, ?, ?, ?)',
    Date.now(),
    d.bearing,
    d.color,
    d.confidence,
  );
}

export interface DetectionRow {
  id: number;
  timestamp: number;
  bearing: number;
  color: string;
  confidence: number;
}

export async function queryRecent(limit = 100): Promise<DetectionRow[]> {
  const database = await getDb();
  return database.getAllAsync<DetectionRow>(
    'SELECT * FROM detections ORDER BY timestamp DESC LIMIT ?',
    limit,
  );
}

export async function clearAll(): Promise<void> {
  const database = await getDb();
  await database.runAsync('DELETE FROM detections');
}
