# MODE PUSH: An Online News Site and Archive for Formula 1 Enthusiasts

#### Video Demo: 
https://youtu.be/0n4ziexflo0
#### Description: 
Mode Push is an online hub where Formula 1 fans can stay updated regarding the latest standings, race results, and news about F1. The website is regularly updated with the latest Formula 1 news and race results. I made this website using HTML, CSS, and JavaScript for the front end and Flask for the back end. The web application also uses a MySQL database containing the important data about the drivers and teams. The integrates two APIs, namely [Ergast API](https://ergast.com/mrd/) for the Formula 1 data and [NewsAPI](https://newsapi.org/) for the news articles. It contains four main sections: Home, Driver, Constructors, and Races. 

The **Home** section contains the latest race results and articles related to Formula 1. The **Driver** section contains the driver standings of the season, which could be filtered to display the standings of previous seasons. The **Constructors** section follows the same idea, except it shows the team standings. Finally, the **Races** section shows the results of the races of a season, which could also be filtered to display race results of previous seasons. These sections default to displaying the current season. The drivers, teams, and races each have their "profile" pages, which show important information about them, such as points, positions, wins, championships, and others. For example, on a driver's profile page, you can see their current position in the standings, their total points, and their recent race results.

## Project Files
### styles.css
The first line imports two fonts from Google Fonts for the website. The following lines changed the font family and font size of the elements, the cursor, and the dimensions of the elements. I also added a box shadow to the navbar to provide more depth. Moreover, I ensured that the article cards on the homepage had uniform width and height because it took much work to implement the look I wanted in Bootstrap. Other than that, I mainly relied on Bootstrap for the website's styling. 

### script.js
In my script.js file, I created a function that toggles the website's theme from light mode to dark mode. I took advantage of Bootstrap's built in color modes by setting the html element's 'data-bs-theme' attribute to dark or light depending on the initial state. The new theme is then stored to the website's local storage, so that the website remains in the chosen color mode until the user changes it. I also made a factory function to return the footer element, which contains a link to my GitHub portfolio.

### layout.html
This file contains the main layout of my website. I have 3 Jinja blocks, one for the navbar and one for the main content. The title block and the navbar block changes content depending on which page the user is on. The main block contains the main content of the website. 

### drivers.html, constructors.html, races.html
These 3 templates generally have the same structure. I have a form in the first row that sends a POST request containing the desired year to be shown on the website; this is used to filter the standings by year. Below that is a table displaying the standings, as well as a link to the driver and the team that leads to a route showing their respective profiles. 

### constructor-profile.html, driver-profile.html
These templates provide a simple profile for the driver/constructor. It contains important information and statistics such as total points, wins, and championships. It uses a card div with an image that changes position from left to top depending on the size of the viewport. It also has a form dedicated to filtering the team/driver's standing per year. 

### app.py 
This file contains the logic for the entire web application. For the application, I made use of a bunch of imports, the most notable ones being ergast_py and newsapi, the main APIs for the project. After that, I initialize both APIs and create a function that createas a connection to my MySQL database. Let me go through each route one by one:

#### Homepage
After initializing my 2 APIs, I fetch important data such as the latest articles, and race results. Out of the race results, I use a function to create a list of dictionaries pertaining to the top 3 drivers of that race. After that, I created a function that checks if my database contains the latest race and updates the total points and wins of the teams and drivers. 

#### Driver Standings, Constructor Standings
These two routes follow the same structure; a GET request displays the standings depending on the year, and a POST request retrieves the year selected by the user. 

#### Driver Profile, Constructor Profile
Firstly, a database connection is established, which fetches the information about the driver/team as well as their picture; this is possible with the route parameters, which contain the id of the driver or team. If the database did not contain a picture for that entry, it displays a fallback picture of a generic driver or team. The data from the API and the database are then passed to the template to be displayed.

#### Races
In this route, I fetched the circuits and their winners during that season asynchronously; this approach was faster than retrieving the data sequentially. After that, the races are sorted by round, so that the final race results list contains the correct order of races within that season. The route takes in a POST method, which takes in a parameter of year; allowing the user to view the race winners per season.

#### Race Results
This route displays the race results of a specific race, given the year and round route parameters. Using the year and the round, I used the API to query for the race results for that race, which is then displayed to the template.

## Installation
1. Clone this repository 
2. Create Python virtual environment ```python3 -m venv venv```
3. Activate your virtual environment
4. Install the dependencies ```pip install -r requirements.txt```   