-------------------------------------
proj3 data sources
-------------------------------------

Most of the data is pulled from NYC open Data per the spec requirement

1) unbanked and underbanked populations in NYC by neighborhood
https://data.cityofnewyork.us/Business/Where-Are-the-Unbanked-and-Underbanked-in-New-York/v5w4-adxa

2) Broadband Adoption Basic Indicators
https://data.cityofnewyork.us/City-Government/Broadband-Adoption-Basic-Indicators/6wy6-6agj/

3) Neighborhood Conversions
https://www1.nyc.gov/site/planning/data-maps/nyc-population/geographic-reference.page
https://www1.nyc.gov/assets/planning/download/pdf/data-maps/nyc-population/census2010/ntas.pdf

4) School location by neighborhood
https://data.cityofnewyork.us/Education/2019-DOE-High-School-Directory/uq7m-95z8

5) NYC regents scores by school
https://data.cityofnewyork.us/Education/2014-15-2018-19-NYC-Regents-Exam-Public/2h3w-9uj9

-------------------------------------
Methodology
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
banking information, and school scores by neighborhood. I think that their
is a good opportunity to mine some interesting information.

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
