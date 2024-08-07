# School

- aim of this project is provide stupid solutions to schools conviniently
- schools can pay a small fee to conviniently use our solution


## possible features
- class register
- school inventory(customizable per class,per department)
- finance tracker for expenses and purcheses
- grades management
- exam reports
- results exports
- inventory exports
- class curriculm planning aided by AI 
- parents can pay to school and upload receipts ,prove of payment
- school can send invoices to parents for fees
- school can manage list of past papers for all subjects
- school can manage past lesson plans
- school inventory
- notifications
- file uploads(receipts, exams,invoices,assignments)


## models

    - `school`
        - id
        - name
        - email 
        - payment_id

    - `teacher`
        - id
        - first name
        - last name
        - email
        - phone
        - school_id
    - `parent `
        - id
        - first name
        - last name
        - email
        - school_id

    - `student`
        - first name
        - last name
        - phone
        - admission_number
        - parent_id
        - class_id
        - payments_id
    
    - `Grade`
        - id
        - subject_id
        - student_id
        - class_id
        - teacher_id
        - exam_id
        - score

    - lessons plans
        - id
        - teacher_id
        - subject_id
        - term
        - date

    - inventory 
        - id
        - title
        - count
        - update at
        - user_id of who updated

    - payments

        - id
        - invoice_id
        - receipt_id
        - file_id
        
    - files
        - id 
        - url
        - name
        - owner_id(who uploaded)