# UniThrive Prototype

A fully working FastAPI backend for the UniThrive student wellbeing platform, featuring AI-powered support through the **3 Rings of Well-Being**: Mental, Psychological, and Physical.

## Features

### Core Features
- **AI Counselling Assistant** - Empathetic chatbot with risk detection for early intervention
- **AI Time Management Assistant** - Smart scheduling, exam planning, and productivity optimization
- **3-Ring Wellbeing Dashboard** - Track Mental, Psychological, and Physical health scores

### 3 Ring Submodules

#### Mental Ring
- Course engagement tracking (attendance, assignments, participation)
- Workshop and seminar attendance
- Skill development monitoring (languages, coding, design, research)
- Academic project tracking
- Learning goal setting

#### Psychological Ring
- MBTI personality assessments
- Self-discovery tests and reflection tools
- Behavioral risk analysis and profiling
- Learning pattern insights
- Neurocognitive testing (memory, reaction time, attention)
- Long-term health metrics tracking

#### Physical Ring
- Time management behavior tracking
- Daily activity monitoring (steps, active minutes, sedentary time)
- Sleep tracking (hours, quality, REM/deep sleep stages)
- Fitness routines and exercise sessions
- Wearable device integration (smartwatches, fitness trackers)

### Additional Features
- Daily check-ins (mood, stress, sleep, exercise, social)
- Weekly summaries with spotlight opportunities
- Achievement badges (Balance Seeker, Stress Fighter, Scholar, etc.)
- Risk alerts with counselor escalation
- Personalized recommendations using multi-perspective scoring

## Architecture

```
unithrive-prototype/
├── app/
│   ├── main.py              # FastAPI entry point
│   ├── config.py            # Configuration settings
│   ├── routers/             # API endpoints
│   │   ├── auth.py
│   │   ├── checkins.py
│   │   ├── dashboard.py
│   │   ├── ai_assistant.py
│   │   ├── wellbeing_rings.py
│   │   ├── mental_ring.py
│   │   ├── psychological_ring.py
│   │   └── physical_ring.py
│   ├── schemas/             # Pydantic models
│   ├── services/            # Business logic
│   ├── storage/             # JSON persistence layer
│   └── decision_engine/      # Feature extraction, perspectives, ranking
├── data/                    # JSON data files
├── batch_job.py            # Weekly processing script
├── seed_data.py            # Sample data generator
├── run.bat                 # Windows startup script
└── requirements.txt        # Python dependencies
```

## Quick Start

### Prerequisites
- Python 3.11 or higher
- Windows (or adapt run.bat for your OS)

### Installation

1. **Clone or extract the project** to your desired location

2. **Run the startup script**:
   ```cmd
   run.bat
   ```

   This will:
   - Create a virtual environment
   - Install dependencies
   - Start the FastAPI server

3. **Access the API**:
   - API Root: http://localhost:8000
   - Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

### Generate Sample Data

To populate the system with sample data for 3 student personas:

```bash
python seed_data.py
```

This creates:
- **Maya**: Business + Psych student with exam week stress pattern
- **Shadow**: Physics + Green Energy student with high mental but low physical
- **Adrian**: CS/Fintech student with high social activity but mood fluctuations

### Run Batch Processing

To calculate ring scores, generate summaries, and create recommendations:

```bash
python batch_job.py
```

Or for a specific user:
```bash
python batch_job.py --user-id <user_id>
```

## API Endpoints

### Authentication
- `POST /api/auth/mock-login` - Anonymous or email-based login
- `GET /api/auth/users/{user_id}` - Get user by ID

### Check-ins
- `POST /api/checkins/` - Submit daily check-in
- `GET /api/checkins/{user_id}` - Get check-in history
- `GET /api/checkins/{user_id}/streak` - Get check-in streak
- `POST /api/checkins/activities` - Log activity

### Dashboard
- `GET /api/dashboard/{user_id}` - Complete dashboard data
- `GET /api/dashboard/{user_id}/weekly-highlight` - Weekly spotlight
- `GET /api/dashboard/{user_id}/quick-stats` - Quick statistics

### Wellbeing Rings
- `GET /api/rings/{user_id}/today` - Today's ring scores
- `GET /api/rings/{user_id}/history` - Ring score history
- `GET /api/rings/{user_id}/badge` - Achievement badge

### AI Assistants
- `POST /api/ai/counselling/chat` - Chat with AI Counselling Assistant
- `GET /api/ai/counselling/sessions/{user_id}` - Chat history
- `POST /api/ai/timemanagement/plan` - Generate study/exam schedule
- `GET /api/ai/timemanagement/suggestions/{user_id}` - Time management tips

### Mental Ring
- `POST /api/mental-ring/courses` - Log course engagement
- `GET /api/mental-ring/courses/{user_id}` - Get courses
- `POST /api/mental-ring/skills` - Add skill development
- `GET /api/mental-ring/skills/{user_id}` - Get skills
- `GET /api/mental-ring/summary/{user_id}` - Mental ring summary

### Psychological Ring
- `POST /api/psychological-ring/personality` - Submit MBTI assessment
- `GET /api/psychological-ring/personality/{user_id}` - Get personality
- `POST /api/psychological-ring/neurocognitive` - Submit test results
- `GET /api/psychological-ring/summary/{user_id}` - Psychological ring summary

### Physical Ring
- `POST /api/physical-ring/sleep` - Log sleep data
- `GET /api/physical-ring/sleep/{user_id}` - Get sleep records
- `POST /api/physical-ring/activity` - Record daily activity
- `POST /api/physical-ring/exercise` - Log exercise session
- `GET /api/physical-ring/summary/{user_id}` - Physical ring summary

## Data Storage

This prototype uses **JSON file storage** for simplicity:
- All data stored in the `data/` directory
- Easily upgradeable to SQLite or PostgreSQL
- Storage layer abstracted for easy migration

## 3 Rings Scoring

### Mental Ring (0-1 scale)
- Course Engagement: 40%
- Skill Development: 30%
- Workshop Attendance: 15%
- Project Participation: 15%

### Psychological Ring (0-1 scale)
- Emotional Stability: 30%
- Self-Awareness: 30%
- Cognitive Health: 20%
- Risk Mitigation: 20%

### Physical Ring (0-1 scale)
- Time Management: 25%
- Activity Level: 25%
- Sleep Quality: 25%
- Fitness: 25%

## Risk Detection

The system monitors for:
- Sustained high stress (≥4 for 3+ days)
- Declining mood trends
- Sleep deprivation (<5 hours for 3+ days)
- Social withdrawal (0 interactions for 5+ days)
- High-risk language patterns in chat

## Development

### Project Structure

All code follows Python best practices:
- Type hints throughout
- Pydantic for data validation
- Async/await for concurrency
- Comprehensive docstrings
- Modular architecture

### Adding New Features

1. Define Pydantic schemas in `app/schemas/`
2. Add storage layer methods in `app/storage/`
3. Implement business logic in `app/services/`
4. Create API endpoints in `app/routers/`
5. Register router in `app/main.py`

### Testing

Run the server and explore the API documentation at:
http://localhost:8000/docs

Use the interactive Swagger UI to test endpoints directly.

## Next Steps for Production

To prepare for production deployment:

1. **Replace JSON storage** with PostgreSQL or SQLite
   - Implement `app/storage/db_storage.py`
   - Keep same interface as base storage

2. **Add authentication**
   - Implement JWT or OAuth2
   - Add password hashing with bcrypt

3. **Integrate real AI**
   - Replace rule-based counselling with LLM API
   - Add NLP for risk detection in text

4. **Add tests**
   - Unit tests for services
   - Integration tests for API
   - Load testing with Locust

5. **Deploy**
   - Docker containerization
   - Cloud deployment (AWS/GCP/Azure)
   - CI/CD pipeline

## License

This is a prototype for demonstration purposes.

## Support

For questions or issues:
- Check the API documentation at `/docs`
- Review the schemas for request/response formats
- Examine the services for business logic

---

**UniThrive** - Supporting student wellbeing through AI-powered insights and evidence-based interventions.
# Unitrhive-demo-3-12
