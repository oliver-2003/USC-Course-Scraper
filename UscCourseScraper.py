from bs4 import BeautifulSoup
import pandas as pd
import randHeaderProxy
import re
import requests


class UscCourseScraper:
    course_code = ""
    year = ""
    term = ""
    course_url = ""

    def __init__(self, course_code, year, term):
        self.course_code = course_code
        self.year = year
        self.term = term

    def get_course_url(self, course_code, year, term):
        # For the argument term, 1 for Spring, 2 for Summer, and 3 for Fall
        course_code = course_code.lower()
        # Convert a GE Category into a course code
        course_code_dict = {"a": "arts", "b": "hinq", "c": "sana", "d": "life", "e": "psc", "f": "qrea", "h": "gph"}
        try:
            real_course_code = course_code_dict[course_code]
        except KeyError:
            real_course_code = course_code

        self.course_url = f'https://classes.usc.edu/term-{year}{term}/classes/{real_course_code}/'

    def get_course_info(self):
        # Set the target course page URL
        self.get_course_url(self.course_code, self.year, self.term)
        headers = randHeaderProxy.get_random_agent()
        proxies = randHeaderProxy.get_random_proxy()
        res = requests.get(self.course_url, headers=headers, proxies=proxies)
        soup = BeautifulSoup(res.text, "html.parser")
        # Locate the information table for each course
        courses = soup.find_all("div", class_="course-info expandable")

        professor_list = []
        course_list = []
        # Define the list for sections of some courses
        section_list = []

        professors = soup.find_all("td", class_="instructor")
        locations = soup.find_all("td", class_="location")
        locations = [location.text for location in locations]
        days = soup.find_all("td", class_="days")
        days = [day.text for day in days]
        registered_num = soup.find_all("td", class_="registered")
        registered_num = [registered.text for registered in registered_num]
        times = soup.find_all("td", class_="time")
        times = [time.text for time in times]
        # Convert all elements in the list into str

        for course in courses:
            course_name = course.find("a").text.replace("(4.0 units)", "").replace("(4.0 units, max 8)", "")
            # Get rid of some meaningless suffixes in the course names
            sessions = course.find_all("td", class_="session")
            for session_num in range(len(sessions)):
                course_list.append(course_name)
            # Since every table row has a "session", use generate a course name for each row based on the number of sessions

            if course.find("td", class_="section-title") is not None:
                sections = course.find_all("td", class_="section-title")
                for section in sections:
                    section_list.append(section.text)
            else:
                for i in range(len(sessions)):
                    section_list.append(" ")
            # If the course has sections, append the section names into the list. If not, append a null string.

        for professor in professors:
            if professor is not None:
                professor_list.append(professor.text)
            else:
                professor_list.append(" ")
        # For each row in the course table, if the session has an instructor, append the name of the instructor. If not, append a null string.

        data = {'courses': course_list, 'professors': professor_list, 'sections': section_list, 'locations': locations,
                'days': days, "registered": registered_num, 'time': times}
        df = pd.DataFrame(data)
        # Generate a Data Frame using the scraped information

        row_num = 0
        for row in df["sections"]:
            if row != " ":
                df.at[row_num, "courses"] = df.at[row_num, "courses"] + ": " + df.at[row_num, "sections"]
            row_num += 1
        df = df.drop(labels='sections', axis=1)
        # Combine the course names with the section names, and then delete the section column

        row_num = 0
        for row in df["professors"]:
            if len(row) < 1:
                df = df.drop([row_num], axis=0)
            row_num += 1
        df = df.reset_index(drop=True)
        # Drop the rows without an instructor, and then reset the index

        return df

    def get_professor_info(self):
        df = self.get_course_info()
        # Generate the Data Frame of the targeted course page

        professor_list = df["professors"].unique()
        # Generate the list of unique professor names
        headers = randHeaderProxy.get_random_agent()
        proxies = randHeaderProxy.get_random_proxy()
        for professor in professor_list:
            professor_url = f'https://www.ratemyprofessors.com/search/teachers?query={professor}&sid=1381'
            # Generate a Rate My Professors URL for each professor. "sid =1381" targets all professors in USC.
            try:
                res = requests.get(professor_url, headers=headers, proxies=proxies)
                first_name = re.findall('"firstName":"(.*?)",', res.text, re.S)[0]
                last_name = re.findall('"lastName":"(.*?)",', res.text, re.S)[0]
                name = first_name + ' ' + last_name
                # Use regular expression to find the first name and last name of the professor, and then combine them to get the full name.

                rating = re.findall('"avgRating":(.*?),', res.text, re.S)[0]
                difficulty = re.findall('"avgDifficulty":(.*?),', res.text, re.S)[0]
                retake_rate = re.findall('"wouldTakeAgainPercent":(.*?),', res.text, re.S)[0]
                num_ratings = re.findall('"numRatings":(.*?),', res.text, re.S)[0]
                # Use regular expression to find the basic data of each professor.

                df.loc[df['professors'] == name, 'Rating'] = rating
                df.loc[df['professors'] == name, 'difficulty'] = difficulty
                df.loc[df['professors'] == name, 'retake_rate'] = retake_rate
                df.loc[df['professors'] == name, 'num_ratings'] = num_ratings
                # Generate columns in the Data Frame for the basic information of each professor

            except IndexError:
                continue
            # If the professor is not recorded in Rate My Professors, an IndexError will be thrown.

        return df

    def get_course_data_frame(self):
        df = self.get_professor_info()
        print(df)

    def course_data_to_csv(self):
        df = self.get_professor_info()
        term_dict = {1: "Spring", 2: "Summer", 3: "Fall"}
        term = term_dict[self.term]
        self.course_code = self.course_code.title()
        df.to_csv(f"{self.year}{term}{self.course_code}.csv")
        # Export a csv file of the Data Frame


scraper_c = UscCourseScraper("c", 2023, 1)
# Generate a UscCourseScraper Object to get the information of all courses of GE category C in 2023 Spring Semester
scraper_c.get_course_data_frame()
scraper_c.course_data_to_csv()

scraper_econ = UscCourseScraper("econ", 2022, 3)
# Generate a UscCourseScraper Object to get the information of all courses of Economics in 2022 Fall Semester
scraper_econ.get_course_data_frame()
scraper_econ.course_data_to_csv()



