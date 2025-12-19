# End-to-End Testing Guide - Playbook Management System

This guide provides step-by-step testing procedures to validate the complete playbook-driven incident response workflow.

## Test Environment Setup

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend should be running on: `http://localhost:8000`

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

Frontend should be running on: `http://localhost:5173`

## Test Suite 1: Playbook Loading

### Test 1.1: Verify All Playbooks Load
**Endpoint**: `GET /api/playbooks`

**Expected**: All 8 playbooks load successfully:
- phishing (4 roles, 23 steps)
- malware (5 roles, 34 steps)
- ransomware (6 roles, 41 steps)
- account_compromise (5 roles, 39 steps)
- data_breach (6 roles, 41 steps)
- insider_threat (5 roles, 24 steps)
- ddos (5 roles, 23 steps)
- unauthorized_access (4 roles, 25 steps)

**Test Steps**:
```bash
curl http://localhost:8000/api/playbooks
```

**Success Criteria**: Response contains all 8 playbooks with correct role and step counts.

---

## Test Suite 2: Incident Creation and Role Assignment

### Test 2.1: Create Phishing Incident
**Endpoint**: `POST /api/incidents`

**Test Steps**:
1. Navigate to `http://localhost:5173`
2. Select incident type: "Phishing"
3. Fill out intake form:
   - Reporting user: test@example.com
   - Sender email: attacker@malicious.com
   - Subject: "Urgent: Verify your account"
   - User clicked link: Yes
   - Attachment opened: No
   - Credentials entered: Yes
4. Click "Create Incident"

**Expected**:
- Incident created with unique ID
- Redirected to Investigation phase
- Dashboard shows incident in "intake" phase
- All 4 roles displayed (incident_commander, security_analyst, email_admin, forensics_analyst)
- Only required roles (first 3) show "REQUIRED" badge

**Success Criteria**: Incident created, roles displayed correctly

### Test 2.2: Assign Roles
**Test Steps**:
1. Click "Assign" button on "Incident Commander" role
2. Enter username: "john.doe@company.com"
3. Click "Assign"
4. Repeat for "Security Analyst": "jane.smith@company.com"
5. Repeat for "Email Admin": "bob.jones@company.com"

**Expected**:
- Each assigned role shows username and timestamp
- "Assign" button changes to show assigned user
- Escalation trigger information displayed for forensics_analyst (optional role)

**Success Criteria**: All roles assigned successfully

---

## Test Suite 3: Step Execution and Evidence Collection

### Test 3.1: Start Investigation Step
**Test Steps**:
1. On Investigation page, find step "inv_001: Review authentication logs"
2. Verify dependencies are met (should be first step)
3. Click "Start" button
4. Verify step status changes to "In Progress"

**Expected**:
- Step status icon changes to spinning indicator
- "Start" button disabled
- Timer starts showing "Time spent: Xm"
- Evidence collection form appears

**Success Criteria**: Step transitions to in_progress state

### Test 3.2: Collect Evidence
**Test Steps**:
1. Expand step "inv_001"
2. Click "Add Evidence" button
3. Fill in evidence form:
   - auth_logs (file): Click "Upload File" → reference: "logs/auth-2025-01.log"
   - suspicious_logins (text): "3 failed login attempts from IP 192.168.1.100"
4. Click "Submit Evidence"

**Expected**:
- Evidence modal closes
- Evidence badge appears on step showing "2 items"
- Evidence expandable section shows collected evidence

**Success Criteria**: Evidence saved and displayed correctly

### Test 3.3: Complete Step
**Test Steps**:
1. Click "Complete" button on step "inv_001"
2. Verify step status changes to "Completed"

**Expected**:
- Step status icon changes to green checkmark
- Step card background changes to light green
- Completion timestamp recorded
- Time spent calculated and displayed

**Success Criteria**: Step marked complete with correct timing

### Test 3.4: Test Step Dependencies
**Test Steps**:
1. Locate step "inv_002: Identify source IP and location"
2. Verify it has dependency on "inv_001"
3. Attempt to start step before "inv_001" is complete

**Expected (before inv_001 complete)**:
- Step shows yellow border with "Dependencies not met" indicator
- Start button disabled
- Dependency list shows "inv_001" in red

**Expected (after inv_001 complete)**:
- Dependencies indicator turns green
- Start button becomes enabled
- Can start step normally

**Success Criteria**: Dependency checking works correctly

### Test 3.5: Test Parallel Execution
**Test Steps**:
1. Locate steps "inv_004" and "inv_005" (parallel_group: "impact_assessment")
2. Verify both can be started simultaneously
3. Start both steps at the same time

**Expected**:
- Both steps show blue dashed border indicating parallel group
- Both can be in "In Progress" state simultaneously
- Group label shows "Can run in parallel with other steps in this group"

**Success Criteria**: Parallel execution allowed

### Test 3.6: Test Conditional Steps
**Test Steps**:
1. Complete investigation with `user_clicked: "yes"` in incident data
2. Verify step "inv_001: Review authentication logs" appears (triggers_when: user_clicked = "yes")
3. Create new incident with `user_clicked: "no"`
4. Verify step does NOT appear

**Expected**:
- Conditional steps only appear when trigger conditions met
- Steps that don't apply show "applies: false" in data structure
- UI hides non-applicable steps

**Success Criteria**: Conditional logic works correctly

---

## Test Suite 4: Phase Handoffs and Sign-Offs

### Test 4.1: Check Handoff Requirements
**Test Steps**:
1. Complete 80% of investigation steps (at least 4 out of 5 critical steps)
2. Scroll to "Handoff Panel" at bottom of Investigation page
3. Review handoff requirements checklist

**Expected**:
- Requirement 1: "At least 80% of investigation steps completed" - Green checkmark if met
- Requirement 2: "Security analyst sign-off required" - Red circle if not met
- "Initiate Handoff" button disabled until all requirements met

**Success Criteria**: Requirements calculated correctly

### Test 4.2: Initiate Handoff
**Test Steps**:
1. Complete all remaining investigation steps to reach 100%
2. Sign off on investigation phase (if required)
3. Click "Initiate Handoff to containment" button
4. Enter handoff notes: "Investigation complete, identified compromised credentials"
5. Click "Confirm Handoff"

**Expected**:
- Handoff recorded with timestamp and notes
- "Pending Handoff" section appears
- Shows: from_role, to_role, initiated_by, completion percentage
- Handoff notes displayed
- "Sign Off on Handoff" button appears for receiving role

**Success Criteria**: Handoff initiated and pending sign-off

### Test 4.3: Sign Off on Handoff
**Test Steps**:
1. As incident_commander role, click "Sign Off on Handoff"
2. Enter sign-off notes: "Received, beginning containment procedures"
3. Click "Sign Off"

**Expected**:
- Phase changes from "investigation" to "containment"
- Browser navigates to Containment page
- Investigation phase marked "Completed" in dashboard
- Containment phase marked "In Progress"
- Handoff added to handoff_history

**Success Criteria**: Phase transition completes successfully

---

## Test Suite 5: Time Tracking and SLA Monitoring

### Test 5.1: Verify Time Tracking Dashboard
**Test Steps**:
1. Navigate to any phase page
2. View "Time Tracking Dashboard" at top of page

**Expected**:
- Shows all phases in order: intake → investigation → containment → remediation → closure
- Current phase highlighted with blue border
- Completed phases show green
- Each phase shows:
  - Progress bar with completion percentage
  - Estimated vs actual time
  - Started/completed timestamps
  - SLA status indicator

**Success Criteria**: Dashboard accurately reflects progress

### Test 5.2: Test SLA Warning
**Test Steps**:
1. Create incident with investigation SLA: 4 hours target, 6 hours escalation
2. Artificially set phase start time to 5 hours ago (modify database or wait)
3. Refresh dashboard

**Expected**:
- SLA status changes from "on_track" (green) to "warning" (yellow)
- Shows "1h remaining" until escalation threshold
- Warning icon appears

**Success Criteria**: SLA warning triggers correctly

### Test 5.3: Test SLA Breach
**Test Steps**:
1. Continue from Test 5.2, set time to 7 hours ago
2. Refresh dashboard

**Expected**:
- SLA status changes to "breached" (red)
- Shows "1h overdue"
- Breach warning appears: "SLA threshold exceeded - escalation required"

**Success Criteria**: SLA breach detection works

---

## Test Suite 6: Containment Phase

### Test 6.1: Execute Containment Steps
**Test Steps**:
1. On Containment page, complete step "cont_002: Change compromised credentials"
2. Add evidence:
   - credentials_changed (boolean): Yes
3. Complete step

**Expected**:
- Step marked complete
- Credentials reset action recorded
- Next dependent step becomes available

**Success Criteria**: Containment actions execute correctly

### Test 6.2: Handle Blocked Step
**Test Steps**:
1. Start step "cont_005: Patch exploited vulnerability"
2. Click "Mark as Blocked"
3. Enter blocked reason: "Patch requires change approval, waiting for CAB"
4. Submit

**Expected**:
- Step status changes to "Blocked"
- Red blocked icon appears
- Blocked reason displayed
- Dependent steps remain locked
- Open risks section on Summary page will include this

**Success Criteria**: Blocked step handling works

---

## Test Suite 7: Summary Generation

### Test 7.1: Generate Incident Summary
**Test Steps**:
1. Complete containment phase
2. Navigate to Summary page
3. Review generated summary

**Expected Summary Contains**:
- Incident ID, type, timestamps
- Total time spent (calculated from phase executions)
- Phases completed list
- Incident narrative (built from playbook data)
- Actions taken (from step evidence)
- Open risks (from blocked steps and notes)
- Recommended follow-ups
- Complete timeline of phase transitions

**Success Criteria**: Summary accurately reflects incident

### Test 7.2: Export Summary as JSON
**Test Steps**:
1. Click "Export as JSON" button
2. Verify file downloads: `incident-{id}.json`
3. Open file and validate structure

**Expected JSON Structure**:
```json
{
  "incident_id": "...",
  "incident_type": "phishing",
  "created_at": "...",
  "total_time_spent_hours": 2.5,
  "phases_completed": ["intake", "investigation", "containment"],
  "actions_taken": [...],
  "open_risks": [...],
  "timeline": [...]
}
```

**Success Criteria**: Valid JSON export

### Test 7.3: Export Summary as Text
**Test Steps**:
1. Click "Export as Text" button
2. Verify file downloads: `incident-{id}.txt`
3. Open file and validate formatting

**Expected Text Format**:
```
INCIDENT RESPONSE SUMMARY
==================================================

Incident ID: abc123
Incident Type: phishing
...
```

**Success Criteria**: Well-formatted text export

---

## Test Suite 8: Multi-Incident Type Testing

### Test 8.1: Test Ransomware Playbook
**Test Steps**:
1. Create ransomware incident
2. Verify ransomware-specific roles appear:
   - backup_admin
   - legal_counsel
3. Verify ransomware-specific steps appear:
   - "Check for offline backup availability"
   - "Determine ransom demand amount"
4. Complete workflow through containment

**Success Criteria**: Ransomware playbook executes correctly

### Test 8.2: Test Data Breach Playbook
**Test Steps**:
1. Create data_breach incident
2. Verify data breach-specific roles:
   - privacy_officer
   - legal_counsel
   - communications_lead (optional, escalates on "media_attention")
3. Verify notification requirements displayed
4. Complete investigation, verify GDPR compliance steps

**Success Criteria**: Data breach playbook with regulatory compliance works

### Test 8.3: Test DDoS Playbook
**Test Steps**:
1. Create ddos incident
2. Verify tight SLAs:
   - Intake: 15 minutes target
3. Verify ISP liaison role required
4. Test rapid response workflow

**Success Criteria**: DDoS playbook with urgent SLAs works

---

## Test Suite 9: Error Handling

### Test 9.1: API Error Handling
**Test Steps**:
1. Stop backend server
2. Attempt to start a step in frontend
3. Verify error message displayed: "Failed to start step"

**Success Criteria**: Graceful error handling

### Test 9.2: Missing Evidence Validation
**Test Steps**:
1. Start step requiring evidence
2. Attempt to complete without providing required evidence
3. Verify validation error

**Expected**: Error message: "Required evidence not collected"

**Success Criteria**: Evidence validation works

### Test 9.3: Handoff Requirement Validation
**Test Steps**:
1. Attempt to initiate handoff with only 50% completion
2. Verify handoff blocked

**Expected**: Button disabled, tooltip shows unmet requirements

**Success Criteria**: Handoff validation prevents premature transitions

---

## Test Suite 10: Performance and Load Testing

### Test 10.1: Large Playbook Loading
**Test Steps**:
1. Load ransomware playbook (41 steps)
2. Measure load time

**Expected**: < 500ms to load and render all steps

**Success Criteria**: Acceptable performance

### Test 10.2: Concurrent Step Updates
**Test Steps**:
1. Open same incident in two browser tabs
2. Start different steps simultaneously
3. Verify both updates persist

**Expected**: Both updates successful, no conflicts

**Success Criteria**: Concurrent updates handled correctly

---

## Test Coverage Summary

| Test Suite | Tests | Critical |
|------------|-------|----------|
| Playbook Loading | 1 | Yes |
| Incident Creation | 2 | Yes |
| Step Execution | 6 | Yes |
| Phase Handoffs | 3 | Yes |
| Time Tracking | 3 | Yes |
| Containment | 2 | Yes |
| Summary Generation | 3 | Yes |
| Multi-Incident Types | 3 | Yes |
| Error Handling | 3 | Yes |
| Performance | 2 | No |
| **Total** | **28** | **24** |

---

## Known Issues and Limitations

1. **Authentication**: No real authentication implemented, using hardcoded users
2. **Notifications**: Notification triggers defined but not implemented
3. **Automation**: No integration with security tools (future enhancement)
4. **Multi-tenancy**: Single-tenant only
5. **Database**: In-memory storage, data lost on restart

---

## Success Criteria for Production Readiness

- [ ] All 24 critical tests pass
- [ ] All 8 incident types tested end-to-end
- [ ] All 250 playbook steps loadable
- [ ] Phase handoffs work correctly
- [ ] Time tracking accurate
- [ ] Evidence collection functional
- [ ] Summary generation complete
- [ ] SLA monitoring operational
- [ ] Export functionality works

---

## Next Steps After Testing

1. Implement authentication/authorization
2. Add notification system
3. Set up persistent database
4. Create admin UI for playbook customization
5. Add metrics and reporting dashboard
6. Integrate with security tools (SIEM, EDR, email gateway)
7. Implement learning system to track playbook effectiveness
