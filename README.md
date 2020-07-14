# summer2020-api
### An API that returns data on what I've done this summer. 
- Endpoints include : <br/>
      1. <strong>/api/v1/summer/books/all</strong>, which returns all the books I've read, <br/>
      2. <strong>/api/v1/summer/textbooks/all</strong>, which returns the textbooks I've read, and <br/>
      3. <strong>/api/v1/summer/work/all</strong>, which returns the different companies I worked for. 

Additionally, as of July 14, this API supports filtering book and textbook requests by one ID and work requests by company name.

For example, <strong>/api/v1/summer/books?id=1</strong> returns the second book I read and /api/v1/summer/work?company=Jam returns information on what I did at [Jam](https://www.joinjam.io).
