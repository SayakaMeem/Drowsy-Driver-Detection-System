import { getDatabase } from '../../../../lib/database';

export async function PUT(request, { params }) {
  try {
    const { sessionId } = params;
    const db = await getDatabase();
    
    const result = await db.run(
      'UPDATE detection_sessions SET end_time = CURRENT_TIMESTAMP WHERE session_id = ?',
      [sessionId]
    );
    
    if (result.changes > 0) {
      return Response.json({ 
        success: true, 
        message: 'Session ended successfully' 
      });
    } else {
      return Response.json({ 
        success: false, 
        error: 'Session not found' 
      }, { status: 404 });
    }
  } catch (error) {
    console.error('Error ending session:', error);
    return Response.json({ error: 'Failed to end session' }, { status: 500 });
  }
}
