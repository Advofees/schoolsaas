
- school has many school_staff

- staff can be :
    - teacher
    - secretary
    - accountant
    - cook

- school has access to many resources
- school_staff has permissions : 
    - Add parent
    - Add student
    - view inventory

- school has many parents
- parent has many schools
- parent has many students
- student has one parent
- student has many school(could transfer hence can be associated to multiple school)
- school has many inventory
- inventory has many intentory items
- school has many files
- parent has many files
- staff has many files