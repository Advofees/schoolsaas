# School

- school-name
- school-email
- school-logo
- school-number

- school stats
	- total number of students
	- total number of teachers
	- yearly enrollment stats
	- payments stats
	
- sidebars:
	- teachers
		- your classroom
		- your students
	- students 
		- classroom name
		- classroom number of students
		- gender: Male | Female(stats)
		- attendance stats PRESENT | ABSENT (stats)
		- absent yesterday
		- fetch all students
			- filter by classroom
				- return students for a particular classroom
	
		- if the current user is the teacher:
			- return students for his class only
			- summary to have:
				- attendance stats
					- ABSENT
					- PRESENT
					
Restrict later based on permissions
- views based on Roles
- full information based on their role

parents/students
if you select year return the grades for the three terms as three objects
- grades
	- filter by:
		- year
	 - academic term
- fees
	-  filter by:
		- year
		- academic term
- school-messages:
	- filter by:
		- created_at
# endpoints

- echarts
- vue-echarts
- postgres

