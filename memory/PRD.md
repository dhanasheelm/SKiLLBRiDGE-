# SKILLBRIDGE — PRD

## Vision
AI-powered opportunity platform connecting students & skilled professionals to fitting roles.

## Personas
- Student: seeks internships/hackathons/research
- Professional: seeks freelance/full-time/collab

## Implemented (Feb 2026)
- Role-based landing (Student/Professional)
- Auth (login/signup) with pathname-derived signup mode
- Forgot password modal (dialog + confirmation)
- Multi-step onboarding — editable fields, skills, interests persist
- Authenticated Home with skill match + My Applications strip
- Dashboard with stat cards + skill breakdown
- Opportunities list + filters + search
- Opportunity detail with save (persists via /api/saved/toggle)
- Multi-step Apply flow (Steps 1-4 with data-testids, Back/Next, success screen)
- My Applications list (updates after submit)
- Profile page + Edit Profile modal (persists via /api/users)
- Professional Workspace + tune profile modal
- Notifications with mark-all-read (persists via /api/notifications/:email/read)
- Skill Match analysis page + Share Card
- Backend: FastAPI + MongoDB (users, applications, saved, notifications)

## Verified
- P0 Apply flow: full end-to-end verified by bug_testing_agent (iteration_3)
- Backend API 100% pass
- P1 controls implemented: forgot password, edit profile, workspace tune, mark-notifications-read, add skill

## Backlog (P1/P2)
- Real email delivery for password reset
- Google/OAuth login
- Real resume storage (S3/object storage)
- Notification bell popover
- Rich profile fields (portfolio uploads)
- Team dashboard for opportunity providers
