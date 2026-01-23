# 🎯 TASK-LEVEL SPECIFICATIONS FOR UOH ACADEMIC EVALUATION SYSTEM

**Document Version:** 1.0  
**Last Updated:** 2025-01-23  
**Project:** UOH Hackathon - Academic Evaluation & Reporting Assistant  
**Status:** Production-Ready MVP Specifications

---

## 📋 TABLE OF CONTENTS

1. [Task A: OCR & Parsing Schema](#task-a-ocr--parsing-schema)
2. [Task B: LLM Insight Prompt](#task-b-llm-insight-prompt)
3. [Task C: Dashboard Analytics Logic](#task-c-dashboard-analytics-logic)
4. [Task D: Excel Export Structure](#task-d-excel-export-structure)
5. [Implementation Checklist](#implementation-checklist)

---

## 🔹 TASK A: OCR & PARSING SCHEMA

### Design a minimal OCR extraction schema for academic documents

**Purpose:** Handle answer sheets, project evaluations, and transcripts with partial OCR failure support and faculty review capability.

### Core Schema Structure

```yaml
# REQUIRED FIELDS (Must Extract)
student_identification:
  student_name: string (2-100 chars)
  roll_number: string (5-20 alphanumeric)
  email: string (valid format or empty)
  department: string
  
academic_core:
  cgpa: float (0.0-10.0, -1.0 if not found)
  semester: string ("Sem-1" to "Sem-10")
  attendance_percentage: float (0.0-100.0, -1.0 if not found)
  
# IMPORTANT FIELDS (Best Effort)
courses:
  - course_code: string (3-15 chars)
    course_name: string
    grade: string (A+/A/B+/B/C/D/F/I/W/N/A)
    credits: integer (1-10, default: 3)
    
# OPTIONAL FIELDS (If Available)
projects:
  - project_title: string
    duration: string
    status: string
    
internships:
  - organization: string
    role: string
    duration: string
```

### Validation Rules

| Field | Validation | Default on Failure |
|-------|-----------|-------------------|
| student_name | Length 2-100, alphabets+spaces | "Unknown Student" |
| roll_number | Alphanumeric 5-20, no spaces | "ROLL_NOT_FOUND" |
| cgpa | 0.0 - 10.0 | -1.0 |
| grade | Must be in [A+,A,B+,B,C,D,F,I,W] | "N/A" |
| credits | 1-10 integer | 3 |

### Handling Partial OCR Failures

**3-Pass Strategy:**

```
Pass 1: PDF Text Extraction (PyPDF2)
  ↓ If fails or confidence < 0.5
Pass 2: OCR with Tesseract
  ↓ If critical fields missing
Pass 3: Flag for Faculty Review
```

**Confidence Scoring:**

```python
if field_confidence < 0.7:
    flag_for_review = True
    color_code = "YELLOW"  # Traffic light system
```

**Priority Levels:**

- **Priority 1 (Critical):** student_name, roll_number, department
- **Priority 2 (Important):** cgpa, email, courses  
- **Priority 3 (Optional):** projects, internships

### Faculty Review Interface Requirements

**Must Support:**
1. Side-by-side view (Original PDF + Extracted Data)
2. Inline editing for all fields
3. Confidence indicators (🔴 Red / 🟡 Yellow / 🟢 Green)
4. Quick actions: Accept All / Review Flagged / Reject
5. Batch approve (for high-confidence extractions)

**Review Workflow:**

```
Upload → OCR → Confidence Check
   ↓
if confidence >= 0.8: Auto-approve
if confidence < 0.8: Flag for review
   ↓
Faculty edits/approves → Save to DB
```

### Sample Low-Confidence Extract

```json
{
  "student_name": "RAJESH KUMAR",
  "roll_number": "21CS3045",
  "cgpa": 8.45,
  "email": "rajesh.21cs@uoh.ac.in",
  "confidence_metadata": {
    "overall": 0.76,
    "student_name": 0.95,
    "email": 0.58
  },
  "flagged_fields": ["email"],
  "requires_review": true
}
```

---

## 🔹 TASK B: LLM INSIGHT PROMPT

### Production-Ready Prompt for Gemini/Cohere

**Copy this entire prompt into your LLM system prompt:**

```markdown
# ACADEMIC PERFORMANCE ANALYSIS ASSISTANT

You are an academic analysis assistant for University of Hyderabad faculty.

## CRITICAL RULES
1. NO HALLUCINATION - Base insights ONLY on provided data
2. NO INVENTIONS - If data missing, state "Data not available"
3. NO ASSUMPTIONS - Don't infer unstated information
4. NO MEDICAL/PSYCHOLOGICAL CLAIMS - Avoid diagnosing
5. NO GRADING DECISIONS - Don't recommend pass/fail
6. FACTUAL ONLY - Present patterns, not judgments

## INPUT
You receive academic data in JSON with:
- Student info (name, roll, department)
- Performance (CGPA, grades, attendance)
- Courses (code, name, credits, grade)

## TASKS

### 1. Performance Pattern Summary
```
PERFORMANCE SUMMARY:
• Current CGPA: [value]
• Credits Earned: [earned/registered]
• Attendance: [percentage]%
• Grade Distribution: [X A's, Y B's, Z C's]
```

### 2. Weak Subjects Identification
```
AREAS NEEDING ATTENTION:
• [Course Code] - [Course Name]: Grade [X]
  Reason: [Grade below average / Low grade high credits]

If none: "Student performing consistently across all courses"
```

### 3. At-Risk Flags
```
ATTENTION FLAGS:
⚠️ [Flag Type]: [Value] (Threshold: [value])
   Action: [Faculty review / Counseling / No action]
```

Flags:
- CGPA < 6.0
- Attendance < 75%
- Backlogs >= 3
- CGPA drop > 0.5 between semesters

### 4. Faculty-Friendly Summary
- Max 5 bullet points per section
- Clear, professional language
- Focus on "what" and "why"
- Actionable recommendations

## OUTPUT FORMAT

```
═══════════════════════════════════════
ACADEMIC PERFORMANCE ANALYSIS
Student: [Name] | Roll: [Number] | Dept: [Dept]
═══════════════════════════════════════

📊 PERFORMANCE SUMMARY
• Current CGPA: [X.XX]/10
• Credits: [earned]/[registered]
• Attendance: [XX]%
• Standing: [Good/Probation/N/A]

📈 GRADE DISTRIBUTION
• A-Grades (9-10): [count]
• B-Grades (7-8.9): [count]
• C-Grades (5-6.9): [count]
• Below C: [count]

⚠️ AREAS NEEDING ATTENTION
• [Course]: Grade [X] - [Reason]
OR
• No significant concerns

🎯 STRENGTHS
• [Observable strength 1]
• [Observable strength 2]

💡 FACULTY RECOMMENDATIONS
• [Actionable item 1]
• [Actionable item 2]
OR
• Continue current performance

📋 DATA COMPLETENESS
✓ Core Data: [Yes/No]
✓ Course History: [Complete/Partial]
✓ Confidence: [High/Medium/Low]

═══════════════════════════════════════
```

## INSUFFICIENT DATA RESPONSE

```
⚠️ INSUFFICIENT DATA FOR ANALYSIS

Available: [List available fields]
Missing: [List missing fields]

Status: INCOMPLETE

Recommendation: Request complete transcript
```

## QUALITY CHECKLIST
- [ ] No hallucinated values
- [ ] All numbers match input
- [ ] No medical claims
- [ ] No pass/fail decisions
- [ ] Clear fact vs. suggestion distinction
- [ ] Missing data acknowledged
- [ ] Professional language
```

### Implementation Example

```python
def analyze_student(student_data: dict) -> str:
    system_prompt = "[PASTE ABOVE PROMPT]"
    
    user_message = f"""
    Analyze this student:
    {json.dumps(student_data, indent=2)}
    """
    
    response = llm_client.generate(
        system_prompt=system_prompt,
        user_message=user_message,
        max_tokens=2000,
        temperature=0.1  # Low temp for consistency
    )
    
    return response.text
```

---

## 🔹 TASK C: DASHBOARD ANALYTICS LOGIC

### 3 Essential Charts (Logic Only - No Frameworks)

---

### CHART 1: CGPA Distribution Histogram

**Purpose:** Show batch performance distribution

**Axes:**
- X-axis: CGPA ranges (0-4, 4-5, 5-6, 6-7, 7-8, 8-9, 9-10)
- Y-axis: Student count

**Data Logic:**

```python
def calculate_cgpa_distribution(students):
    ranges = {
        "0-4": 0, "4-5": 0, "5-6": 0, 
        "6-7": 0, "7-8": 0, "8-9": 0, "9-10": 0
    }
    
    for student in students:
        cgpa = float(student.get('cgpa', -1))
        if cgpa < 0: continue
        
        if cgpa < 4: ranges["0-4"] += 1
        elif cgpa < 5: ranges["4-5"] += 1
        elif cgpa < 6: ranges["5-6"] += 1
        elif cgpa < 7: ranges["6-7"] += 1
        elif cgpa < 8: ranges["7-8"] += 1
        elif cgpa < 9: ranges["8-9"] += 1
        else: ranges["9-10"] += 1
    
    return ranges
```

**Why Useful:**
- Quick class performance overview
- Identify if batch is struggling/excelling
- Benchmark against previous years
- Determine support resource allocation

**Faculty Use Case:**  
*"If 40% are in 6-7 range and only 10% in 8-10, I need to adjust teaching or provide extra support."*

---

### CHART 2: Subject-Wise Average Performance

**Purpose:** Identify difficult courses

**Axes:**
- X-axis: Course codes (CS301, MA201, etc.)
- Y-axis: Average grade points (0-10)
- Color-coding: Red (<6), Yellow (6-7.5), Green (>7.5)

**Data Logic:**

```python
def calculate_subject_averages(students):
    course_data = {}
    
    for student in students:
        for course in student.get('courses', []):
            code = course['course_code']
            grade_points = convert_grade_to_points(course['grade'])
            
            if code not in course_data:
                course_data[code] = {
                    "name": course['course_name'],
                    "total": 0,
                    "count": 0
                }
            
            course_data[code]["total"] += grade_points
            course_data[code]["count"] += 1
    
    # Calculate averages
    for code, data in course_data.items():
        data["average"] = data["total"] / data["count"]
    
    return course_data

def convert_grade_to_points(grade):
    grades = {
        "A+": 10, "A": 9, "B+": 8, "B": 7,
        "C": 6, "D": 5, "F": 0
    }
    return grades.get(grade, 0)
```

**Why Useful:**
- Spot courses where students struggle
- Assess teaching effectiveness
- Allocate TAs to difficult courses
- Review curriculum difficulty

**Faculty Use Case:**  
*"If CS401 averages 5.2 while other 400-level courses average 7+, that course needs attention—maybe teaching pace, prerequisites, or expectations."*

---

### CHART 3: At-Risk Students Dashboard

**Purpose:** Proactive intervention list

**Format:** Table with columns:
- Name | Roll | Dept | Risk Factors | Priority

**Risk Criteria:**
1. CGPA < 6.0 (High Priority)
2. Attendance < 75% (Medium)
3. Backlogs >= 3 (High)
4. CGPA drop > 0.5 (Medium)

**Data Logic:**

```python
def identify_at_risk_students(students):
    at_risk = []
    
    for student in students:
        risk_factors = []
        priority_score = 0
        
        # CGPA check
        cgpa = float(student.get('cgpa', 10))
        if cgpa < 6.0:
            risk_factors.append(f"Low CGPA: {cgpa}")
            priority_score += 3
        
        # Attendance check
        attendance = float(student.get('attendance_percentage', 100))
        if attendance < 75:
            risk_factors.append(f"Low Attendance: {attendance}%")
            priority_score += 2
        
        # Backlogs check
        backlogs = int(student.get('backlogs_count', 0))
        if backlogs >= 3:
            risk_factors.append(f"Backlogs: {backlogs}")
            priority_score += 3
        
        # Add to list if any risks
        if risk_factors:
            priority = "High" if priority_score >= 4 else \
                      "Medium" if priority_score >= 2 else "Low"
            
            at_risk.append({
                "name": student['student_name'],
                "roll": student['roll_number'],
                "dept": student['department'],
                "risks": risk_factors,
                "priority": priority,
                "score": priority_score
            })
    
    # Sort by priority
    at_risk.sort(key=lambda x: x['score'], reverse=True)
    return at_risk
```

**Why Useful:**
- Identify struggling students BEFORE failure
- Prioritize intervention efforts
- Track counseling outcomes
- Early warning system

**Faculty Use Case:**  
*"Every Monday, I check this. High priority students get immediate counseling. This reduced our dropout rate by 30%."*

---

### Summary: 3 Charts

| # | Chart | Key Metric | Question Answered | Frequency |
|---|-------|-----------|------------------|-----------|
| 1 | CGPA Distribution | Count per range | "How's the class doing?" | After exams |
| 2 | Subject Performance | Avg grade/course | "Which courses are hard?" | End of sem |
| 3 | At-Risk Students | Risk flag list | "Who needs help now?" | Weekly |

**Implementation Priority:**  
Chart 3 → Chart 1 → Chart 2  
(Chart 3 provides immediate actionable value)

---

## 🔹 TASK D: EXCEL EXPORT STRUCTURE

### Multi-Sheet Excel Workbook Design

**File Naming:**
```
academic_evaluation_[BATCH_NAME]_[TIMESTAMP].xlsx

Examples:
- academic_evaluation_batch_2024-01-23_14-30-45.xlsx
- academic_evaluation_CSE_SEM5_2024-01-23.xlsx
```

---

### SHEET 1: Raw Extracted Records

**Purpose:** Complete unfiltered data from OCR

**Columns:**

| Column | Type | Example |
|--------|------|---------|
| Record_ID | Integer | 1, 2, 3... |
| Student_Name | Text | "Rajesh Kumar Sharma" |
| Roll_Number | Text | "21CS3045" |
| Email | Text | "rajesh.21cs3045@uoh.ac.in" |
| Department | Text | "Computer Science" |
| Program | Text | "B.Tech" |
| Semester | Text | "Sem-5" |
| Academic_Year | Text | "2024-2025" |
| CGPA | Number (2 decimals) | 8.45 |
| SGPA | Number (2 decimals) | 8.72 |
| Attendance_Percentage | Number (1 decimal) | 87.5 |
| Credits_Earned | Integer | 120 |
| Credits_Registered | Integer | 148 |
| Backlogs_Count | Integer | 0 |
| Current_Standing | Text | "Good Standing" |
| Extraction_Timestamp | DateTime | "2024-01-23 14:30:45" |
| Confidence_Score | Number (2 decimals) | 0.89 |
| Requires_Review | Boolean | FALSE |

**Example Rows:**

| Record_ID | Student_Name | Roll_Number | CGPA | Attendance | Confidence |
|-----------|-------------|-------------|------|------------|------------|
| 1 | Anjali Sharma | 21PH2034 | 7.85 | 82.5 | 0.92 |
| 2 | Vikram Reddy | 21CS3001 | 9.12 | 95.0 | 0.98 |
| 3 | Priya Gupta | 21MA1045 | 6.45 | 71.0 | 0.76 |

**Formatting:**
- Header row: Bold, blue background (#4472C4), white text
- Freeze first row
- Auto-filter enabled
- Column widths: Auto-fit
- Alternating row colors (white/#F2F2F2)
- Confidence < 0.8: Orange background
- Requires_Review = TRUE: Red text

---

### SHEET 2: Subject-Wise Performance Summary

**Purpose:** Aggregated course statistics

**Columns:**

| Column | Type | Description |
|--------|------|-------------|
| Course_Code | Text | "CS301" |
| Course_Name | Text | "Data Structures" |
| Course_Type | Text | "Core/Elective" |
| Credits | Integer | 4 |
| Students_Enrolled | Integer | 45 |
| Avg_Grade_Points | Number (2 decimals) | 7.85 |
| Grade_A_Count | Integer | 12 |
| Grade_B_Count | Integer | 20 |
| Grade_C_Count | Integer | 10 |
| Grade_D_Count | Integer | 2 |
| Grade_F_Count | Integer | 1 |
| Pass_Percentage | Number (1 decimal) | 95.6 |
| Difficulty_Level | Text (Formula) | "Moderate" |

**Example Rows:**

| Course_Code | Course_Name | Avg_Grade | Pass_% | Difficulty |
|------------|-------------|-----------|--------|------------|
| CS301 | Data Structures | 7.85 | 97.8 | Moderate |
| MA201 | Linear Algebra | 6.12 | 88.9 | Difficult |
| PH101 | Quantum Mechanics | 8.45 | 100.0 | Easy |

**Formulas:**

```excel
# Difficulty Level (column L)
=IF(K2>=8, "Easy", IF(K2>=6.5, "Moderate", "Difficult"))

# Pass Percentage (column J)
=(B2-G2)/B2*100
```

**Formatting:**
- Header: Bold, green background (#70AD47)
- Difficulty "Difficult": Red text
- Pass % < 90%: Orange background
- Conditional formatting on Avg_Grade_Points:
  - >8: Green
  - 6-8: Yellow
  - <6: Red

---

### SHEET 3: Student Difficulty Indicators

**Purpose:** At-risk student identification

**Columns:**

| Column | Type | Description |
|--------|------|-------------|
| Priority | Text | "High/Medium/Low" |
| Student_Name | Text | "Rajesh Kumar" |
| Roll_Number | Text | "21CS3045" |
| Department | Text | "Computer Science" |
| CGPA | Number (2 decimals) | 5.82 |
| Attendance | Number (1 decimal) | 68.5 |
| Backlogs | Integer | 4 |
| Risk_Factors | Text | "Low CGPA, Low Attendance, Multiple Backlogs" |
| Weak_Subjects | Text | "MA201 (C), CS302 (D)" |
| Last_Counseling_Date | Date | "2024-01-15" |
| Counselor_Assigned | Text | "Dr. Sharma" |
| Action_Required | Text | "Immediate intervention" |
| Status | Text | "Pending/In Progress/Resolved" |

**Example Rows:**

| Priority | Name | Roll | CGPA | Attendance | Risk_Factors |
|----------|------|------|------|------------|--------------|
| High | Rajesh K | 21CS3045 | 5.82 | 68.5% | Low CGPA, Low Attend, 4 Backlogs |
| Medium | Priya G | 21MA1045 | 6.45 | 71.0% | Low Attendance |
| Medium | Vikram R | 21PH2012 | 7.12 | 88.0% | CGPA dropped 0.8 points |

**Formulas:**

```excel
# Priority (auto-calculate from risk factors)
=IF(AND(E2<6, F2<75), "High", 
   IF(OR(E2<6.5, F2<80), "Medium", "Low"))
```

**Formatting:**
- Header: Bold, red background (#C00000), white text
- Priority "High": Bold, red background
- Priority "Medium": Yellow background
- Sort by: Priority (High first), then CGPA (ascending)
- Freeze first 2 rows
- Data validation dropdown for Status column

---

### SHEET 4: Batch Metadata (Optional)

**Purpose:** Processing information

**Format:** Key-Value pairs

| Metric | Value |
|--------|-------|
| Batch Name | "CSE_SEM5_2024" |
| Processing Date | "2024-01-23 14:30:45" |
| Total Documents | 150 |
| Successfully Processed | 147 |
| Failed Extractions | 3 |
| Success Rate | 98.0% |
| LLM Provider | "Gemini 1.5 Flash" |
| Average Confidence | 0.87 |
| Documents Flagged for Review | 12 |
| Total Students | 147 |
| Departments | "CSE, ECE, Mech, Civil" |
| Faculty Name | "Dr. Raghavan" |

---

### Update Frequency

| Sheet | Update Frequency | Trigger |
|-------|-----------------|---------|
| Sheet 1: Raw Records | Real-time | After each document processed |
| Sheet 2: Subject Summary | End of batch | After all docs processed |
| Sheet 3: At-Risk Students | Weekly | Every Monday 9 AM |
| Sheet 4: Metadata | End of batch | Final processing step |

---

### Column Name Standards

- Use snake_case for consistency
- Max 30 characters per column name
- No special characters except underscore
- Abbreviations: Avg (Average), Dept (Department), Sem (Semester)

---

### Excel File Properties

```python
# Openpyxl implementation example
workbook = openpyxl.Workbook()

# Sheet 1
ws1 = workbook.active
ws1.title = "Raw_Records"
ws1.freeze_panes = "A2"  # Freeze header row
ws1.auto_filter.ref = ws1.dimensions

# Sheet 2
ws2 = workbook.create_sheet("Subject_Performance")

# Sheet 3
ws3 = workbook.create_sheet("At_Risk_Students")

# Sheet 4 (optional)
ws4 = workbook.create_sheet("Batch_Metadata")

# Save
workbook.save(f"academic_evaluation_{timestamp}.xlsx")
```

---

## 📝 IMPLEMENTATION CHECKLIST

### Task A: OCR Schema
- [ ] Define field categories (Identification, Academic, Performance)
- [ ] Set validation rules for each field
- [ ] Implement 3-pass extraction strategy
- [ ] Add confidence scoring
- [ ] Create faculty review interface
- [ ] Test with low-quality scans

### Task B: LLM Prompt
- [ ] Copy prompt template into system prompt
- [ ] Test with complete student data
- [ ] Test with missing data
- [ ] Verify no hallucinations
- [ ] Confirm proper flagging of insufficient data
- [ ] Validate output format consistency

### Task C: Dashboard Logic
- [ ] Implement CGPA distribution function
- [ ] Implement subject average calculation
- [ ] Implement at-risk identification
- [ ] Test with sample datasets
- [ ] Verify correct edge case handling
- [ ] Add chart refresh logic

### Task D: Excel Export
- [ ] Create 3-sheet workbook structure
- [ ] Implement column formatting
- [ ] Add conditional formatting rules
- [ ] Add formulas for calculated fields
- [ ] Test file generation
- [ ] Verify file opens correctly in Excel

---

## 🧪 TESTING SCENARIOS

### OCR Schema Testing
1. High-quality PDF → Should auto-approve
2. Scanned image PDF → Should use OCR
3. Partially corrupted PDF → Should flag missing fields
4. Missing critical field → Should require review

### LLM Prompt Testing
1. Complete data → Full analysis
2. Missing CGPA → State "Data not available"
3. Student with all A's → No "areas needing attention"
4. Student with CGPA < 6 → Flag as at-risk
5. Empty JSON → Return "INSUFFICIENT DATA"

### Dashboard Logic Testing
1. Empty student list → Return empty results
2. All students CGPA 9+ → All in 9-10 range
3. Mixed performance → Correct distribution
4. No at-risk students → Empty list
5. Student with multiple risk factors → High priority

### Excel Export Testing
1. Generate with 1 student → Verify structure
2. Generate with 100 students → Check performance
3. Open in Excel → Verify formatting
4. Sort/filter → Test auto-filter
5. Formulas → Verify calculations

---

**END OF TASK SPECIFICATIONS**

**Next Steps:**
1. Review this document with your team
2. Choose which task to implement first
3. Use code examples as implementation reference
4. Test each component independently
5. Integrate into main system

**Questions or clarifications needed? Ask before implementing!**
