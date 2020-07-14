# summer2020-api
### An API that returns data on what I've done this summer. 
- Endpoints include :
      1. /api/v1/summer/books/all, which returns all the books I've read,
      2. /api/v1/summer/textbooks/all, which returns the textbooks I've read, and 
      3. /api/v1/summer/work/all, which returns the different companies I worked for. 

Additionally, as of July 14, this API supports filtering book and textbook requests by one ID and work requests by company name.

For example, /api/v1/summer/books?id=1 returns the second book I read and /api/v1/summer/work?company=Jam returns information on what I did at [joinjam.io](Jam).
