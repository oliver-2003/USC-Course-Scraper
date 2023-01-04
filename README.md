# USC-Course-Scraper
USC Course Scraper Class
=
This is a Python class that scrapes certain courses at the University of Southern California Combined with their Rate My Professors data. 

Initializing Object
-
The three arguments in initializing the object are course code/GE category, year, and term. <br>
For the term argument, 1 represents Spring, 2 for Summer, and 3 for Fall.
``` python
scraper_c = UscCourseScraper("c", 2023, 1)
# This generates a UscCourseScraper Object to get the information of all courses of GE category C in 2023 Spring Semester
scraper_econ = UscCourseScraper("econ", 2022, 3)
# This generates a UscCourseScraper Object to get the information of all courses of Economics in 2022 Fall Semester
```
Functions
-
This Python class uses BeautifulSoup to scrape data of all courses of a certain course code or GE category, including the course names, section names, instructors, locations, and time. Then for each instructor, this class uses regular expression to scrape the data including ratings, difficulty, and the number of ratings. Finally, this class puts all data into a Pandas Data Frame that could be exported as a cvs file.

### Get Course Information
```python
scraper_c = UscCourseScraper("c", 2023, 1)
scraper_c.get_course_info()
```
This call of the get_course_info function returns a Data Frame of the information on all courses of GE category C in 2023 Spring Semester

### Get Course Information with the Rate My Professors data
```python
scraper_econ = UscCourseScraper("econ", 2022, 3)
scraper_econ.get_course_data_frame()
```
This call of the get_course_dara_frame function returns a Data Frame of the information for all courses of Economics in 2022 Fall Semester combined with data including the rating and difficulty of each instructor. 

### Export Data as a csv File
 ```python
scraper_econ = UscCourseScraper("econ", 2022, 3)
scraper_econ.course_data_to_csv()
```
This call of course_data_to_csv exports the Data Frame as a csv file named 2022FallEcon.csv
 
 
