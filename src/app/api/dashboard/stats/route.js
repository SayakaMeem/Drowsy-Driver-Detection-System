import { getDatabase } from '../../../lib/database';

export async function GET(request) {
  try {
    const { searchParams } = new URL(request.url);
    const sessionId = searchParams.get('sessionId');
    const timeRange = searchParams.get('timeRange') || '24h'; // 24h, 7d, 30d
    
    const db = await getDatabase();
    
    // Calculate time filter
    let timeFilter = '';
    let timeParams = [];
    
    switch (timeRange) {
      case '24h':
        timeFilter = "AND timestamp >= datetime('now', '-1 day')";
        break;
      case '7d':
        timeFilter = "AND timestamp >= datetime('now', '-7 days')";
        break;
      case '30d':
        timeFilter = "AND timestamp >= datetime('now', '-30 days')";
        break;
      default:
        timeFilter = "AND timestamp >= datetime('now', '-1 day')";
    }
    
    // Get overall statistics
    const statsQuery = `
      SELECT 
        COUNT(*) as total_detections,
        AVG(average_confidence) as avg_confidence,
        AVG(left_eye_confidence) as avg_left_eye,
        AVG(right_eye_confidence) as avg_right_eye,
        AVG(blink_rate) as avg_blink_rate,
        SUM(yawn_count) as total_yawns,
        COUNT(CASE WHEN average_confidence < 40 THEN 1 END) as drowsy_detections,
        COUNT(CASE WHEN average_confidence < 20 THEN 1 END) as very_drowsy_detections
      FROM detection_records 
      WHERE 1=1 ${sessionId ? 'AND session_id = ?' : ''} ${timeFilter}
    `;
    
    const statsParams = sessionId ? [sessionId] : [];
    const stats = await db.get(statsQuery, statsParams);
    
    // Get recent confidence trend (last 20 records)
    const trendQuery = `
      SELECT 
        timestamp,
        average_confidence,
        left_eye_confidence,
        right_eye_confidence
      FROM detection_records 
      WHERE 1=1 ${sessionId ? 'AND session_id = ?' : ''} ${timeFilter}
      ORDER BY timestamp DESC 
      LIMIT 20
    `;
    
    const trendParams = sessionId ? [sessionId] : [];
    const trend = await db.all(trendQuery, trendParams);
    
    // Get alertness level distribution
    const alertnessQuery = `
      SELECT 
        alertness_level,
        COUNT(*) as count
      FROM detection_records 
      WHERE 1=1 ${sessionId ? 'AND session_id = ?' : ''} ${timeFilter}
      GROUP BY alertness_level
      ORDER BY count DESC
    `;
    
    const alertnessParams = sessionId ? [sessionId] : [];
    const alertnessDistribution = await db.all(alertnessQuery, alertnessParams);
    
    // Get recent alerts
    const alertsQuery = `
      SELECT 
        timestamp,
        alert_type,
        message,
        severity,
        confidence_level
      FROM alerts 
      WHERE 1=1 ${sessionId ? 'AND session_id = ?' : ''} ${timeFilter}
      ORDER BY timestamp DESC 
      LIMIT 10
    `;
    
    const alertsParams = sessionId ? [sessionId] : [];
    const recentAlerts = await db.all(alertsQuery, alertsParams);
    
    return Response.json({
      stats,
      trend: trend.reverse(), // Reverse to show chronological order
      alertnessDistribution,
      recentAlerts
    });
  } catch (error) {
    console.error('Error fetching dashboard stats:', error);
    return Response.json({ error: 'Failed to fetch dashboard stats' }, { status: 500 });
  }
}
