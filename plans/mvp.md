# MVP Checklist
- users
  - school-admin
  - teachers
    - roles:
      - TEACHER
      - CLASS_TEACHER
  - student/parent

- registration
  - registration is for schools only

- register
  - name
  - email
  - school_code/school_number
  - contact number

- login
  - email
  - password

- school-admin-dashboard

  - info

    - [ ] School name 
    - [ ] School email 
    - [ ] School logo
    - [ ] School contact number 

  - stats

    - [ ] Total student count
    - [ ] Total teacher 
    - [ ] attendance metrics
          - total present count
            - male count
            - female count
          - total absent count
            - male count
            - female count
        
    - [ ] Yearly enrollment trends
    - [ ] Payment analytics
          - Revenue overview
          - Outstanding payments
          - Payment history



## Teacher dashboard Features
- [ ] Classroom management
  - [ ] View assigned classroom
  - [ ] Student list management
- [ ] Student Analytics
  - [ ] Gender distribution stats
  - [ ] Attendance tracking
    - [ ] Present/Absent marking
    - [ ] Daily attendance summary
    - [ ] Absence notifications
  - [ ] Class-specific student filters
  - [ ] Attendance reports generation

## Student/Parent Dashboard Features
- [ ] Academic Records
  - [ ] Grade viewing by year
  - [ ] Term-wise grade breakdown
    - [ ] First term
    - [ ] Second term
    - [ ] Third term
- [ ] Fee Management
  - [ ] View fees by year
  - [ ] View fees by term
  - [ ] Payment history
- [ ] School Communications
  - [ ] Message center
  - [ ] Date-based message filtering

## API Endpoints
- [ ] Authentication endpoints
- [ ] School information endpoints
- [ ] Analytics endpoints
- [ ] Student management endpoints
- [ ] Grade management endpoints
- [ ] Attendance management endpoints
- [ ] Communication endpoints

## Filters & Search
- [ ] Classroom filter
- [ ] Year filter
- [ ] Term filter
- [ ] Date range filter for messages
- [ ] Student search functionality

## Additional Features
- [ ] Role-based view restrictions
- [ ] Data export functionality


## Notes:
- Each item can be marked as complete by changing `[ ]` to `[x]`
- Implementation priority should follow the order listed
- All features should include proper error handling and validation
- Regular testing and feedback loops should be maintained
- Documentation should be updated as features are completed
