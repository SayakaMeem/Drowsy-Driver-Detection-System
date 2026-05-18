import { getDatabase } from '../../lib/database';

export async function POST(request) {
  try {
    const data = await request.json();
    const db = await getDatabase();
    
    const result = await db.run(`
      INSERT INTO detection_records (
        session_id,
        left_eye_confidence,
        right_eye_confidence,
        average_confidence,
        alertness_level,
        blink_rate,
        eye_closure_status,
        head_position,
        yawn_count,
        eye_aspect_ratio,
        mouth_aspect_ratio,
        pupil_diameter,
        eye_movement_status,
        face_detected,
        model_used
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `, [
      data.sessionId,
      data.leftEyeConfidence,
      data.rightEyeConfidence,
      data.averageConfidence,
      data.alertnessLevel,
      data.blinkRate,
      data.eyeClosureStatus,
      data.headPosition,
      data.yawnCount,
      data.eyeAspectRatio,
      data.mouthAspectRatio,
      data.pupilDiameter,
      data.eyeMovementStatus,
      data.faceDetected ? 1 : 0,
      data.modelUsed
    ]);
    
    // Update session total_detections
    await db.run(
      'UPDATE detection_sessions SET total_detections = total_detections + 1 WHERE session_id = ?',
      [data.sessionId]
    );
    
    return Response.json({ 
      success: true, 
      recordId: result.lastID 
    });
  } catch (error) {
    console.error('Error storing record:', error);
    return Response.json({ error: 'Failed to store record' }, { status: 500 });
  }
}

export async function GET(request) {
  try {
    const { searchParams } = new URL(request.url);
    const sessionId = searchParams.get('sessionId');
    const limit = searchParams.get('limit') || 100;
    const offset = searchParams.get('offset') || 0;
    
    const db = await getDatabase();
    
    let query = `
      SELECT * FROM detection_records 
      WHERE 1=1
    `;
    let params = [];
    
    if (sessionId) {
      query += ' AND session_id = ?';
      params.push(sessionId);
    }
    
    query += ' ORDER BY timestamp DESC LIMIT ? OFFSET ?';
    params.push(limit, offset);
    
    const records = await db.all(query, params);
    
    return Response.json({ records });
  } catch (error) {
    console.error('Error fetching records:', error);
    return Response.json({ error: 'Failed to fetch records' }, { status: 500 });
  }
}
