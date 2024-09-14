# Auth

# School
    - isolate access to all data related to this school via auth
    - before access to data for a particular check ownership
        - does staff belong to this school 
        - do they have permissions

- school register endpoint
- 2fa for school via email
- school can add staff_users
- school assign permissions to staff users

# Authorization
- request for an action say create add_teachers, will need:
    - authenticated user
    - user with a role 
    - the role id must return a permission with add_teacher as true for that request to be completed

  