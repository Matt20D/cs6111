------------------------------------------------------------
Proj 3: Readme 
Matthew Duran (md3420)
Ethan Garry (epg2136)
------------------------------------------------------------
    --------------------------------------
    Directory Structure of proj2
    --------------------------------------

├── proj3/
    ├── readme.txt <-- You are reading this file 
    ├── mining.py 
    ├── integrated_data_final.csv
    ├── setup.sh* [Note: ensure that the shell file has executable permissions]   
    ├── run.sh* [Note: ensure that the shell file has executable permissions]   
    ├── requirements.txt

    ------------------------------------
    How to install and run our software
    ------------------------------------

    1) source setup.sh to install our package dependenciess
    2) ensure that integrated_data_final.csv is within the same dir
    3) Feel free to use run.sh to test, or of course use the command line
    
-------------------------------------
proj3 data sources
-------------------------------------

Most of the data is pulled from NYC open Data per the spec requirement

1) unbanked and underbanked populations in NYC by neighborhood
https://data.cityofnewyork.us/Business/Where-Are-the-Unbanked-and-Underbanked-in-New-York/v5w4-adxa
'why this data is collected': The dataset was commissioned by DCWP and is an aggregation of data 
collected by the Urban Institute for the "Unbanked" study.

2) Broadband Adoption Basic Indicators
https://data.cityofnewyork.us/City-Government/Broadband-Adoption-Basic-Indicators/6wy6-6agj/
why this data is collected': Key indicators of broadband adoption, service and infrastructure 
in New York City by NTA

3) Neighborhood Conversions
https://www1.nyc.gov/site/planning/data-maps/nyc-population/geographic-reference.page
https://www1.nyc.gov/assets/planning/download/pdf/data-maps/nyc-population/census2010/ntas.pdf

4) School location by neighborhood
https://data.cityofnewyork.us/Education/2019-DOE-High-School-Directory/uq7m-95z8
why this data is collected': This data is collected for the purposes of providing families and students with information about 
NYC DOE high schools for the purposes of admissions. Each record represents one high school. 


5) NYC regents scores by school
https://data.cityofnewyork.us/Education/2014-15-2018-19-NYC-Regents-Exam-Public/2h3w-9uj9
why this data is collected': To track the school level NYC results on NYS Regents Exams

-------------------------------------
Methodology and Interest in Dataset
-------------------------------------
The hard part was finding a way to link schoolwide data to other data sets
like broadband acceptance, and % underbanked.

%underbanked data is broken out by borough and sub-borough, which closely
matches the NTA districts in the broadband acceptance dataset. NYC breaks
their neighborhoods into Neighborhood Tabulation Area Names (NTA NAME).
However they may group multiple neighborhoods into an NTA group, such as
below: Carroll Gardens-Columbia Street-Red Hook. So I had to break up the
NTA groupings into three separate rows so that I could join the banking data
to the broadband data on said "sub-borough name".

Then, once I had those two aforementioned datasets linked I began to look at
the 2019 Department of Education NYC high school directory. Luckily, the
high school data set was also broken out by NTA so I did a simple join of
the previously defined dataset to the DOE one on their NTA.

Now I had to link in one final data set. The one previously defined was then
joined on the High School regents scores by school dbn. DBN is a unique
identifier for each school within a district within a borough. So this was
the easiest join of them all. NYC had regents data for 2014 - 2019,
but to prune the data I chose to utilize 2018 and 2019. Those dates nicely
match up with the timelines for the other datasets as well.

Now In that final join, some schools could have changed district, or whatnot
so an #N/A value I got in excel invalidated the whole row. I was able to
prune 12000 market baskets to about 8000. Lastly, I began eliminating all of
the columns that were present in the dataset and I kept 50 relevant ones out
of the 500. That number will also likely be pruned as I reduce the feature
space through interactions and discretization.

But that in a nutshell is the process undertaken to wrangle and produce this
dataset, and I seek to see any rules we can mine using access to internet,
banking information, and school scores by neighborhood. I think that there
is a good opportunity to mine some interesting information. We are not trying
to manipulate the data to mine rules we think exists ("the bad connotation of 
data mining"), rather we will like to see if we can extract any interesting 
information relating wealth, access to internet, nyc geography, and school
test scores.

-------------------------------------
Variable Explanation
-------------------------------------
School DBN: code used by the NYC Department of Education to uniquely identify schools
boro: NYC Boro Name
Neighborhood: New York City neighborhood name based on US Census geographic unit
School Name: NYC School Name
School Type: A classification of an organization describing the type of educational setting.
School Level: The name of a general grade classification similar to school level.
Regents Exam: The name of a Regents Exam
Year: The year for which the Regents data is reported
Mean Score: The mean score received of all students tested on the specified Regents exam for the school, and year being reported
Percent Scoring Below 65: The percentage of students that took the specified Regents exam for the school, and year being reported who scored below a 65
Percent Scoring 65 or Above: The percentage of students that took the specified Regents exam for the school, and year being reported who scored a 65 or above
Percent Scoring 80 or Above: The percentage of students that took the specified Regents exam for the school, and year being reported who scored an 80 or above
number_AP_CLASSES: Advanced Placement courses offered by the school, 
listed under Academics in the HS Directory. This has been discretized into ranges.
num_total_ways_to_school: including number of bus and subway lines near the school.
For each school we totaled the number of ways to get to a particular school using mass transit.
total_students: Total number of students enrolled in the school as of the audited register in October 2016
start_time: Start time for a typical 9th grade student 
end_time: End time for a typical 9th grade student 
graduation_rate: At the end of the 2015-16 school year, the percent of students who graduated "on time" by earning a diploma four years after they entered 9th grade
attendance_rate: Daily attendance rate of the school's students in 2015-16 school year
college_career_rate: At the end of the 2015-16 school year, the percent of students who graduated from high school four years after they entered 9th grade and then 
enrolled in college, a vocational program, or a public service program within six months of graduation
Unbanked 2013: Percent of residencts having no access to banking or other personal financial services in 2013
Underbanked 2013: Percent of residencts having very limited access to or substantive obstacles to attaining banking or other personal financial services in 2013
% Poor 2013: Percent of poor residents in 2013
% Foreign born 2013: Percent of foreign born residents in 2013
Median income 2013: Median household income in 2013
Unemployment 2013: Unemployment rate in 2013
Total Population: The total number of persons based on 5 year American Community Survey estimates.
Home Broadband Adoption (Percentage of Households): Percentage of Households with a broadband internet service subscription by neighborhood.
Home Broadband Adoption: Percentage of Households with a broadband internet service subscription, catagorized by quartiles.
Mobile Broadband Adoption (Percentage of Households): Percentage of Households in the neighborhood with a cellular data plan internet service subscription.
Mobile broadband adoption: Percentage of Households with a cellular data plan, categorized by quartiles 
Percentage of Blocks without a Commercial Fiber Provider by Quartiles: The percentage of census blocks in the reported to have no commercial fiber internet service providers available by quartiles.
Available Free Public Wi-Fi: Indicates if a public Wi-Fi access point or points are available in a pedestrian corridor within the specified NTA.
Number of Public Computer Centers with free public Wi-Fi: Indicates the number of public computer centers that offer public Wi-Fi  within the specified NTA.

Note: Most of our data was numeric in nature, so we needed to discretize it into buckets in order to extract meaningful data. Further
Since the Apriori Algorithm involves counts, and returns rules based as such we renamed the items within a basket to be the 
range, or observation type concatenated with the column header. This allows for maximum readability of the rules, and with the feature
description above we can analyze our resulting mined ruleset.

For example:
    1) 60-69_mean_score: mean score for a paticular regents was between 60 and 69 for a school
    2) 26%-50%_of_class_FAILED_TEST: between 26 and 50% of the class failed the regents
    3) <10%_unbanked: less than 10% of the area is unbanked, implying that the neighborhood is probably wealthy.

-------------------------------------
How To reproduce the Dataset
-------------------------------------

*) retrieve (2), and clean the NTA codes, by breaking them up into single
neighborhoods.

*) Join (1) to (2) on NTA

*) Join (1,2) to (4) on neighborhood or NTA, but there will likely be some
cleaning to do (for poorly kept data).

*) Join (1,2,4) to (5) on School DBN.

*) Filter (1,2,4,5) on year to 2018-2019, and clean out a majority of the
features.

*) Delete NTA column, Number of busways, and Number of subways columns.

-------------------------------------
Final File
-------------------------------------
integrated_data_final.csv will contain the union of the most interesting
columns of data from the above 5 sources. This was not a trivial process.
Took about 2 days of data wrangling and sourcing 5 different NYC open
datasets.

-------------------------------------
A Priori Implementation
-------------------------------------

