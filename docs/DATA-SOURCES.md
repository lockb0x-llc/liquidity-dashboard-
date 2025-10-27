#Here are the endpoints available for use as official financial and market data sources for the application.

---
Repo and Reverse Repo Operations
Repo, Reverse Repo and Propositions

GET
/api/rp/{operationType}/{method}/{status}/latest.{format}
Current date operations

GET
/api/rp/{operationType}/{method}/results/lastTwoWeeks.{format}
Operations within last two weeks

GET
/api/rp/{operationType}/{method}/results/last/{number}.{format}
Last n number of operations

GET
/api/rp/results/search.{format}
Filter operations

GET
/api/rp/reverserepo/propositions/search.{format}
Filter Reverse Repo propositions

--- 

Central Bank Liquidity Swaps Operations
U.S. Dollar and Non-U.S. Dollar



GET
/api/fxs/{operationType}/latest.{format}
Current date posted operations

GET
/api/fxs/{operationType}/last/{number}.{format}
Last n number of operations

GET
/api/fxs/{operationType}/search.{format}
Filter operations

GET
/api/fxs/list/counterparties.{format}
List of Counterparties

---
Reference Rates
Secured and Unsecured



GET
/api/rates/all/latest.{format}
Last As of Date from current date rates

GET
/api/rates/all/search.{format}
Filter rates

GET
/api/rates/secured/all/latest.{format}
Last As of Date from current date for Secured rates

GET
/api/rates/secured/{ratetype}/last/{number}.{format}
Last n number of Secured rates

GET
/api/rates/secured/{ratetype}/search.{format}
Filter Secured rates

GET
/api/rates/unsecured/all/latest.{format}
Last As of Date from current date for Unsecured rates

GET
/api/rates/unsecured/{ratetype}/last/{number}.{format}
Last n number of Unsecured rates

GET
/api/rates/unsecured/{ratetype}/search.{format}
Filter Unsecured rates

---
Securities Lending Operations
Securities Lending and Extensions



GET
/api/seclending/{operation}/results/{include}/latest.{format}
Current date operations

GET
/api/seclending/{operation}/results/{include}/lastTwoWeeks.{format}
Operations within last two weeks

GET
/api/seclending/{operation}/results/{include}/last/{number}.{format}
Last n number of operations

GET
/api/seclending/{operation}/results/{include}/search.{format}
Filter operations

---
System Open Market Account Holdings
SOMA Holdings (Please take note that Agency includes Agency Debts, MBS, and CMBS. Treasury includes Bills, Notes/Bonds, FRN, and TIPS.)



GET
/api/soma/asofdates/latest.{format}
Last As Of Date

GET
/api/soma/summary.{format}
Total by Security Types

GET
/api/soma/asofdates/list.{format}
List of As Of Dates

GET
/api/soma/agency/get/release_log.{format}
List of Release Dates for Agency Securities

GET
/api/soma/agency/get/asof/{date}.{format}
Agency Securities by As Of Date

GET
/api/soma/agency/get/cusip/{cusip}.{format}
Agency Securities by CUSIP

GET
/api/soma/agency/get/{holdingtype}/asof/{date}.{format}
Agency Securities by Holding Type and As Of Date

GET
/api/soma/agency/wam/agency debts/asof/{date}.{format}
Agency Debt Weighted Average Maturity by As Of Date

GET
/api/soma/tsy/get/release_log.{format}
List of Release Dates for Treasury Securities

GET
/api/soma/tsy/get/asof/{date}.{format}
Treasury Securities by As Of Date

GET
/api/soma/tsy/get/cusip/{cusip}.{format}
Treasury Securities by CUSIP

GET
/api/soma/tsy/get/{holdingtype}/asof/{date}.{format}
Treasury Securities by Holding Type and As Of Date

GET
/api/soma/tsy/wam/{holdingtype}/asof/{date}.{format}
Treasury Debt Weighted Average Maturity by Holding Type and As Of Date

GET
/api/soma/tsy/get/monthly.{format}
Monthly summary of Treasury Holdings

---
Treasury Securities Operations
Outrights and Prices Paid (Please take note that Prices Paid are included in operations detail when available)



GET
/api/tsy/{operation}/{status}/{include}/latest.{format}
Current date operations

GET
/api/tsy/{operation}/results/{include}/lastTwoWeeks.{format}
Operations within last two weeks

GET
/api/tsy/{operation}/results/{include}/last/{number}.{format}
Last n number of operations

GET
/api/tsy/{operation}/results/{include}/search.{format}
Filter operations