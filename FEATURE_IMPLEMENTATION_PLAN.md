# PyLearn Feature Implementation Plan

## Executive Summary

This document outlines a comprehensive multi-phase plan to transform PyLearn from an individual learning platform into a full-fledged classroom management system with AI-powered content generation, role-based access, and enhanced UX.

---

## Current State Analysis

### Module 0 - Current Issues Found
1. **Progress bar on card**: Shows on dashboard but meaningless for generative module
2. **Save/Discard UX flaw**: User can't preview module before committing
3. **Limited input options**: Only PDF uploads, no topic-based generation
4. **No module preview**: Generated content not viewable before saving

### Current Architecture
- **Auth**: Email/password + Google OAuth (JWT tokens)
- **User Model**: Basic fields (email, name, progress tracking)
- **Content**: Static modules + AI-generated modules saved to disk
- **No role system**: All users have same permissions
- **No classroom/group concept**: Individual learning only

---

## PHASE 1: Module 0 Fixes & Enhancements
**Priority: HIGH | Estimated Time: 2-3 days**

### 1.1 Remove Progress Bar from Module-0 Card
**Files to modify:**
- `frontend/src/pages/DashboardPage.tsx` (lines 200-230)

**Changes:**
```typescript
// Add condition to skip progress bar for generative modules
{!mod.is_generative && (
  <>
    <ProgressBar value={pct} color={accent} size="sm" showPercent={false} />
    <div className="mt-1 mb-5 flex justify-between">
      <span className="font-mono text-xs text-text-muted">{pct}% Complete</span>
      <span className="font-mono text-xs text-text-muted">{p?.docs_read ?? 0}/{mod.doc_count} Lessons</span>
    </div>
  </>
)}
```

### 1.2 Enhanced Content Generation Options
**New input methods:**
1. **PDF Upload** (existing)
2. **Topic Input** (new) - User enters topic name/description
3. **URL Import** (new) - Scrape content from URL
4. **Text Paste** (new) - Direct markdown/text input

**Backend Changes:**
- New endpoint: `POST /api/generate/from-topic` 
- New endpoint: `POST /api/generate/from-url`
- New endpoint: `POST /api/generate/from-text`

**Frontend Changes:**
- Add tab-based UI in `GenerativeUploadUI.tsx`
- Separate forms for each input type

### 1.3 Preview-First Workflow
**Current flow:** Upload → Generate → Save/Discard
**New flow:** Upload → Generate → **Preview Module** → Save to Disk (from navbar)

**Implementation:**
1. After generation, navigate to module view with temporary ID: `/modules/preview-{uuid}`
2. Add floating "Save to Disk" button in navbar (lime green, pulsing)
3. Store generated data in sessionStorage/Context
4. On save, persist to disk and refresh dashboard
5. On navigate away, prompt user to save

**Files to modify:**
- `frontend/src/pages/GenerativeUploadUI.tsx`
- `frontend/src/pages/ModulePage.tsx` (add preview mode)
- New context: `frontend/src/store/generatedModuleStore.ts`

---

## PHASE 2: Role-Based System (Faculty vs Student)
**Priority: HIGH | Estimated Time: 4-5 days**

### 2.1 Database Schema Changes
**New fields in User table:**
```python
role = Column(String, default="student", nullable=False)  # "student" | "faculty"
created_modules = relationship("ClassroomModule", back_populates="creator")
enrolled_classrooms = relationship("Enrollment", back_populates="student")
```

**New tables:**
```python
class ClassroomModule(Base):
    __tablename__ = "classroom_modules"
    id = Column(Integer, primary_key=True)
    code = Column(String(6), unique=True, index=True, nullable=False)  # 6-digit code
    module_id = Column(String, nullable=False)  # Reference to content module
    title = Column(String, nullable=False)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_test = Column(Boolean, default=False)
    time_limit_minutes = Column(Integer, nullable=True)
    deadline = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    creator = relationship("User", back_populates="created_modules")
    enrollments = relationship("Enrollment", back_populates="classroom_module")

class Enrollment(Base):
    __tablename__ = "enrollments"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    classroom_module_id = Column(Integer, ForeignKey("classroom_modules.id"), nullable=False)
    enrolled_at = Column(DateTime(timezone=True), server_default=func.now())
    score = Column(Integer, nullable=True)  # Overall score/grade
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    student = relationship("User", back_populates="enrolled_classrooms")
    classroom_module = relationship("ClassroomModule", back_populates="enrollments")
```

**Migration:** `alembic revision --autogenerate -m "add_roles_and_classrooms"`

### 2.2 Auth Flow Updates
**Signup:**
- Add role selection: "Student" or "Faculty" (default: Student)
- Update `SignupRequest` schema

**Login Response:**
- Include role in JWT token and UserResponse

### 2.3 Backend APIs

**Faculty Endpoints:**
```python
POST   /api/classrooms/create           # Create classroom from module
GET    /api/classrooms/my-classrooms    # List faculty's classrooms
GET    /api/classrooms/{id}/analytics   # Enrollment stats, scores
DELETE /api/classrooms/{id}             # Delete classroom
PUT    /api/classrooms/{id}             # Update settings
```

**Student Endpoints:**
```python
POST   /api/classrooms/enroll           # Enroll with 6-digit code
GET    /api/classrooms/my-enrollments   # List enrolled classrooms
DELETE /api/classrooms/{id}/unenroll    # Unenroll from classroom
```

### 2.4 Frontend Changes

**New Pages:**
- `frontend/src/pages/FacultyDashboard.tsx` - Faculty-specific dashboard
- `frontend/src/pages/StudentDashboard.tsx` - Student-specific dashboard  
- `frontend/src/pages/ClassroomDetailPage.tsx` - Analytics for faculty
- `frontend/src/pages/SettingsPage.tsx` - Settings for both roles

**Navigation Updates:**
- Role-based dashboard routing
- Faculty: Only sees Module-0 + created classrooms
- Student: Sees all modules + enrolled classrooms

---

## PHASE 3: Navbar & Settings Pages
**Priority: MEDIUM | Estimated Time: 2-3 days**

### 3.1 Scalable Navbar Component
**Location:** `frontend/src/components/Navbar.tsx`

**Structure:**
```typescript
<header className="sticky top-0 z-50 border-b-4 border-border-dark bg-bg-card shadow-neo">
  <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
    {/* Left: Logo & Brand */}
    <Link to="/dashboard" className="flex items-center gap-3">
      <LogoMark size={36} />
      <span className="font-heading font-bold text-xl">PyLearn</span>
    </Link>
    
    {/* Center: Navigation Links (scalable) */}
    <nav className="hidden md:flex items-center gap-6">
      <NavLink to="/dashboard">Dashboard</NavLink>
      {user?.role === 'faculty' && (
        <NavLink to="/create">Create Content</NavLink>
      )}
      {user?.role === 'student' && (
        <NavLink to="/my-courses">My Courses</NavLink>
      )}
      <NavLink to="/leaderboard">Leaderboard</NavLink>
    </nav>
    
    {/* Right: Actions */}
    <div className="flex items-center gap-4">
      {generatedModule && (
        <Button color="green" className="animate-pulse">
          <Save className="w-4 h-4" aria-hidden /> Save to Disk
        </Button>
      )}
      
      <Button variant="ghost" onClick={() => navigate('/settings')}>
        <Settings className="w-4 h-4" aria-hidden /> Settings
      </Button>
      
      <Avatar user={user} />
    </div>
  </div>
</header>
```

### 3.2 Student Settings Page
**Features:**
- Profile info (name, email, avatar)
- Enrolled classrooms list
- "Add Course" section (enter 6-digit code)
- Unenroll from courses
- Learning preferences
- Export progress data

### 3.3 Faculty Settings Page  
**Features:**
- Profile info
- My Classrooms table (code, title, enrolled count, avg score)
- Analytics per classroom (click to expand)
  - Student list with scores
  - Completion rates
  - Concept mastery breakdown
- Delete classroom action
- Export analytics as CSV

---

## PHASE 4: Additional Recommended Features
**Priority: MEDIUM-LOW | Estimated Time: 5-7 days**

### 4.1 Leaderboard System
**Global + Per-Classroom Leaderboards**
- Points system: +10 per doc read, +20 per quiz passed, +50 per problem solved
- Streak bonuses: +5 points/day
- Display top 50 users globally
- Display top 20 per classroom

**New table:**
```python
class UserPoints(Base):
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    total_points = Column(Integer, default=0)
    rank = Column(Integer, nullable=True)
```

### 4.2 Real-Time Notifications
**Use WebSocket for:**
- New enrollments (faculty)
- Assignment deadlines (student)
- Leaderboard position changes
- Module generation progress

**Tech:** Socket.io or FastAPI WebSocket

### 4.3 Analytics Dashboard (Faculty)
**Visualizations:**
- Enrollment trends over time (Line chart)
- Score distribution (Histogram)
- Concept mastery heatmap
- Time spent per lesson (Bar chart)

**Library:** Chart.js or Recharts

### 4.4 Code Execution Sandbox Improvements
**Current:** Basic Python execution
**Enhanced:**
- Support for imports (numpy, pandas)
- Pre-installed packages in sandbox
- Better error messages
- Performance metrics (time, memory)

### 4.5 Content Collaboration
**Allow faculty to:**
- Share module templates with other faculty
- Fork and customize existing modules
- Community module marketplace

### 4.6 Mobile-First Responsive Design
**Optimize for mobile:**
- Bottom navigation for mobile
- Swipeable module cards
- Offline mode (PWA)
- Code editor mobile experience

### 4.7 Gamification Enhancements
**Add:**
- Badges for achievements (First Quiz, 10-day Streak, 50 Problems Solved)
- Daily challenges
- XP levels (Beginner → Expert)
- Animated confetti on milestones

### 4.8 AI Tutor Chatbot
**Integrate:**
- Groq-powered chatbot for help
- Context-aware (knows current lesson)
- Can explain code errors
- Suggests next topics to learn

### 4.9 Version Control for Content
**Allow faculty to:**
- Create multiple versions of modules
- A/B test different content
- Roll back to previous versions

### 4.10 Accessibility Features
**Ensure:**
- Screen reader support
- Keyboard navigation
- High contrast mode
- Text-to-speech for docs
- Adjustable font sizes

---

## Implementation Priority Matrix

| Feature | Impact | Effort | Priority | Phase |
|---------|--------|--------|----------|-------|
| Module-0 UX fixes | High | Low | CRITICAL | 1 |
| Topic-based generation | High | Medium | CRITICAL | 1 |
| Preview workflow | High | Medium | CRITICAL | 1 |
| Role-based system | High | High | HIGH | 2 |
| Classroom creation | High | High | HIGH | 2 |
| Navbar component | Medium | Low | HIGH | 3 |
| Settings pages | Medium | Medium | MEDIUM | 3 |
| Leaderboard | Medium | Medium | MEDIUM | 4 |
| Analytics dashboard | High | High | MEDIUM | 4 |
| Real-time notifications | Low | High | LOW | 4 |
| AI Tutor chatbot | Medium | High | LOW | 4 |
| Mobile optimization | High | High | MEDIUM | 4 |

---

## Technical Considerations

### Database Migrations
- Plan migrations carefully (test on dev DB first)
- Add indexes for `code`, `role`, `classroom_module_id`
- Consider partitioning `enrollments` table if scaling

### Security
- Rate limiting on classroom creation (prevent spam)
- Validate 6-digit codes (alphanumeric, collision handling)
- Role-based middleware on all faculty endpoints
- Sanitize AI-generated content (XSS prevention)

### Performance
- Cache module metadata (Redis)
- Pagination for classroom student lists
- Lazy load modules on dashboard
- Optimize AI generation (streaming responses)

### Testing
- Unit tests for role validation
- Integration tests for enrollment flow
- E2E tests for module generation
- Load testing for concurrent users

---

## Success Metrics

**User Engagement:**
- Average time on platform
- Modules completed per user
- Streak retention rate

**Faculty Adoption:**
- Number of classrooms created
- Average enrollment per classroom
- Faculty satisfaction score

**Content Quality:**
- AI-generated module quality ratings
- Student feedback scores
- Concept mastery improvements

---

## Next Steps

**Immediate (Start Now):**
1. Review this plan and approve phases
2. Set up feature branch: `git checkout -b feature/classroom-system`
3. Start Phase 1: Module-0 fixes

**Short-term (This Week):**
1. Complete Phase 1 (Module-0)
2. Design classroom UI mockups
3. Plan database migrations for Phase 2

**Medium-term (Next 2 Weeks):**
1. Implement Phase 2 (Roles + Classrooms)
2. Build Phase 3 (Navbar + Settings)
3. User testing with beta testers

**Long-term (Next Month):**
1. Roll out Phase 4 features incrementally
2. Gather user feedback
3. Iterate and improve

---

## Questions & Decisions Needed

1. **Classroom codes:** 6-digit alphanumeric or numeric only?
2. **Module sharing:** Should students see module content before enrolling?
3. **Grading:** Auto-grade or faculty-reviewed?
4. **Pricing:** Will classrooms be a premium feature?
5. **Limits:** Max classrooms per faculty? Max enrollments per student?

---

**Created:** 2026-07-30  
**Author:** AI Assistant  
**Status:** Awaiting Review & Approval  

---

## Bonus Ideas (Quick Wins)

1. **Dark Mode Toggle** - Many users prefer dark interfaces
2. **Export Certificate** - PDF certificate on module completion
3. **Study Timer** - Pomodoro timer integrated in navbar
4. **Code Snippets Library** - Save favorite code examples
5. **Keyboard Shortcuts** - Power user features (Ctrl+K command palette)
6. **Progress Reminders** - Email digest of weekly progress
7. **Social Sharing** - Share achievements on Twitter/LinkedIn
8. **Import from GitHub** - Generate modules from README files
9. **Syntax Highlighting Themes** - Customizable editor themes
10. **Voice Commands** - "Next lesson", "Run code" via speech

