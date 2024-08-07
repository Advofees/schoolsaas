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
- printing jobs(have a list of jobs that can be processed for printing)
- support channel (discord,whatsapp,email,chat,twitter)

## models

    - `School`

        - id
        - name
        - email 
        - phone number
        - payment_id
        - logo
        - website url

    - `Teacher`
        - id
        - first name
        - last name
        - email
        - phone
        - school_id

    - `Parent `

        - id
        - first name
        - last name
        - email
        - school_id

    - `Student`

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

    - LessonPlan

        - id
        - teacher_id
        - subject_id
        - term
        - date

    - Examination
        `provide an editor to write question,add tables,objects,images, final output to be well formatted`
        - id

    - Inventory 

        - id
        - title
        - count
        - update at
        - user_id of who updated

    - Payment

        - id
        - invoice_id
        - receipt_id
        - file_id
        
    - File

        - id 
        - url
        - name
        - owner_id(who uploaded)

