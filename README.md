# equity-extraction

- exclude buyer or sellers that are fed agencies or commercial bank
- just going to use LLC, etc. for corporate

For the purchasing, we capture corporate buying from individuals for the properties that are to be used as rentals upon the transaction. For the selling, we are also able to capture corporates’ selling of their rental properties to individual home buyers. Lastly, for holding, we track how long the SFR properties are owned by corporate landlords who do not residing on those premises (i.e. owner’s mailing address different from the property address).   

capture price diff for buying and selling compared to FMV, need parcel data for each year

*we are doing aggreggates, not tracking (but we can with cross join)

steps:
- data cleaning
- merge sales and parcel (can do left join, we only care ab sales but lets just do outer or left on parcel
)
- drop banks
- for all sales during the period, create a diff between sale and FMV col
- aggregate all purchases by corporates on the diff col
- aggreggate all inverse purchases on diff col
- merge the two above totals into a table
- create a rental price column, multiple FMV by .005
- aggreg rental price column for any parcels owned by corporate

-are rental earnings only from properties that were bought in the period?
concerns:
- 

NOTE: at this time, I only used sales data left joined with parcel data, altering the method required. It makes sense to use parcel data left joined with sales data instead- I just used what I had at the time.

METHOD:
- Spatial join sales_parcel to Atlanta neighborhoods
- Dropped row duplicates (there were some, not sure why at the moment)
- Drop govt institutions and banks
    - Govt identified by FEDERAL in name (Fannie and Freddie Mac appear to always include this for purchases/sales)
    - Banks identified by ['BANK', 'MORTGAGE', 'LENDING', 'LOAN', 'FINANCE', 'FUND', 'CREDIT', 'TRUST', 'SERVICES'] in their name
    - Dropped total ATL sale count from 52K -> 43K
- Identified corporates and created a flag column with [
    'LLC',
    'INC',
    'LLP',
    'L.L.C',
    'L.L.P',
    'I.N.C',
    'L L C',
    'L L P',
    'L P',
    'LTD',
    'CORP',
    'CORPORATION',
    'COMPANY',
    ' CO',
    'LIMITED',
    'PARTNERSHIP',
    'PARTNERSHIPS',
    'ASSOCIATION',
    'ASSOC'
] keywords
- Created a sales_diff column = SALES PRICE - FMV
- Created 4 columns for each sale: corp_bought_ind, ind_bought_ind, corp_sold_ind, ind_sold_ind based on whether or not GRANTEE and GRANTOR name was a corp
- Created a held_by_corp column indicating if the purchase resulted in corp ownership
- Calculated the years_held for each corp owned property by sorting the values on (ParcelID, Taxyr) and subtracting the year of the next sale IF the ParcelID matched (mask and shift); if a property was bought by a corp but never sold, I filled that with the max value for the time period (2018 - sale tax year); the sale data I had ended in 2018 for some reason- need to check that
- Calculated rental_price by FMV * .005 and multipled by years_held to get rental_sum (only for properties owned by corp)
- Created stats off of that (e.g. rental_price avg by aggreggating at neighborhood level and finding the mean)
- Mapped

QUESTIONS:
- How exactly did you integrate Open Refine into the methodology for FCS? Was that only to identify small, medium, and large investors?
- How did you calculate duration of ownership in the FCS paper if you weren't tracking by property?
- For rental income, do we want to include the full year when the property was bought/sold? So if the property was bought Dec 2020, are our calculations including 2020 rental income?
- I don't believe you are tracking buying then selling, rather just aggreggating any corp purchase from ind, and corp sale to ind; what impact might this have- for instance, corps may have bought a lot of properties before the study period. Then they go to sell during the study period. Sales will appear very high whereas buying activity only has the chance to occur during the study period without being impacted by prior circumstances. Calculating avg difference in price - fmv works since it normalizes for count, but the total sums could be skewed along with other factors may have not considered.
- We are counting all sales to corps as rental properties. People might have an issue with this. Although I think its good enough. I guess flipping activity would be the main issue.
- We are summing rental income from: "While properties are held by corporations as rentals; for those purchased
from individuals" (page 18 diagram); what about corp buying from corp? Likely those properties are still rentals.
- The length of the study period impacts the ratio of importance of buying, holding, and selling. If the study period is very long, holding will become larger and larger. This needs to be discussed.


ANATOMY OF PAPER:

METHODS:

Data processing:
- Sources of data (appending, some instances of missing parcel records); DeKalb excluded
- Data cleaning
- Geocoding to determine NSA
- Merging data
- Number of parcels, number of sales
- LUC = 101, Saveval = 0

Analysis:
- Dropping ADUs
- Drop parcels and sales where govt inst or banks are involved
- Identifying same owners for parcel and sales data
- Determine ownership scale of the owner of each parcel during that year on the neighborhood, city, and county level
    - Change in ownership by year (total prop owned by corp by size, ind for each year chart), graph showing slope of each on one
    - Top owners in Fulton (could potentially show where they own most parcels by neighborhood); take year where owner had most?
    - Top owners in ATL
    - Top owner concentrations in neighborhoods (careful of small neighorhoods)
    - Distribution of ownership size (plot) e.g. percent of owners with n properties - for 2022? Whatever year has highest; could agg over years, only select for corp?
    - Bins of ownership size by year (chart) - boxplot?
    - DURATION OF OWNERSHIP BY type??? HOW - have a flag for small, medium, and large investor; sum years held where flag is set true for each type (what about corp to corp sales tho); or keep counting until owner changes and agg based on owner size bin (omg bruh); held is a meaningless metric bc we are taking a sample?
- Determine scale of buying and selling activty for each buyer and seller in that year (some important data notes from sales) - TODO
    - Change in percent of transcations by corp size and overall (also break down for buying and selling)
    - Top buyers and sellers in Fulton, ATL, neighborhoods
    - Distribution of activity e.g. what percent of owners bought n properties
    - Bins of activity by year (chart) - boxplot
- Sale classification matrix
    - Distribution of sales
    - Distribution of sales by neighborhoods e.g. which properties had a lot of corps buying or selling in a year
- Agg of sales and purchases
    - By neighborhood for each year and agg
    - Significance test of diff agg between purchase and sell power of corp vs ind, per neighborhood
    - dist of salesprice - fmv paid by owner size
- Holding activity
    - By neighborhood
- Total measure (just agg)
    - broken down by only those sold which were bought during period, or all sales (includes purchasing before period)
    - broken down by small, medium, large investor? in city or neighborhood (both lol)?
- Total normalized measure (divided by median sale price)
    - 
- Burden measure (divided by yearly median income)
- How long until renting would overtake buying and selling?
- Neighborhood characteristics linked to equity loss (lol)
- neighborhood transcation metrics, number of transcations, number of unique as a percent of total, etc

- I don't believe you are tracking buying then selling, rather just aggreggating any corp purchase from ind, and corp sale to ind; what impact might this have- for instance, corps may have bought a lot of properties before the study period. Then they go to sell during the study period. Sales will appear very high whereas buying activity only has the chance to occur during the study period without being impacted by prior circumstances. Calculating avg difference in price - fmv works since it normalizes for count, but the total sums could be skewed along with other factors may have not considered. (we basically account for this by doing this year by year concentration metrics)

- We are summing rental income from: "While properties are held by corporations as rentals; for those purchased from individuals" (page 18 diagram); what about corp buying from corp? Likely those properties are still rentals. TODO - corp buying from corp should be included


RESULTS:
- want to understand corporate purachsing overall in Atlanta and compared to Fulton
- want to have a absolute and normalized measure of equity loss for each neighborhood in ATL
- how does metric compare to individual, what does it say about geospatial, is corporate power statistically significant
- is there a link between equity loss and neighborhood characteristics (regression)
- classify investors on a discrete or continuous scale
- want to understand the major factors of equity loss
- simulate how long until renting would become more important than buying and selling (for policy implications)
- 

Notes:
- We are counting all sales to corps as rental properties. People might have an issue with this. Although I think its good enough. I guess flipping activity would be the main issue.
- The length of the study period impacts the ratio of importance of buying, holding, and selling. If the study period is very long, holding will become larger and larger. This needs to be discussed.
- Limitation of using neighborhoods versus radii
- For rental income, do we want to include the full year when the property was bought/sold? So if the property was bought Dec 2020, are our calculations including 2020 rental income? Decision: we are not accounting for this as it should be normally distributed?