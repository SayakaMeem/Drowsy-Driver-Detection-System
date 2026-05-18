# Drowsiness Detection Dashboard

This project now includes a comprehensive dashboard for monitoring drowsiness detection performance and storing all detection data in a SQLite database.

## Features

### Dashboard Components
- **Real-time Analytics**: View confidence scores, blink rates, and other metrics
- **Session Management**: Track individual detection sessions
- **Historical Data**: Analyze trends over time (24h, 7d, 30d)
- **Alert Tracking**: Monitor drowsiness alerts and their severity
- **Eye Confidence Details**: Separate tracking for left and right eye confidence

### Database Schema

#### Detection Sessions
- Session ID and timestamps
- Total detections and alerts triggered
- Session duration

#### Detection Records
- Left and right eye confidence scores
- Average confidence and alertness level
- Blink rate, eye closure status, head position
- Yawn count, eye aspect ratio, mouth aspect ratio
- Pupil diameter, eye movement status
- Face detection status and model used

#### Alerts
- Alert type and severity
- Confidence level and message
- Timestamp and session association

## API Endpoints

### Sessions
- `POST /api/sessions` - Create new session
- `GET /api/sessions` - List sessions with pagination
- `PUT /api/sessions/[sessionId]/end` - End a session

### Records
- `POST /api/records` - Store detection record
- `GET /api/records` - Retrieve records with filtering

### Alerts
- `POST /api/alerts` - Store alert
- `GET /api/alerts` - Retrieve alerts with filtering

### Dashboard Stats
- `GET /api/dashboard/stats` - Get aggregated statistics and trends

## Usage

1. **Start Detection**: Click "Start Detecting" on the main page
2. **View Dashboard**: Click "Dashboard" button to access analytics
3. **Session Selection**: Choose specific sessions or view combined data
4. **Time Range**: Filter data by 24h, 7d, or 30d periods

## Charts and Visualizations

- **Confidence Trend**: Line chart showing confidence over time
- **Alertness Distribution**: Doughnut chart of alertness levels
- **Key Metrics**: Cards showing averages and totals
- **Recent Alerts**: List of recent drowsiness alerts

## Database Location

The SQLite database is stored as `drowsiness_data.db` in the project root directory.

## Dependencies

- `sqlite3` - Database operations
- `chart.js` & `react-chartjs-2` - Chart visualizations
- `date-fns` - Date formatting and manipulation

## Data Flow

1. **Detection Start**: Creates new session in database
2. **Frame Processing**: Stores each detection record
3. **Alert Triggering**: Stores alerts when drowsiness detected
4. **Session End**: Updates session end time
5. **Dashboard Display**: Retrieves and visualizes stored data

## Future Enhancements

- Export functionality for data analysis
- Advanced filtering and search
- Real-time dashboard updates
- Performance optimization for large datasets
- User authentication and session management
