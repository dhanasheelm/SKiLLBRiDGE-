# SKILLBRIDGE Product Requirements

## Original problem statement
Build SKILLBRIDGE, a premium AI-powered opportunity platform for students and skilled professionals, including role selection, authentication, separate onboarding, personalized home, dashboard, deterministic skill matching, opportunities, details, applications, profiles, notifications, search/filtering, responsive design, persistent state, demo data, routing, and complete hackathon demo flow.

## Architecture decisions
- React single-page application with React Router routes for public, onboarding, and authenticated experiences.
- Local browser persistence is used for demo authentication, user profile, saved opportunities, and applications; no external auth setup is required.
- Deterministic skill overlap data powers match scores and explanations for reliable presentations.
- Demo data is seeded in the frontend for eight realistic opportunities and two existing applications.

## Personas
- Student exploring internships, research, projects, and early career opportunities.
- Skilled professional looking for projects, freelance work, collaboration, or employment.
- Hackathon presenter demonstrating a polished end-to-end journey.

## Core requirements
- Role-first unauthenticated entry screen.
- Role-specific auth and onboarding paths.
- Authenticated navigation without login/signup links.
- Home, dashboard, skill match, opportunity discovery/details, apply tracking, profile, and notifications.
- Responsive layouts with loading/error/empty states and accessible reduced-motion behavior.

## Implemented (2026-08-18)
- Premium near-black, deep navy, cyan/violet visual system with responsive layouts.
- Student/professional role selection and role-specific authentication/demo entry.
- Four-step onboarding, persistent session guard, logout.
- Home with AI match hero, My Applications, and latest opportunities.
- Dashboard stats, skill breakdown, recent activity.
- Opportunity search/filtering, details, save, apply action, and persistent My Applications.
- Dedicated Skill Match analysis, notifications, and profile pages.
- Demo seed: eight opportunities and two applications.

## Backlog
- P0: Add backend persistence and real user accounts when the demo needs multi-device access.
- P1: Add resume upload and full multi-step application review/submit form.
- P1: Add professional-specific opportunity seed data and professional profile editing.
- P2: Add real AI explanation generation and employer opportunity submission.