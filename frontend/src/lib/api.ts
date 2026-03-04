import type { ApiGroup } from "../types";
import { requestJson } from "./http";

export const demoUserId = "demo-user-001";

export const apiGroups: ApiGroup[] = [
  {
    key: "platform",
    title: "Core Platform",
    description: "Core connectivity checks via existing backend routes.",
    endpoints: [
      { label: "List Users (connectivity)", method: "GET", path: "/api/auth/users?limit=1&offset=0" },
      { label: "Dashboard Quick Stats", method: "GET", path: `/api/dashboard/${demoUserId}/quick-stats` }
    ]
  },
  {
    key: "auth",
    title: "auth.py",
    description: "Mock login, logout, and user retrieval.",
    endpoints: [
      {
        label: "Mock Login",
        method: "POST",
        path: "/api/auth/mock-login",
        sampleBody: {
          email: "demo@unithrive.ai",
          display_name: "Demo Student",
          anonymous: false
        }
      },
      {
        label: "Logout",
        method: "POST",
        path: `/api/auth/logout?user_id=${demoUserId}`
      },
      { label: "Get User", method: "GET", path: `/api/auth/users/${demoUserId}` },
      { label: "List Users", method: "GET", path: "/api/auth/users?limit=10&offset=0" }
    ]
  },
  {
    key: "checkins",
    title: "checkins.py",
    description: "Daily check-ins, activities, streaks, and summaries.",
    endpoints: [
      {
        label: "Create Check-In",
        method: "POST",
        path: "/api/checkins/",
        sampleBody: {
          user_id: demoUserId,
          mood_score: 4,
          stress_score: 2,
          sleep_hours: 7.5,
          exercise_minutes: 35,
          social_interactions: 3,
          notes_text: "Feeling focused today."
        }
      },
      { label: "History", method: "GET", path: `/api/checkins/${demoUserId}?days=30` },
      { label: "Today", method: "GET", path: `/api/checkins/${demoUserId}/today` },
      { label: "Streak", method: "GET", path: `/api/checkins/${demoUserId}/streak` },
      {
        label: "Create Activity",
        method: "POST",
        path: "/api/checkins/activities",
        sampleBody: {
          user_id: demoUserId,
          type: "exercise",
          duration_minutes: 45,
          tag_ring: "physical",
          date: "2026-03-04",
          title: "Cardio Session",
          description: "Treadmill + stretching"
        }
      },
      { label: "Activity History", method: "GET", path: `/api/checkins/activities/${demoUserId}?days=14` },
      { label: "Today Summary", method: "GET", path: `/api/checkins/${demoUserId}/summary/today` }
    ]
  },
  {
    key: "dashboard",
    title: "dashboard.py",
    description: "Main dashboard and recommendation summary endpoints.",
    endpoints: [
      { label: "Dashboard", method: "GET", path: `/api/dashboard/${demoUserId}` },
      { label: "Summary", method: "GET", path: `/api/dashboard/${demoUserId}/summary` },
      { label: "Weekly Highlight", method: "GET", path: `/api/dashboard/${demoUserId}/weekly-highlight` },
      { label: "Quick Stats", method: "GET", path: `/api/dashboard/${demoUserId}/quick-stats` },
      { label: "Alerts", method: "GET", path: `/api/dashboard/${demoUserId}/alerts` },
      { label: "Recommendations", method: "GET", path: `/api/dashboard/${demoUserId}/recommendations?limit=5` },
      { label: "Weekly Summary", method: "GET", path: `/api/dashboard/${demoUserId}/weekly-summary` }
    ]
  },
  {
    key: "ai_assistant",
    title: "ai_assistant.py",
    description: "Counselling chat and time management assistant APIs.",
    endpoints: [
      {
        label: "Counselling Chat",
        method: "POST",
        path: "/api/ai/counselling/chat",
        sampleBody: {
          user_id: demoUserId,
          message: "I feel overwhelmed with deadlines this week."
        }
      },
      { label: "Session List", method: "GET", path: `/api/ai/counselling/sessions/${demoUserId}?limit=5` },
      {
        label: "Generate Time Plan",
        method: "POST",
        path: "/api/ai/timemanagement/plan",
        sampleBody: {
          user_id: demoUserId,
          upcoming_exams: [
            {
              exam_name: "Math Midterm",
              exam_date: "2026-03-20",
              subject: "Mathematics",
              priority: 5,
              preparation_start_date: "2026-03-06",
              recommended_daily_study_hours: 2.5
            },
            {
              exam_name: "Biology Quiz",
              exam_date: "2026-03-24",
              subject: "Biology",
              priority: 4,
              preparation_start_date: "2026-03-08",
              recommended_daily_study_hours: 2
            }
          ],
          preferred_study_hours_per_day: 3,
          preferred_productive_times: ["morning", "afternoon"],
          constraints: ["Class from 9am to 2pm"]
        }
      },
      {
        label: "Optimize Schedule",
        method: "POST",
        path: "/api/ai/timemanagement/optimize",
        sampleBody: {
          user_id: demoUserId,
          current_plan_id: "plan-demo-1",
          issues: ["low focus after 8pm", "too little revision time"],
          goals: ["improve retention", "sleep before 11pm"]
        }
      },
      { label: "Suggestions", method: "GET", path: `/api/ai/timemanagement/suggestions/${demoUserId}` },
      { label: "General Tips", method: "GET", path: `/api/ai/timemanagement/tips/${demoUserId}` }
    ]
  },
  {
    key: "wellbeing_rings",
    title: "wellbeing_rings.py",
    description: "Cross-ring scoring, trends, and weekly summaries.",
    endpoints: [
      { label: "Today Rings", method: "GET", path: `/api/rings/${demoUserId}/today` },
      { label: "Ring History", method: "GET", path: `/api/rings/${demoUserId}/history?days=30` },
      { label: "Calculate Scores", method: "GET", path: `/api/rings/${demoUserId}/scores` },
      { label: "Calculate and Store", method: "POST", path: `/api/rings/${demoUserId}/calculate` },
      { label: "Weekly Summary", method: "GET", path: `/api/rings/${demoUserId}/weekly-summary` },
      { label: "All Weekly Summaries", method: "GET", path: `/api/rings/${demoUserId}/weekly-summary/all?limit=5` },
      { label: "Achievement Badge", method: "GET", path: `/api/rings/${demoUserId}/badge` },
      { label: "Trends", method: "GET", path: `/api/rings/trends/${demoUserId}?period_days=7` }
    ]
  },
  {
    key: "mental_ring",
    title: "mental_ring.py",
    description: "Course, workshops, skills, projects, goals and summary.",
    endpoints: [
      {
        label: "Create Course Engagement",
        method: "POST",
        path: "/api/mental-ring/courses",
        sampleBody: {
          user_id: demoUserId,
          course_id: "course-data-sci-101",
          course_name: "Data Science Foundations",
          attendance_rate: 0.9,
          assignment_completion: 0.8,
          participation_score: 0.85
        }
      },
      { label: "Get Courses", method: "GET", path: `/api/mental-ring/courses/${demoUserId}` },
      { label: "Get Workshops", method: "GET", path: `/api/mental-ring/workshops/${demoUserId}` },
      { label: "Get Skills", method: "GET", path: `/api/mental-ring/skills/${demoUserId}` },
      { label: "Get Projects", method: "GET", path: `/api/mental-ring/projects/${demoUserId}` },
      { label: "Get Goals", method: "GET", path: `/api/mental-ring/goals/${demoUserId}` },
      { label: "Summary", method: "GET", path: `/api/mental-ring/summary/${demoUserId}` }
    ]
  },
  {
    key: "psychological_ring",
    title: "psychological_ring.py",
    description: "Personality, self-discovery, risk profile and alerts.",
    endpoints: [
      {
        label: "Submit Personality",
        method: "POST",
        path: "/api/psychological-ring/personality",
        sampleBody: {
          user_id: demoUserId,
          assessment_type: "big_five",
          results: {
            openness: 0.78,
            conscientiousness: 0.72,
            extraversion: 0.49,
            agreeableness: 0.81,
            neuroticism: 0.31
          }
        }
      },
      { label: "Get Personality", method: "GET", path: `/api/psychological-ring/personality/${demoUserId}` },
      {
        label: "Trigger Risk Analysis",
        method: "POST",
        path: "/api/psychological-ring/risk-analysis",
        sampleBody: {
          user_id: demoUserId,
          analysis_period_days: 14
        }
      },
      { label: "Risk Profile", method: "GET", path: `/api/psychological-ring/risk-profile/${demoUserId}` },
      { label: "Alerts", method: "GET", path: `/api/psychological-ring/alerts/${demoUserId}` },
      { label: "Summary", method: "GET", path: `/api/psychological-ring/summary/${demoUserId}` }
    ]
  },
  {
    key: "physical_ring",
    title: "physical_ring.py",
    description: "Time management, activity, sleep, fitness and wearables.",
    endpoints: [
      {
        label: "Log Time Management",
        method: "POST",
        path: "/api/physical-ring/time-management",
        sampleBody: {
          user_id: demoUserId,
          date: "2026-03-04",
          schedule_adherence: 0.82,
          productive_hours: 5.5,
          procrastination_instances: 1,
          tasks_completed: 6,
          tasks_planned: 8
        }
      },
      { label: "Get Time Management", method: "GET", path: `/api/physical-ring/time-management/${demoUserId}?days=30` },
      { label: "Get Activity", method: "GET", path: `/api/physical-ring/activity/${demoUserId}?days=30` },
      { label: "Get Sleep", method: "GET", path: `/api/physical-ring/sleep/${demoUserId}?days=30` },
      { label: "Get Fitness", method: "GET", path: `/api/physical-ring/fitness/${demoUserId}` },
      { label: "Get Exercise", method: "GET", path: `/api/physical-ring/exercise/${demoUserId}?days=14` },
      { label: "Connected Wearables", method: "GET", path: `/api/physical-ring/wearables/${demoUserId}` },
      { label: "Wearable Data", method: "GET", path: `/api/physical-ring/wearable-data/${demoUserId}?days=7` },
      { label: "Summary", method: "GET", path: `/api/physical-ring/summary/${demoUserId}` }
    ]
  }
];

export async function callEndpoint(
  method: "GET" | "POST",
  path: string,
  body?: Record<string, unknown>
): Promise<unknown> {
  return requestJson(path, method, body);
}
