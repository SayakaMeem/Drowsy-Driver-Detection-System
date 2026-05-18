import { getDatabase } from '../../lib/database';

export async function POST(request) {
  try {
    const { sessionId } = await request.json();
    const db = await getDatabase();
    
    const result = await db.run(
      'INSERT INTO detection_sessions (session_id) VALUES (?)',
      [sessionId]
    );
    
    return Response.json({ 
      success: true, 
      sessionId,
      sessionId: result.lastID 
    });
  } catch (error) {
    console.error('Error creating session:', error);
    return Response.json({ error: 'Failed to create session' }, { status: 500 });
  }
}

export async function GET(request) {
  try {
    const { searchParams } = new URL(request.url);
    const limit = searchParams.get('limit') || 10;
    const offset = searchParams.get('offset') || 0;
    
    const db = await getDatabase();
    
    const sessions = await db.all(`
      SELECT 
        id,
        session_id,
        start_time,
        end_time,
        total_detections,
        alerts_triggered,
        CASE 
          WHEN end_time IS NULL THEN 
            ROUND((julianday('now') - julianday(start_time)) * 24 * 60, 2)
          ELSE 
            ROUND((julianday(end_time) - julianday(start_time)) * 24 * 60, 2)
        END as duration_minutes
      FROM detection_sessions 
      ORDER BY start_time DESC 
      LIMIT ? OFFSET ?
    `, [limit, offset]);
    
    return Response.json({ sessions });
  } catch (error) {
    console.error('Error fetching sessions:', error);
    return Response.json({ error: 'Failed to fetch sessions' }, { status: 500 });
  }
}
