import { getDatabase } from '../../lib/database';

export async function POST(request) {
  try {
    const data = await request.json();
    const db = await getDatabase();
    
    const result = await db.run(`
      INSERT INTO alerts (
        session_id,
        alert_type,
        confidence_level,
        message,
        severity
      ) VALUES (?, ?, ?, ?, ?)
    `, [
      data.sessionId,
      data.alertType,
      data.confidenceLevel,
      data.message,
      data.severity
    ]);
    
    // Update session alerts_triggered
    await db.run(
      'UPDATE detection_sessions SET alerts_triggered = alerts_triggered + 1 WHERE session_id = ?',
      [data.sessionId]
    );
    
    return Response.json({ 
      success: true, 
      alertId: result.lastID 
    });
  } catch (error) {
    console.error('Error storing alert:', error);
    return Response.json({ error: 'Failed to store alert' }, { status: 500 });
  }
}

export async function GET(request) {
  try {
    const { searchParams } = new URL(request.url);
    const sessionId = searchParams.get('sessionId');
    const limit = searchParams.get('limit') || 50;
    const offset = searchParams.get('offset') || 0;
    
    const db = await getDatabase();
    
    let query = `
      SELECT * FROM alerts 
      WHERE 1=1
    `;
    let params = [];
    
    if (sessionId) {
      query += ' AND session_id = ?';
      params.push(sessionId);
    }
    
    query += ' ORDER BY timestamp DESC LIMIT ? OFFSET ?';
    params.push(limit, offset);
    
    const alerts = await db.all(query, params);
    
    return Response.json({ alerts });
  } catch (error) {
    console.error('Error fetching alerts:', error);
    return Response.json({ error: 'Failed to fetch alerts' }, { status: 500 });
  }
}
