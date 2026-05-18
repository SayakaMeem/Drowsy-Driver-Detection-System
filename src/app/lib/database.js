import sqlite3 from 'sqlite3';
import { open } from 'sqlite';
import path from 'path';

let db = null;

export async function getDatabase() {
  if (db) {
    return db;
  }

  // Create database in the project root
  const dbPath = path.join(process.cwd(), 'drowsiness_data.db');
  
  db = await open({
    filename: dbPath,
    driver: sqlite3.Database
  });

  // Create tables if they don't exist
  await db.exec(`
    CREATE TABLE IF NOT EXISTS detection_sessions (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      session_id TEXT NOT NULL,
      start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
      end_time DATETIME,
      total_detections INTEGER DEFAULT 0,
      alerts_triggered INTEGER DEFAULT 0
    )
  `);

  await db.exec(`
    CREATE TABLE IF NOT EXISTS detection_records (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      session_id TEXT NOT NULL,
      timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
      left_eye_confidence REAL NOT NULL,
      right_eye_confidence REAL NOT NULL,
      average_confidence REAL NOT NULL,
      alertness_level TEXT NOT NULL,
      blink_rate REAL,
      eye_closure_status TEXT,
      head_position TEXT,
      yawn_count INTEGER DEFAULT 0,
      eye_aspect_ratio REAL,
      mouth_aspect_ratio REAL,
      pupil_diameter REAL,
      eye_movement_status TEXT,
      face_detected BOOLEAN DEFAULT FALSE,
      model_used TEXT
    )
  `);

  await db.exec(`
    CREATE TABLE IF NOT EXISTS alerts (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      session_id TEXT NOT NULL,
      timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
      alert_type TEXT NOT NULL,
      confidence_level REAL NOT NULL,
      message TEXT NOT NULL,
      severity TEXT NOT NULL
    )
  `);

  return db;
}

export async function closeDatabase() {
  if (db) {
    await db.close();
    db = null;
  }
}
