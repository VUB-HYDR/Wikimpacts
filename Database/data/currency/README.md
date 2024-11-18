In the Wikimpacts 1.0 database, we adjusted all monetary damage values for inflation to 2024. The original data source is [here](https://www.minneapolisfed.org/about-us/monetary-policy/inflation-calculator/consumer-price-index-1800-). The file `inflation_Index_original.csv` contains data directly from this website, while `inflation_Index_2024.csv` has been adjusted to a base year of 2024, which we applied in our process.

For currency conversion, we converted the majority of non-USD currencies. The count below reflects the number of currency records in the Wikimpacts 1.0 database. We obtained the original conversion rates on a monthly scale from [this source](https://fx.sauder.ubc.ca/fxdata.php), stored in `Database/data/Currency_Conversion.xlsx`. We then aggregated these to yearly rates in `Database/data/Currency_conversion_yearly_averages.xlsx`. For conversion, we used the yearly rate, and for currencies predating the years available in our table, we applied a constant rate from the earliest available year.
| Currency | Count |
|----------|-------|
| EUR      | 151   |
| AUD      | 186   |
| GBP      | 98    |
| INR      | 84    |
| CAD      | 144   |
| NZD      | 43    |
| JPY      | 252   |
| PHP      | 158   |
| CNY      | 118   |
| VND      | 51    |
| KRW      | 13    |
| MXN      | 57    |
| NTD      | 20    |
| BRL      | 10    |
