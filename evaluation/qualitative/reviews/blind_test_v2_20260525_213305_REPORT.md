# Blind Test V2 — Analysis Report

- responses : blind_test_v2_20260525_213305_responses.json
- key       : blind_test_v2_20260525_213305_KEY.md
- data      : blind_test_v2_20260525_213305_data.json
- queries with answers: 15; total rated rows: 133; cannot_evaluate: 1

## Per encoder × metric

| encoder | same_dynamic | same_regime | same_surprise | mental_precedent |
|---|---|---|---|---|
| **contrastive_v2** | 1.59 (med 1.0, n=44) | 3.16 (med 3.0, n=44) | 3.52 (med 4.0, n=44) | 2.07 (med 2.0, n=44) |
| **concat_eq** | 2.13 (med 2.0, n=45) | 4.18 (med 5.0, n=45) | 3.93 (med 4.0, n=45) | 2.80 (med 3.0, n=45) |
| **random** | 1.24 (med 1.0, n=45) | 2.38 (med 2.0, n=45) | 3.02 (med 3.0, n=45) | 1.56 (med 1.0, n=45) |

### High (≥4) / Low (≤2) per encoder × metric

| encoder | metric | hi | lo | n |
|---|---|---|---|---|
| contrastive_v2 | same_dynamic | 4 | 38 | 44 |
| contrastive_v2 | same_regime | 17 | 21 | 44 |
| contrastive_v2 | same_surprise | 23 | 9 | 44 |
| contrastive_v2 | mental_precedent | 7 | 31 | 44 |
| concat_eq | same_dynamic | 11 | 30 | 45 |
| concat_eq | same_regime | 34 | 5 | 45 |
| concat_eq | same_surprise | 35 | 7 | 45 |
| concat_eq | mental_precedent | 15 | 22 | 45 |
| random | same_dynamic | 0 | 44 | 45 |
| random | same_regime | 7 | 30 | 45 |
| random | same_surprise | 18 | 15 | 45 |
| random | mental_precedent | 1 | 42 | 45 |

## Statistical tests

### Kruskal-Wallis (3-way) per metric

| metric | H | p | significant |
|---|---|---|---|
| same_dynamic | 11.976 | 0.0025 | **p<0.05** |
| same_regime | 36.725 | 0.0000 | **p<0.05** |
| same_surprise | 9.575 | 0.0083 | **p<0.05** |
| mental_precedent | 22.086 | 0.0000 | **p<0.05** |

### Pairwise Mann-Whitney U (two-sided)

| metric | pair | U | p | sig |
|---|---|---|---|---|
| same_dynamic | contrastive_v2 vs concat_eq | 786.0 | 0.0637 | . |
| same_dynamic | contrastive_v2 vs random | 1154.0 | 0.0924 | . |
| same_dynamic | concat_eq vs random | 1374.0 | 0.0007 | ** |
| same_regime | contrastive_v2 vs concat_eq | 588.5 | 0.0005 | ** |
| same_regime | contrastive_v2 vs random | 1300.5 | 0.0072 | ** |
| same_regime | concat_eq vs random | 1728.5 | 0.0000 | ** |
| same_surprise | contrastive_v2 vs concat_eq | 797.5 | 0.1005 |  |
| same_surprise | contrastive_v2 vs random | 1175.0 | 0.1196 |  |
| same_surprise | concat_eq vs random | 1376.0 | 0.0025 | ** |
| mental_precedent | contrastive_v2 vs concat_eq | 687.5 | 0.0105 | ** |
| mental_precedent | contrastive_v2 vs random | 1247.5 | 0.0223 | ** |
| mental_precedent | concat_eq vs random | 1555.5 | 0.0000 | ** |

## Hard Failures (mean of 4 metrics ≤ 2.0)  —  45 candidates

### Q2 HPE 2020-05-21 → label A: GWW 2019-01-24  (Industrials)
- encoders: **random**  | mean=1.00
- same_dynamic=1  same_regime=1  same_surprise=1  mental_precedent=1
- notes: _HPE colpita da lockdown, GWW trimestrale positiva pre-covid_
- summary: Grainger reported strong financial results for the 2018 fourth quarter and full year, with sales and margins exceeding expectations, driven by U.S. segment volume growth and cost reductions across the organization. Chairman DG Macpherson expressed confidence in maintaining high operating margins and driving continued growth in 2019.
- text[:600]: > Exhibit GRAINGER REPORTS RESULTS FOR THE 2018 FOURTH QUARTER AND FULL YEAR Full year sales increase 8 percent; reported operating margin of 10 percent; adjusted operating margin of 12 percent; company provides 2019 guidance 2018 Financial Highlights • Sales of $11.2 billion, up 8 percent • Reported operating earnings of $1.2 billion, up 12 percent; adjusted operating earnings of $1.3 billion, up 17 percent • Reported operating margin of 10.3 percent, up 40 basis points; adjusted operating margin of 12.0 percent, up 100 basis points • Reported EPS of $13.73, up 37 percent; adjusted EPS of $16.7

### Q2 HPE 2020-05-21 → label G: EXPD 2019-11-05  (Industrials)
- encoders: **random**  | mean=1.00
- same_dynamic=1  same_regime=1  same_surprise=1  mental_precedent=1
- summary: Expeditors International declared a semi-annual cash dividend of $0.50 per share, driven by strong financial performance, to be paid on December 16, 2019, to shareholders of record as of December 2, 2019; the tone is confident reflecting the company's positive outlook.
- text[:600]: > expd-ex991_7.htm Exhibit 99.1 PRESS RELEASE By: Expeditors International of Washington, Inc. 1015 Third Avenue, Suite 1200 Seattle, Washington 98104 CONTACTS: Jeffrey S. Musser Bradley S. Powell Geoffrey Buscher President and Chief Executive Officer Senior Vice President and Chief Financial Officer Director - Investor Relations (206) 674-3433 (206) 674-3412 (206) 892-4510 FOR IMMEDIATE RELEASE _____________________________________________________________________________________________ EXPEDITORS ANNOUNCES SEMI-ANNUAL CASH DIVIDEND OF $0.50 SEATTLE, WASHINGTON – November 5, 2019, Expeditors In

### Q12 NDSN 2020-05-20 → label D: FICO 2018-07-26  (Information Technology)
- encoders: **random**  | mean=1.00
- same_dynamic=1  same_regime=1  same_surprise=1  mental_precedent=1
- summary: FICO reported third-quarter fiscal 2018 earnings of $1.04 per share with revenues of $260 million, up from $231 million in the prior year, driven by record revenues and a transition to more recurring business models. The company remains optimistic about its future prospects as it executes on its strategic initiatives.
- text[:600]: > FICO Announces Earnings of $1.04 per Share for Third Quarter Fiscal 2018 Revenues of $260 million vs. $231 million in prior year SAN JOSE, Calif., July 26, 2018 /PRNewswire/ -- FICO (NYSE:FICO), a leading predictive analytics and decision management software company, today announced results for its third fiscal quarter ended June 30, 2018. Third Quarter Fiscal 2018 GAAP Results Net income for the quarter totaled $32.4 million, or $1.04 per share, versus $25.2 million, or $0.78 per share, reported in the prior year period. Net cash provided by operating activities for the quarter was $85.1 mill

### Q9 CPB 2021-09-01 → label H: ROK 2022-01-27  (Industrials)
- encoders: **contrastive_v2**  | mean=1.25
- same_dynamic=1  same_regime=2  same_surprise=1  mental_precedent=1
- summary: Rockwell Automation reported strong first quarter fiscal 2022 results with record quarterly orders of $2.5 billion, up over 40% year-over-year, driven by robust sales growth across all business segments despite supply chain challenges. The company remains optimistic about the year ahead, reaffirming its guidance for significant sales and earnings growth while emphasizing continued execution in a dynamic environment.
- text[:600]: > Document Exhibit 99 1201 S. Second Street Milwaukee, WI 53204 USA News Release Contact Marci Pelzer Media Relations Rockwell Automation 414.382.5679 Jessica Kourakos Investor Relations Rockwell Automation 414.382.8510 Rockwell Automation Reports First Quarter 2022 Results • Record quarterly orders of $2.5 billion, up over 40% year over year • Reported sales up 18.7% year over year; organic sales up 16.8% • Acquisitions contributed 2.6% to reported sales growth • Total ARR up over 50% with recent Plex acquisition; Organic ARR up double digits • Q1 Diluted EPS of $2.05 and Adjusted EPS of $2.14 

### Q13 MMM 2019-04-25 → label B: PEG 2023-08-01  (Utilities)
- encoders: **random**  | mean=1.25
- same_dynamic=1  same_regime=2  same_surprise=1  mental_precedent=1
- notes: _Notizie opposte, tassi e grafici non allineati_
- summary: PSEG reported strong second-quarter earnings with net income of $591 million and non-GAAP operating earnings of $351 million, up significantly from the previous year due to growth in regulated operations and higher average hedged prices. The company remains optimistic, re-affirming its full-year 2023 guidance range of $3.40 to $3.50 per share while highlighting ongoing investments in electric and natural gas infrastructure.
- text[:600]: > Public Service Enterprise Group 80 Park Plaza Newark, NJ 07102 CONTACTS: Media Relations Investor Relations Marijke Shugrue Carlotta Chan 908-531-4253 973-430-6565 Marijke.Shugrue@pseg.com Carlotta.Chan@pseg.com PSEG Announces Second Quarter 2023 Results $1.18 Per Share Net Income $0.70 Per Share Non-GAAP Operating Earnings Re-Affirms Full-Year 2023 Non-GAAP Operating EPS Guidance Range of $3.40 - $3.50 (NEWARK, N.J. – August 1, 2023) Public Service Enterprise Group (NYSE: PEG) reported second quarter 2023 Net Income of $591 million, or $1.18 per share, compared to Net Income of $131 million, 

### Q13 MMM 2019-04-25 → label C: DVN 2021-02-17  (Energy)
- encoders: **random**  | mean=1.25
- same_dynamic=1  same_regime=2  same_surprise=1  mental_precedent=1
- summary: Devon Energy Corporation reported strong financial and operational results for the fourth quarter and full year 2020, highlighting industry-first variable dividends and improved well productivity, particularly in the Delaware Basin. The company's CEO expressed confidence in its portfolio and strategy, emphasizing disciplined capital spending and a focus on free cash flow generation despite market uncertainties.
- text[:600]: > Devon Energy Corporation 333 West Sheridan Avenue Oklahoma City, OK 73102-5015 Devon Energy Reports Fourth-Quarter and Full-Year 2020 Financial and Operational Results OKLAHOMA CITY – Feb. 16, 2021 – Devon Energy Corp. (NYSE: DVN) today reported financial and operational results for the fourth quarter and full year 2020. On Jan. 7, 2021, Devon closed its merger with WPX Energy. Results discussed within this release represent legacy Devon operations and do not include amounts related to WPX unless specified. Supplemental financial tables, pro forma information combining certain Devon and WPX re

### Q13 MMM 2019-04-25 → label D: TAP 2022-05-03  (Consumer Staples)
- encoders: **contrastive_v2**  | mean=1.25
- same_dynamic=1  same_regime=2  same_surprise=1  mental_precedent=1
- summary: Molson Coors Beverage Company reported strong first-quarter results with double-digit growth in both top and bottom lines, driven by positive net pricing, favorable sales mix, and financial volume growth, particularly in European markets. The company remains optimistic about its revitalization plan and reaffirms 2022 guidance for continued top and bottom-line growth despite inflationary pressures.
- text[:600]: > false000002454500000245452022-05-032022-05-030000024545dei:FormerAddressMember2022-05-032022-05-030000024545tap:ClassACommonStockParValue001Member2022-05-032022-05-030000024545tap:One25SeniorNotesDue2024Member2022-05-032022-05-030000024545tap:ClassBCommonStockParValue001Member2022-05-032022-05-03 Molson Coors Beverage Company Reports 2022 First Quarter Results Molson Coors Delivers First Quarter Double-Digit Top and Bottom-Line Growth with Highest Above Premium Mix Since the 2016 MillerCoors Acquisition Company Reaffirms 2022 Guidance for Top and Bottom-Line Growth, Continuing to Deliver on it

### Q13 MMM 2019-04-25 → label F: ESS 2020-08-03  (Real Estate)
- encoders: **random**  | mean=1.25
- same_dynamic=1  same_regime=1  same_surprise=2  mental_precedent=1
- summary: Essex Property Trust, Inc. reported its financial results for the three and six months ended June 30, 2020, highlighting strong performance driven by robust rental income and occupancy rates; the press release maintains a confident tone regarding future prospects.
- text[:600]: > Item 2.02. Results of Operations and Financial Condition. On August 3, 2020, Essex Property Trust, Inc. (the “Company”) issued a press release and supplemental information announcing the Company’s financial results for the three and six months ended June 30, 2020. The Company has posted a copy of the press release and supplemental information on the Company’s website at www.essex.com. A copy of the press release and supplemental information is attached hereto as Exhibit 99.1 and incorporated by reference herein. The information in this report (including Exhibit 99.1) is being furnished pursuan

### Q15 URI 2020-04-29 → label H: DHR 2023-01-24  (Health Care)
- encoders: **random**  | mean=1.25
- same_dynamic=1  same_regime=2  same_surprise=1  mental_precedent=1
- summary: Danaher Corporation reported strong fourth-quarter and full-year 2022 results, with net earnings up 25% year-over-year and core revenue growth of 7.5%, driven by broad-based strength across its portfolio. The CEO expressed confidence in the company's future, citing its leading portfolio, Danaher Business System, and strong balance sheet as key factors for generating sustainable long-term shareholder value.
- text[:600]: > Document Exhibit 99.1 DANAHER REPORTS FOURTH QUARTER AND FULL YEAR 2022 RESULTS WASHINGTON, D.C., January 24, 2023 -- Danaher Corporation (NYSE: DHR) (the “Company”) today announced results for the fourth quarter and full year 2022. All results in this release reflect only continuing operations unless otherwise noted. Net earnings refers to net earnings attributable to common shareholders. For the quarter ended December 31, 2022, net earnings were $2.2 billion, or $2.99 per diluted common share which represents a 25.0% year-over-year increase from the comparable 2021 period. Non-GAAP adjusted 

### Q2 HPE 2020-05-21 → label I: SMCI 2021-11-02  (Information Technology)
- encoders: **contrastive_v2**  | mean=1.50
- same_dynamic=2  same_regime=2  same_surprise=1  mental_precedent=1
- summary: Supermicro reported first quarter fiscal year 2022 financial results with a 35% year-over-year revenue growth, exceeding $1 billion for the second consecutive quarter, driven by strong design win momentum and shipment growth to key global customers in various markets. The company remains optimistic about future growth, projecting significant increases in net sales and earnings per share for the upcoming quarters despite ongoing supply chain challenges.
- text[:600]: > Document Exhibit 99.1 Supermicro Announces First Quarter Fiscal Year 2022 Financial Results SAN JOSE, Calif. -- November 2 , 2021 (BUSINESS WIRE) -- Super Micro Computer, Inc. (Nasdaq: SMCI) , a global leader in high-performance, high-efficiency server and storage technology and green computing, today announced financial results for its first quarter of fiscal year 2022 ended September 30, 2021. First Quarter Fiscal Year 2022 Highlights • Net sales of $1.03 billion versus $1.07 billion in the fourth quarter of fiscal year 2021 and $762 million in the same quarter of last year. • Gross margin o

### Q4 ALGN 2019-04-24 → label D: LIN 2020-05-07  (Materials)
- encoders: **random**  | mean=1.50
- same_dynamic=1  same_regime=1  same_surprise=3  mental_precedent=1
- notes: _Contesti macro opposti e trend grafici speculari_
- summary: Linde reported strong first-quarter 2020 financial results, including a 26% increase in operating cash flow and robust balance sheet liquidity, driven by improved pricing and operational efficiency despite a 1% decrease in sales due to the COVID-19 pandemic. CEO Steve Angel expressed confidence in the company's ability to create shareholder value through its resilient business model and opportunities to mitigate economic challenges.
- text[:600]: > lin_ex991 Exhibit 99.1 Press Release Linde Reports First-Quarter 2020 Results Financial Highlights ➢ Strong operating cash flow of $1.3 billion, up 26% versus prior year ➢ Robust balance sheet with ample liquidity for growth opportunities ➢ Operating profit of $0.7 billion, up 20% versus prior year; adjusted operating profit of $1.4 billion up 11% ➢ Operating profit margin up 210 bps, adjusted operating profit margin up 240 bps versus prior year ➢ EPS of $1.07 up 35% versus prior year, adjusted EPS of $1.89 up 12% Guildford, UK, May 7, 2020 – Linde plc (NYSE: LIN; FWB: LIN) today reported firs

### Q6 EQR 2024-01-30 → label G: MAA 2024-02-07  (Real Estate)
- encoders: **concat_eq**  | mean=1.50
- same_dynamic=1  same_regime=2  same_surprise=2  mental_precedent=1
- summary: MAA reported fourth-quarter and full-year 2023 results with Core FFO ahead of expectations due to stable employment conditions and positive migration trends, despite new apartment supply impacting rent growth. The company remains optimistic about improving rent growth in late 2024 as the volume of new deliveries is expected to decline.
- text[:600]: > TABLE OF CONTENTS Earnings Release 3 Financial Highlights 8 Consolidated Statements of Operations/Share and Unit Data 9 Consolidated Balance Sheets 10 Reconciliation of Non-GAAP Financial Measures 11 Non-GAAP Financial Measures 14 Other Key Definitions 15 Portfolio Statistics S-1 Components of Net Operating Income/Components of Same Store Portfolio Property Operating Expenses S-3 Multifamily Same Store Portfolio NOI Contribution Percentage S-4 Multifamily Same Store Portfolio Comparisons S-5 Multifamily Development Pipeline/Multifamily Lease-up Communities/Multifamily Interior Redevelopment Pi

### Q9 CPB 2021-09-01 → label B: CTVA 2023-08-03  (Materials)
- encoders: **random**  | mean=1.50
- same_dynamic=1  same_regime=3  same_surprise=1  mental_precedent=1
- notes: _Settori differenti, tassi ed eventi non allineati_
- summary: Corteva, Inc. reported its consolidated financial results for the quarter ended June 30, 2023, showing strong performance despite challenges in the agricultural sector; the company cited favorable crop conditions and robust demand as key drivers of its success. The tone is cautiously optimistic, highlighting both achievements and underlying market factors influencing the results.
- text[:600]: > Item 2.02 Results of Operations and Financial Condition On August 3, 2023, Corteva, Inc. (the "Company") announced its consolidated financial results for the quarter ended June 30, 2023. A copy of the Company’s press release and financial statement schedules are furnished herewith on Form 8-K as Exhibits 99.1 and 99.2, respectively. The information contained in this report, including Exhibits 99.1 and 99.2, is being furnished and shall not be deemed “filed” for purposes of Section 18 of the Securities Exchange Act of 1934, as amended (the “Exchange Act”), or otherwise subject to the liability 

### Q9 CPB 2021-09-01 → label D: PSX 2019-04-30  (Energy)
- encoders: **contrastive_v2**  | mean=1.50
- same_dynamic=1  same_regime=2  same_surprise=2  mental_precedent=1
- summary: Phillips 66 reported first-quarter earnings of $204 million, reflecting a diversified portfolio's resilience despite a weak market environment, with key achievements including high Chemicals segment utilization and significant shareholder returns. Chairman Greg Garland expressed confidence in the company’s growth projects and dedication to operating excellence, while acknowledging challenges such as unplanned refinery downtime that impacted performance.
- text[:600]: > Exhibit Phillips 66 Reports First-Quarter Earnings of $204 Million (Adjusted Earnings of $187 Million) Exhibit 99.1 Phillips 66 Reports First -Quarter Earnings of $204 Million or $0.44 Per Share Adjusted earnings of $187 million or $0.40 per share Highlights • Returned $708 million to shareholders through dividends and share repurchases • Achieved 98% O&P capacity utilization in Chemicals • Delivered record utilization at Sweeny fractionator and Freeport LPG export facility • Advanced several large-scale Midstream growth projects • Executed major turnaround program impacting five refineries • 

### Q9 CPB 2021-09-01 → label F: DRI 2020-06-25  (Consumer Discretionary)
- encoders: **random**  | mean=1.50
- same_dynamic=2  same_regime=1  same_surprise=2  mental_precedent=1
- summary: Darden Restaurants reported a significant decline in sales due to the closure of dining rooms during the pandemic, with total sales decreasing by 43.0% in the fourth quarter of fiscal 2020 compared to the previous year. Despite the challenges, the company attributes its resilience to its strong scale and culture, which enabled quick adaptation and innovation, positioning it well for future market share gains as the industry recovers.
- text[:600]: > NEWS RELEASE Exhibit Exhibit 99.1 Darden Restaurants Reports Fiscal 2020 Fourth Quarter and Full Year Results; And Provides Fiscal 2021 First Quarter Outlook ORLANDO, Fla., June 25, 2020 /PRNewswire/ -- Darden Restaurants, Inc., (NYSE:DRI) today reported its financial results for the fourth quarter and fiscal year ended May 31, 2020 , which included a 53rd week of operations compared to 52 weeks last year. Statement from Gene Lee, CEO. The strategy we put in place five years ago helped us successfully navigate one of the most challenging periods in our Company’s history. When our dining rooms 

### Q11 URI 2021-04-28 → label C: FCX 2022-10-20  (Materials)
- encoders: **random**  | mean=1.50
- same_dynamic=1  same_regime=1  same_surprise=3  mental_precedent=1
- summary: Freeport-McMoRan reported strong third-quarter and year-to-date 2022 results, with copper and gold sales volumes above guidance due to robust production performance; however, unit net cash costs were slightly higher than expected. The company remains optimistic about its long-term market fundamentals and is confident in its strategy despite near-term uncertainties, as evidenced by significant debt retirements and a solid balance sheet.
- text[:600]: > Document Freeport-McMoRan Reports Third-Quarter and Nine-Month 2022 Results • Strong production performance; copper and gold sales volumes above July 2022 guidance • Unit net cash costs were 5% above July 2022 guidance • Solid balance sheet, liquidity and financial flexibility • Significant debt retirements through open-market transactions • Published updated climate report ▪ Net income attributable to common stock in third-quarter 2022 totaled $404 million, $0.28 per share, and adjusted net income attributable to common stock totaled $375 million, $0.26 per share, after excluding net credits 

### Q12 NDSN 2020-05-20 → label F: TRGP 2024-08-01  (Energy)
- encoders: **random**  | mean=1.50
- same_dynamic=1  same_regime=2  same_surprise=1  mental_precedent=2
- notes: _Settori e notizie distanti, trend finali positivi_
- summary: Targa Resources Corp. reported record second-quarter 2024 results with adjusted EBITDA reaching $984.3 million, driven by higher volumes across its Gathering and Processing and Logistics and Transportation systems, and announced a new $1 billion share repurchase program, signaling confidence in future growth.
- text[:600]: > 811 Louisiana, Suite 2100 Houston, TX 77002 713.584.1000 Targa Resources Corp. Reports Record Second Quarter 2024 Results and Increases Full Year 2024 Outlook HOUSTON – August 1, 2024 - Targa Resources Corp. (NYSE: TRGP) (“TRGP,” the “Company” or “Targa”) today reported second quarter 2024 results. Second quarter 2024 net income attributable to Targa Resources Corp. was $298.5 million compared to $329.3 million for the second quarter of 2023. The Company reported adjusted earnings before interest, income taxes, depreciation and amortization, and other non-cash items (“adjusted EBITDA”) (1) of 

### Q12 NDSN 2020-05-20 → label I: EXR 2022-08-02  (Real Estate)
- encoders: **contrastive_v2**  | mean=1.50
- same_dynamic=1  same_regime=2  same_surprise=2  mental_precedent=1
- notes: _Grafici del tutto speculari, tassi ed eventi opposti_
- summary: Extra Space Storage Inc. reported strong second-quarter results with significant increases in net income, FFO, and occupancy rates, driven by robust same-store revenue growth and active external growth initiatives. The company's CEO expressed confidence in its diversified portfolio expansion and continued accretive investments, maintaining an optimistic tone for future performance.
- text[:600]: > Document Exhibit 99.1 Extra Space Storage Inc. PHONE (801) 365-4600 2795 East Cottonwood Parkway, Suite 300 Salt Lake City, Utah 84121 www.extraspace.com FOR IMMEDIATE RELEASE Extra Space Storage Inc. Reports 2022 Second Quarter Results SALT LAKE CITY, August 2, 2022 — Extra Space Storage Inc. (NYSE: EXR) (the “Company”), a leading owner and operator of self-storage facilities in the United States and a member of the S&P 500, announced operating results for the three and six months ended June 30, 2022. Highlights for the three months ended June 30, 2022: • Achieved net income attributable to c

### Q13 MMM 2019-04-25 → label H: AZO 2023-05-23  (Consumer Discretionary)
- encoders: **contrastive_v2**  | mean=1.50
- same_dynamic=1  same_regime=3  same_surprise=1  mental_precedent=1
- summary: AutoZone reported a 5.8% increase in net sales and a 1.9% rise in same-store sales for its third quarter, driven by the dedication of its employees to superior customer service. The company remains optimistic despite weaker-than-expected March sales, expressing confidence in its ongoing performance.
- text[:600]: > EdgarFiling EXHIBIT 99.1 AutoZone 3rd Quarter Same Store Sales Increase 1.9%; EPS Increases to $34.12 MEMPHIS, Tenn., May 23, 2023 (GLOBE NEWSWIRE) -- AutoZone, Inc. (NYSE: AZO) today reported net sales of $4.1 billion for its third quarter (12 weeks) ended May 6, 2023, an increase of 5.8% from the third quarter of fiscal 2022 (12 weeks). Domestic same store sales, or sales for stores open at least one year, increased 1.9% for the quarter. “I would like to congratulate and thank our entire organization for delivering solid earnings in our third fiscal quarter. The hard work of our AutoZoners a

### Q15 URI 2020-04-29 → label D: COP 2021-08-03  (Energy)
- encoders: **random**  | mean=1.50
- same_dynamic=1  same_regime=2  same_surprise=1  mental_precedent=2
- summary: ConocoPhillips delivered strong second-quarter 2021 financial results with earnings of $2.1 billion, driven by higher realized prices and volumes following the company's recent 10-year market update that reaffirmed its commitment to the energy transition while maintaining sector-leading returns on capital. The CEO expressed confidence in the company’s multi-year plan and resilience, emphasizing its unique position to deliver through industry price cycles.
- text[:600]: > ConocoPhillips Delivers Strong Second-Quarter 2021 Financial and Operational Results Following Recent 10-Year Market Update Reported earnings of $2.1 billion; adjusted earnings of $1.7 billion. Generated cash provided by operating activities of $4.3 billion; cash from operations of $4.0 billion. Produced 1,547 MBOED excluding Libya. HOUSTON--(BUSINESS WIRE)--August 3, 2021--ConocoPhillips (NYSE: COP) today reported second-quarter 2021 earnings of $2.1 billion, or $1.55 per share, compared with second-quarter 2020 earnings of $0.3 billion, or $0.24 per share. Excluding special items, second-qua

### Q1 COHR 2020-08-13 → label I: OXY 2022-02-24  (Energy)
- encoders: **random**  | mean=1.75
- same_dynamic=1  same_regime=1  same_surprise=4  mental_precedent=1
- summary: Occidental Petroleum reported strong fourth-quarter 2021 earnings, exceeding guidance and setting new operational records, driven by higher commodity prices and efficient production. The company also announced a new shareholder return framework and significant debt reduction targets, positioning itself for continued financial improvement in 2022.
- text[:600]: > Document PRESS RELEASE Occidental Announces 4th Quarter 2021 Results • Announced new shareholder return framework and additional debt reduction target • Earnings per share of $1.37 per diluted share and adjusted earnings per share of $1.48 per diluted share • Cash flow from continuing operations of $3.2 billion and cash flow from continuing operations, before working capital of $3.9 billion • Capital spending of $937 million, resulting in record free cash flow, excluding working capital of over $2.9 billion • Reduced debt maturities by $2.2 billion through debt tender and 2022 maturity call pr

### Q2 HPE 2020-05-21 → label F: FDX 2020-09-15  (Industrials)
- encoders: **random**  | mean=1.75
- same_dynamic=1  same_regime=4  same_surprise=1  mental_precedent=1
- notes: _Settori opposti: HPE bloccata, FDX spinta dall'e-commerce_
- summary: FedEx Corp. reported strong first-quarter results with significant growth in revenue and operating income, driven by volume increases and yield improvements across its services. The company's CEO highlighted strategic investments and team efforts amid global challenges, while the CFO expressed cautious optimism about future earnings despite ongoing uncertainties.
- text[:600]: > fdx-ex991_6.htm Exhibit 99.1 FedEx Corp. Reports Strong First Quarter Results MEMPHIS, Tenn., September 15, 2020 ... FedEx Corp. (NYSE: FDX) today reported the following consolidated results for the first quarter ended August 31 (adjusted measures exclude TNT Express integration expenses as described below): Fiscal 2021 Fiscal 2020 As Reported (GAAP) Adjusted (non-GAAP) As Reported (GAAP) Adjusted (non-GAAP) Revenue $19.3 billion $19.3 billion $17.0 billion $17.0 billion Operating income $1.59 billion $1.64 billion $0.98 billion $1.05 billion Operating margin 8.2% 8.5% 5.7% 6.1% Net income $1.

### Q3 STE 2021-08-09 → label I: KMB 2021-10-25  (Consumer Staples)
- encoders: **random**  | mean=1.75
- same_dynamic=1  same_regime=4  same_surprise=1  mental_precedent=1
- notes: _STE alza l'outlook, KMB taglia per inflazione_
- summary: Kimberly-Clark reported third-quarter 2021 results showing organic sales growth of 4% and earnings per share of $1.62, but the company's outlook was downgraded due to significant input cost inflation. Despite these challenges, Chairman and CEO Mike Hsu expressed confidence in the company’s strategy and its ability to create long-term shareholder value.
- text[:600]: > EARNINGS RELEASE Document Exhibit 99.1 KIMBERLY-CLARK ANNOUNCES THIRD QUARTER 2021 RESULTS DALLAS, October 25, 2021-Kimberly-Clark Corporation (NYSE: KMB) today reported third quarter 2021 results. Executive Summary • Third quarter 2021 net sales of $5.0 billion increased 7 percent compared to the year-ago period, with an organic sales increase of 4 percent. • Diluted net income per share for the third quarter was $1.39 in 2021 and $1.38 in 2020. • Third quarter adjusted earnings per share were $1.62 in 2021 compared to $1.72 in 2020. Adjusted earnings per share exclude certain items described

### Q5 AJG 2023-07-27 → label I: IEX 2023-02-01  (Industrials)
- encoders: **contrastive_v2**  | mean=1.75
- same_dynamic=1  same_regime=3  same_surprise=2  mental_precedent=1
- notes: _AJG espansiva, IEX frena sulla guidance_
- summary: IDEX reported its Q4 2022 and full-year 2022 earnings on February 1, 2023, highlighting cautious guidance for 2023 amid ongoing economic uncertainties and risks related to pandemics, geopolitical tensions, and market conditions.
- text[:600]: > q42022earningsslid 1 Fourth Quarter & Full Year 2022 Earnings February 1, 2023 2IDEX Proprietary & Confidential Agenda IDEX Business Overview • IDEX Overview • Segment Outlook Financials • Q4 & Full Year 2022 Performance • Full Year 2022 Adjusted EBITDA Walk 2023 Guidance Q&A 3IDEX Proprietary & Confidential Replay Information • Dial toll–free: 877.660.6853 • • Conference ID: #13734461 • Log on to: www.idexcorp.com 4IDEX Proprietary & Confidential Cautionary Statement Cautionary Statement Under the Private Securities Litigation Reform Act; Non-GAAP Measures This presentation contains “forward-

### Q8 OXY 2018-08-08 → label C: MNST 2022-05-05  (Consumer Staples)
- encoders: **random**  | mean=1.75
- same_dynamic=1  same_regime=2  same_surprise=3  mental_precedent=1
- summary: Monster Beverage reported a 22.1% increase in first-quarter net sales to $1.52 billion, driven by significant cost increases due to higher freight rates, fuel costs, and input prices. The company remains optimistic despite these challenges, as evidenced by its strategic acquisition of CANarchy Craft Brewery Collective LLC and plans for a price increase effective September 1, 2022.
- text[:600]: > PondelWilkinson Inc. 2945 Townsgate Road, Suite 200 Westlake Village, CA 91361 Investor Relations T (310) 279 5980 Strategic Public Relations W www.pondel.com CONTACTS: Rodney C. Sacks Chairman and Co-Chief Executive Officer (951)739-6200 NEWS RELEASE Hilton H. Schlosberg Vice Chairman and Co-Chief Executive Officer (951)739-6200 Roger S. Pondel / Judy Lin Sfetcu PondelWilkinson Inc. (310)279-5980 MONSTER BEVERAGE REPORTS 2022 FIRST QUARTER RESULTS -- Record First Quarter Net Sales Rise 22.1 Percent to $1.52 Billion – -- Company Completes its Acquisition of CANarchy Craft Brewery Collective LL

### Q9 CPB 2021-09-01 → label A: CRL 2019-07-31  (Health Care)
- encoders: **random**  | mean=1.75
- same_dynamic=1  same_regime=3  same_surprise=1  mental_precedent=2
- summary: Charles River Laboratories reported a 12.3% year-over-year revenue growth to $657.6 million in the second quarter of 2019, driven by acquisitions and organic growth across its business segments, with particular strength from biotechnology clients. The company remains optimistic about industry fundamentals and its strategic investments, as expressed by CEO James C. Foster, who highlighted ongoing efforts to enhance client relationships and expand service offerings.
- text[:600]: > Charles River Laboratories Announces Second-Quarter 2019 Results – Second-Quarter Revenue of $657.6 Million – – Second-Quarter GAAP Earnings per Share of $0.88 and Non-GAAP Earnings per Share of $1.63 – – Updates 2019 Guidance – WILMINGTON, Mass.--(BUSINESS WIRE)--July 31, 2019--Charles River Laboratories International, Inc. (NYSE: CRL) today reported its results for the second quarter of 2019. For the quarter, revenue was $657.6 million, an increase of 12.3% from $585.3 million in the second quarter of 2018. Acquisitions, principally the partial-quarter benefit from Citoxlab, contributed 5.7%

### Q9 CPB 2021-09-01 → label G: OXY 2019-05-06  (Energy)
- encoders: **concat_eq**  | mean=1.75
- same_dynamic=1  same_regime=3  same_surprise=1  mental_precedent=2
- summary: Occidental Petroleum reported strong first quarter 2019 results, exceeding guidance across all business segments due to higher production volumes and favorable pricing, with the CEO expressing pride in executing its returns-focused strategy. The company returned over $800 million to shareholders through dividends and share repurchases, maintaining a confident tone.
- text[:600]: > Occidental Announces 1st Quarter 2019 Results · Returned over $800 million to shareholders through dividends and share repurchases · Exceeded pre-tax income guidance for both Chemical and Midstream and Marketing · Exceeded the high end of guidance with production of 719,000 BOE per day · Permian Resources production of 261,000 BOE per day · of $631 million, or $0.84 per diluted share. Net and core income for the fourth quarter of 2018 was $706 million, or $0.93 per diluted share, and $922 million, or $1.22 per diluted share, respectively. “We’re proud to have completed another strong quarter w

### Q10 TAP 2021-04-29 → label H: SNA 2024-02-08  (Industrials)
- encoders: **random**  | mean=1.75
- same_dynamic=1  same_regime=2  same_surprise=3  mental_precedent=1
- summary: Snap-on reported strong fourth-quarter and full-year 2023 results with a 7.5% gain in diluted EPS to $4.75, driven by organic sales growth of 2.2% and improved operating margins. The company remains optimistic about its future prospects despite market turbulence, attributing its success to the resilience of its markets and the capabilities of its teams.
- text[:600]: > Snap-on Announces Fourth Quarter and Full Year 2023 Results Diluted EPS of $4.75 for the quarter represents a gain of 7.5% from Q4 2022; Sales of $1,196.6 million up 3.5% from Q4 2022, organic sales up 2.2%; Operating margin before financial services of 21.6% compares to 21.5% in Q4 2022 KENOSHA, Wis.--(BUSINESS WIRE)--February 8, 2024--Snap-on Incorporated (NYSE: SNA), a leading global innovator, manufacturer and marketer of tools, equipment, diagnostics, repair information and systems solutions for professional users performing critical tasks, today announced 2023 operating results for the f

### Q13 MMM 2019-04-25 → label E: CRL 2019-07-31  (Health Care)
- encoders: **contrastive_v2**  | mean=1.75
- same_dynamic=1  same_regime=4  same_surprise=1  mental_precedent=1
- summary: Charles River Laboratories reported a 12.3% year-over-year revenue growth to $657.6 million in the second quarter of 2019, driven by acquisitions and organic growth across its business segments, with particular strength from biotechnology clients. The company remains optimistic about industry fundamentals and its strategic investments, as expressed by CEO James C. Foster, who highlighted ongoing efforts to enhance client relationships and expand service offerings.
- text[:600]: > Charles River Laboratories Announces Second-Quarter 2019 Results – Second-Quarter Revenue of $657.6 Million – – Second-Quarter GAAP Earnings per Share of $0.88 and Non-GAAP Earnings per Share of $1.63 – – Updates 2019 Guidance – WILMINGTON, Mass.--(BUSINESS WIRE)--July 31, 2019--Charles River Laboratories International, Inc. (NYSE: CRL) today reported its results for the second quarter of 2019. For the quarter, revenue was $657.6 million, an increase of 12.3% from $585.3 million in the second quarter of 2018. Acquisitions, principally the partial-quarter benefit from Citoxlab, contributed 5.7%

### Q14 EMR 2023-08-02 → label G: EQR 2021-02-10  (Real Estate)
- encoders: **random**  | mean=1.75
- same_dynamic=1  same_regime=2  same_surprise=2  mental_precedent=2
- notes: _Notizie e macro opposte, grafici divergenti nel finale_
- summary: Equity Residential reported a decline in earnings per share and funds from operations due to lower depreciation expense and various adjustment items, but the company remains optimistic about recovery in 2021 as operating trends improve and demand for its properties is expected to accelerate with widespread vaccine administration. The CEO expressed confidence in the company's ability to recover, highlighting improvements in physical occupancy and stabilization of pricing trends despite challenging conditions in 2020.
- text[:600]: > eqr-ex991_15.htm i Fourth Quarter 2020 Results Table of Contents Earnings Release 1 - 5 Consolidated Statements of Operations 6 Consolidated Statements of Funds From Operations and Normalized Funds From Operations 7 Consolidated Balance Sheets 8 Portfolio Summary 9 Portfolio Rollforward 10 Same Store Results 11 - 17 Debt Summary 18 - 20 Capital Structure 21 Common Share and Unit Weighted Average Amounts Outstanding 22 Development and Lease-Up Projects 23 Capital Expenditures to Real Estate 24 Normalized EBITDAre Reconciliations 25 Adjustments from FFO to Normalized FFO 26 Normalized FFO Guidan

### Q15 URI 2020-04-29 → label E: FSLR 2024-10-29  (Information Technology)
- encoders: **random**  | mean=1.75
- same_dynamic=1  same_regime=2  same_surprise=3  mental_precedent=1
- summary: First Solar reported third-quarter 2024 financial results with net sales of $0.9 billion, impacted by a product warranty reserve charge of $50 million, reflecting industry volatility and political uncertainty; the company remains optimistic about its long-term approach despite these challenges. CEO Mark Widmar expressed confidence in navigating upcoming US elections and continued solar manufacturing industry volatility through disciplined management.
- text[:600]: > Document EXHIBIT 99.1 News Release First Solar, Inc. Announces Third Quarter 2024 Financial Results • Net sales of $0.9 billion • Net income per diluted share of $2.91, impacted by $50 million product warranty reserve charge • Net cash balance of $0.7 billion • YTD net bookings of 4.0 GW; 0.4 GW since second quarter earnings call • Expected sales backlog of 73.3 GW TEMPE, Ariz., October 29, 2024 – First Solar, Inc. (Nasdaq: FSLR) (the “Company”) today announced financial results for the third quarter ended September 30, 2024. Net sales for the third quarter were $0.9 billion, a decrease of $0.

### Q1 COHR 2020-08-13 → label G: PPL 2019-11-05  (Utilities)
- encoders: **random**  | mean=2.00
- same_dynamic=1  same_regime=1  same_surprise=4  mental_precedent=2
- summary: PPL Corporation reported strong third-quarter 2019 earnings, increasing its forecast range for full-year earnings from ongoing operations to $2.35 to $2.45 per share from $2.30 to $2.50 per share, driven by solid financial results and operational performance across its regulated utilities. The company remains optimistic about future growth, reaffirming expectations of 5% to 6% compound annual earnings growth through 2020.
- text[:600]: > Exhibit Exhibit 99.1 news release www.pplnewsroom.com Contacts: For news media – Ryan Hill, 610-774-5997 For financial analysts – Andy Ludwig, 610-774-3389 PPL Corporation Reports Third -Quarter 2019 Earnings • Announces strong third -quarter reported earnings of $ 0.65 per share and earnings from ongoing operations of $ 0.61 per share. • Narrows 2019 earnings from ongoing operations forecast range to $2.35 to $2.45 per share from $2.30 to $2.50 per share. ALLENTOWN, Pa. (Nov. 5, 2019 ) - PPL Corporation (NYSE: PPL) on Tuesday (11/5) announced third -quarter 2019 reported earnings (GAAP) of $ 

### Q4 ALGN 2019-04-24 → label B: ES 2023-11-06  (Utilities)
- encoders: **random**  | mean=2.00
- same_dynamic=1  same_regime=2  same_surprise=3  mental_precedent=2
- notes: _Settori distanti e tassi macroeconomici non comparabili_
- summary: Eversource Energy and its subsidiaries reported their financial performance for the third quarter of 2023 in a press release, highlighting operational results; the driver mentioned was strong utility operations and stable customer demand. The tone is cautiously optimistic, with management set to discuss these results during an upcoming conference call.
- text[:600]: > false 0000072741 8-K 2023-11-06 false 0000023426 ̈ ̈ ̈ ̈ 8-K 2023-11-06 false 0000013372 ̈ ̈ ̈ ̈ 0000315256 ̈ 8-K 2023-11-06 false ̈ ̈ ̈ 0000072741 2023-11-06 2023-11-06 0000072741 es:TheConnecticutLightAndPowerCompanyMember 2023-11-06 2023-11-06 0000072741 es:NstarElectricCompanyMember 2023-11-06 2023-11-06 0000072741 es:PublicServiceCompanyOfNewHampshireMember 2023-11-06 2023-11-06 iso4217:USD xbrli:shares iso4217:USD xbrli:shares UNITED STATES SECURITIES AND EXCHANGE COMMISSION Washington, D.C. 20549 FORM 8-K CURRENT REPORT Pursuant to Section 13 or 15(d) of the Securities Exchange Act of 1

### Q4 ALGN 2019-04-24 → label E: ICE 2021-02-04  (Financials)
- encoders: **contrastive_v2**  | mean=2.00
- same_dynamic=1  same_regime=2  same_surprise=4  mental_precedent=1
- notes: _Entrambe trimestrali record, ma macro e settori distanti_
- summary: Intercontinental Exchange reported record revenues for the 15th consecutive year in 2020, with net revenues reaching $6.0 billion, driven by strong performance across its exchanges, fixed income and data services, and mortgage technology segments. The company expressed confidence in its future growth prospects, emphasizing the contributions of its employees and strategic investments.
- text[:600]: > Intercontinental Exchange Reports Fourth Quarter & Full Year 2020 15th consecutive year of record revenues • 2020 net revenues of $6.0 billion, +16% y/y Jeffrey C. Sprecher , ICE Chairman & Chief Executive Officer , said , “We are pleased to report our 15 th consecutive year of record revenues and another year of double-digit earnings per share growth. In this unprecedented year, we are grateful for our customers and their trust. As we begin 2021, we are focused on applying our expertise, technology and data services to solving problems for our customers and creating value for our shareholders

### Q6 EQR 2024-01-30 → label E: PSX 2019-04-30  (Energy)
- encoders: **contrastive_v2**  | mean=2.00
- same_dynamic=1  same_regime=2  same_surprise=3  mental_precedent=2
- summary: Phillips 66 reported first-quarter earnings of $204 million, reflecting a diversified portfolio's resilience despite a weak market environment, with key achievements including high Chemicals segment utilization and significant shareholder returns. Chairman Greg Garland expressed confidence in the company’s growth projects and dedication to operating excellence, while acknowledging challenges such as unplanned refinery downtime that impacted performance.
- text[:600]: > Exhibit Phillips 66 Reports First-Quarter Earnings of $204 Million (Adjusted Earnings of $187 Million) Exhibit 99.1 Phillips 66 Reports First -Quarter Earnings of $204 Million or $0.44 Per Share Adjusted earnings of $187 million or $0.40 per share Highlights • Returned $708 million to shareholders through dividends and share repurchases • Achieved 98% O&P capacity utilization in Chemicals • Delivered record utilization at Sweeny fractionator and Freeport LPG export facility • Advanced several large-scale Midstream growth projects • Executed major turnaround program impacting five refineries • 

### Q7 NUE 2023-04-20 → label A: PCG 2023-07-27  (Utilities)
- encoders: **random**  | mean=2.00
- same_dynamic=1  same_regime=3  same_surprise=3  mental_precedent=1
- summary: PG&E Corporation released a press release detailing financial results and business outlook for its utility operations, citing regulatory challenges and safety concerns as key drivers; the tone is cautiously optimistic, emphasizing management's commitment to improving performance while navigating these issues.
- text[:600]: > The press release is attached as Exhibit 99.1 to this report. PG&E Corporation also will hold a webcast conference call to discuss financial results and management’s business outlook. The press release contains information about how to access the webcast. The slide presentation, which includes supplemental information relating to PG&E Corporation and the Utility, will be used by management during the webcast and is attached as Exhibit 99.2 to this report. The Exhibits will be posted on PG&E Corporation’s website at http://investor.pgecorp.com. The information included in Items 2.02, 7.01, and 

### Q7 NUE 2023-04-20 → label C: JKHY 2022-11-08  (Financials)
- encoders: **random**  | mean=2.00
- same_dynamic=1  same_regime=2  same_surprise=4  mental_precedent=1
- summary: Jack Henry & Associates, Inc., reported a 8% increase in both GAAP and non-GAAP revenue for Q1 FY'2023, driven by strong demand for its technology solutions and new initiatives. The company remains optimistic about its future prospects, as evidenced by the guidance for continued growth in fiscal year 2023.
- text[:600]: > - Q1 FY'2023 PRESS RELEASE Document Press Release Mimi L. Carsley | Chief Financial Officer | mcarsley@jackhenry.com FOR IMMEDIATE RELEASE Jack Henry & Associates, Inc. Reports First Quarter Fiscal 2023 Results First quarter summary: • GAAP revenue increased 8% and GAAP operating income increased 5% for the three months ended September 30, 2022, compared to the prior fiscal year quarter. • Non-GAAP adjusted revenue increased 8% and non-GAAP adjusted operating income increased 2% for the three months ended September 30, 2022, compared to the prior fiscal year quarter. 1 ▪ GAAP EPS was $1.46 per

### Q9 CPB 2021-09-01 → label C: WMB 2019-07-31  (Energy)
- encoders: **contrastive_v2**  | mean=2.00
- same_dynamic=2  same_regime=2  same_surprise=3  mental_precedent=1
- summary: The Williams Companies, Inc. reported its financial results for the quarter ended June 30, 2019, highlighting key operational metrics; the announcement was made on July 31, 2019, with a focus on providing detailed financial insights and performance indicators.
- text[:600]: > Item 2.02. Results of Operations and Financial Condition On July 31, 2019 , The Williams Companies, Inc. (the "Company") issued a press release announcing its financial results for the quarter ended June 30, 2019 . A copy of the press release and accompanying financial highlights and operating statistics and reconciliation schedules are furnished herewith as Exhibit 99.1 and are incorporated herein in their entirety by reference. The press release and accompanying financial highlights and operating statistics and reconciliation schedules are being furnished pursuant to

### Q10 TAP 2021-04-29 → label F: COP 2021-08-03  (Energy)
- encoders: **contrastive_v2, concat_eq**  | mean=2.00
- same_dynamic=1  same_regime=3  same_surprise=3  mental_precedent=1
- summary: ConocoPhillips delivered strong second-quarter 2021 financial results with earnings of $2.1 billion, driven by higher realized prices and volumes following the company's recent 10-year market update that reaffirmed its commitment to the energy transition while maintaining sector-leading returns on capital. The CEO expressed confidence in the company’s multi-year plan and resilience, emphasizing its unique position to deliver through industry price cycles.
- text[:600]: > ConocoPhillips Delivers Strong Second-Quarter 2021 Financial and Operational Results Following Recent 10-Year Market Update Reported earnings of $2.1 billion; adjusted earnings of $1.7 billion. Generated cash provided by operating activities of $4.3 billion; cash from operations of $4.0 billion. Produced 1,547 MBOED excluding Libya. HOUSTON--(BUSINESS WIRE)--August 3, 2021--ConocoPhillips (NYSE: COP) today reported second-quarter 2021 earnings of $2.1 billion, or $1.55 per share, compared with second-quarter 2020 earnings of $0.3 billion, or $0.24 per share. Excluding special items, second-qua

### Q10 TAP 2021-04-29 → label G: HWM 2018-07-31  (Industrials)
- encoders: **contrastive_v2**  | mean=2.00
- same_dynamic=1  same_regime=2  same_surprise=3  mental_precedent=2
- summary: Arconic reported second-quarter 2018 results showing strong organic revenue growth and doubled adjusted free cash flow, driven by higher volumes in key markets. CEO Chip Blankenship expressed confidence in the company's progress despite challenges like unfavorable production mix and customer claims settlements, maintaining a cautiously optimistic tone.
- text[:600]: > Arconic Reports Second Quarter 2018 Results Second Quarter 2018 Highlights Revenue of $3.6 billion, up 10% year over year; organic revenue 1 up 5% year over year Net income of $120 million, or $0.24 per share, versus net income of $212 million, or $0.43 per share, in the second quarter of 2017 Net income excluding special items of $185 million, or $0.37 per share, versus $165 million, or $0.32 per share, in the second quarter of 2017 Operating income of $324 million, up 1% year over year Operating income excluding special items of $381 million, down 2% year over year In the second quarters of 

### Q11 URI 2021-04-28 → label A: AEE 2018-05-09  (Utilities)
- encoders: **contrastive_v2**  | mean=2.00
- same_dynamic=1  same_regime=2  same_surprise=4  mental_precedent=1
- summary: Ameren Corporation reported a 47.6% increase in first quarter earnings per share to $0.62 in 2018 from $0.42 in 2017, driven by higher electric service rates and retail sales due to colder winter temperatures; the company remains confident in its 2018 earnings guidance of $2.95 to $3.15 per share despite potential risks.
- text[:600]: > Exhibit Exhibit 99.1 NEWS RELEASE 1901 Chouteau Avenue: St. Louis, MO 63103: Ameren.com Contacts Media Analysts Investors Joe Muehlenkamp Doug Fischer Andrew Kirk Investor Services 314.554.2182 314.554.4859 314.554.3942 800.255.2237 jmuehlenkamp@ameren.com dfischer@ameren.com akirk@ameren.com invest@ameren.com For Immediate Release Ameren Announces First Quarter 2018 Results • First Quarter Earnings Per Share were $0.62 in 2018 vs. $0.42 in 2017 • Guidance Range for 2018 Affirmed at $2.95 to $3.15 Per Diluted Share ST. LOUIS (May 9, 2018) — Ameren Corporation (NYSE: AEE) today announced first 

### Q11 URI 2021-04-28 → label H: ETN 2020-07-29  (Industrials)
- encoders: **contrastive_v2**  | mean=2.00
- same_dynamic=2  same_regime=2  same_surprise=2  mental_precedent=2
- summary: Eaton reported second-quarter earnings per share of $0.13, with adjusted earnings per share at $0.70 after excluding charges related to acquisitions and restructuring. Despite a challenging environment due to the pandemic, which led to significant sales declines across multiple segments, CEO Craig Arnold expressed confidence in the company's ability to navigate through the downturn and implement restructuring programs aimed at improving long-term profitability.
- text[:600]: > Eaton Reports Second Quarter Earnings Per Share of $0.13 Adjusted Earnings Per Share of $0.70 for the Second Quarter Excluding Charges of $0.20 Per Share Related to Acquisitions and Divestitures and $0.37 Per Share Related to Multi-Year Restructuring Program 2020 Full Year Free Cash Flow Guidance Reaffirmed at $2.3 Billion to $2.7 Billion DUBLIN--(BUSINESS WIRE)--July 29, 2020--Power management company Eaton Corporation plc (NYSE:ETN) today announced that earnings per share were $0.13 for the second quarter of 2020. Excluding charges of $0.20 per share related to acquisitions and divestitures 

### Q12 NDSN 2020-05-20 → label A: EPAM 2024-08-08  (Information Technology)
- encoders: **random**  | mean=2.00
- same_dynamic=2  same_regime=2  same_surprise=3  mental_precedent=1
- summary: EPAM Systems reported a 2.0% decrease in second-quarter revenues to $1.147 billion, attributing the decline to ongoing macroeconomic challenges, while updating its full-year outlook with narrowed revenue and earnings guidance due to stable client demand. The company remains optimistic about adapting operations and enhancing service offerings despite current market conditions, as evidenced by a new share repurchase program authorized for up to $500 million.
- text[:600]: > Document Exhibit 99.1 EPAM Reports Results for Second Quarter 2024 and Updates Full Year Outlook • Second quarter revenues of $1.147 billion, down 2.0% year-over-year • GAAP income from operations was 10.5% of revenues and non-GAAP income from operations was 15.2% of revenues for the second quarter • Second quarter GAAP diluted EPS of $1.70, a decrease of $0.33, and non-GAAP diluted EPS of $2.45, a decrease of $0.19 on a year-over-year basis • For the full year, EPAM narrows expected range for revenues to $4.590 billion to $4.625 billion, updates expected GAAP diluted EPS to now be in the rang

### Q12 NDSN 2020-05-20 → label B: EIX 2025-02-27  (Utilities)
- encoders: **contrastive_v2**  | mean=2.00
- same_dynamic=1  same_regime=2  same_surprise=3  mental_precedent=2
- summary: Edison International reported fourth-quarter earnings per share (EPS) of $0.88, down from $0.99 in the same period last year, primarily due to higher operation and maintenance expenses and interest expense, but benefited by an approved TKM settlement authorizing $1.6 billion of cost recovery for pre-AB 1054 wildfires. The company remains optimistic, guiding core EPS growth between $5.94 and $6.34 in 2025, reflecting confidence in its wildfire mitigation efforts and regulatory support.
- text[:600]: > EDISON Document Exhibit 99.1 NEWS Investor Relations: Sam Ramraj, (626) 302- 2540 Media Relations : (626) 302- 2255 News@sce.com Edison GAAP EPS of $ 0.88; Core EPS of $1.05 • Full-year 2024 GAAP EPS of $3.33; Core EPS of $4.93 • TKM settlement approved, authorizing $1.6 billion of cost recovery for pre-AB 1054 wildfire • Revised 2025 Core EPS guidance of $5.94-$6.34 includes impact of TKM settlement • Continued confidence in delivering 5-7% Core EPS growth from $5.84 (2025) to $6.74-$7.14 (2028) ROSEMEAD, Calif., Feb. 27, 2025 — Edison International (NYSE: EIX) today reported fourth-quarter n

### Q13 MMM 2019-04-25 → label I: CVX 2020-01-31  (Energy)
- encoders: **concat_eq**  | mean=2.00
- same_dynamic=2  same_regime=3  same_surprise=2  mental_precedent=1
- summary: Chevron reported a fourth-quarter loss of $6.6 billion, primarily due to upstream impairments and write-offs totaling $10.4 billion related to various projects, but still managed to deliver on core financial priorities with strong cash flow from operations and record annual oil-equivalent production. The company remains optimistic about its commitment to capital discipline and superior shareholder returns despite the quarter's challenges.
- text[:600]: > Exhibit news release FOR RELEASE AT 5:30 AM PDT JANUARY 31, 2020 Chevron Announces Fourth Quarter 2019 Results Delivers on core financial priorities, demonstrates commitment to capital discipline and superior shareholder returns • Fourth quarter loss $6.6 billion ; earnings excluding special items and FX $2.8 billion • Annual earnings $2.9 billion ; earnings excluding special items and FX $11.9 billion • Cash flow from operations of $27.3 billion in 2019 • Record annual net oil-equivalent production of 3.06 million barrels per day • Dividends and share repurchases of $13.0 billion in 2019 San 

## Top Performers (mean of 4 metrics ≥ 4.0)  —  20 candidates

### Q6 EQR 2024-01-30 → label H: SNA 2024-02-08  (Industrials)
- encoders: **concat_eq**  | mean=5.00
- same_dynamic=5  same_regime=5  same_surprise=5  mental_precedent=5
- notes: _Stesso settore e settimana, grafici speculari in rialzo_
- summary: Snap-on reported strong fourth-quarter and full-year 2023 results with a 7.5% gain in diluted EPS to $4.75, driven by organic sales growth of 2.2% and improved operating margins. The company remains optimistic about its future prospects despite market turbulence, attributing its success to the resilience of its markets and the capabilities of its teams.

### Q2 HPE 2020-05-21 → label C: REG 2020-05-08  (Real Estate)
- encoders: **concat_eq**  | mean=4.50
- same_dynamic=4  same_regime=5  same_surprise=5  mental_precedent=4
- notes: _stesso mese, impatto covid negativo su entrambe_
- summary: Regency Centers reported first quarter 2020 results showing a net loss per diluted share of ($0.15) due to a non-cash goodwill impairment charge, while NAREIT FFO remained strong at $0.98 per diluted share. Despite the impact of the COVID-19 pandemic, which led to a decline in same property Net Operating Income by 0.7%, Regency expressed confidence in its well-positioned portfolio and healthy balance sheet, emphasizing its dedication to tenant support during these challenging times.

### Q2 HPE 2020-05-21 → label D: CAT 2020-04-28  (Industrials)
- encoders: **contrastive_v2**  | mean=4.50
- same_dynamic=4  same_regime=5  same_surprise=5  mental_precedent=4
- notes: _Stesso shock Covid, crollo ricavi a doppia cifra_
- summary: Caterpillar Inc. reported a 21% decrease in first-quarter 2020 sales and revenues due to lower end-user demand and changes in dealer inventories, resulting in a 39% decline in profit per share. Despite the challenges posed by the COVID-19 pandemic, the company remains optimistic about emerging stronger and is taking actions to enhance its financial position while continuing its strategy for profitable growth.

### Q3 STE 2021-08-09 → label D: EPAM 2021-08-05  (Information Technology)
- encoders: **concat_eq**  | mean=4.50
- same_dynamic=3  same_regime=5  same_surprise=5  mental_precedent=5
- notes: _Stessa settimana, stesso macroclima e grafici speculari_
- summary: EPAM Systems reported strong second-quarter results with a 39.4% year-over-year revenue increase to $881.4 million and raised its full-year outlook due to robust demand and successful execution, highlighting the company's adaptability in a changing market; the CEO expressed confidence in continuing growth through expanded capabilities and talent expansion.

### Q3 STE 2021-08-09 → label H: ECL 2021-07-27  (Materials)
- encoders: **concat_eq**  | mean=4.50
- same_dynamic=4  same_regime=5  same_surprise=5  mental_precedent=4
- notes: _Settori affini, stesso mese e macroclima identico_
- summary: Ecolab reported strong second-quarter earnings with double-digit sales and earnings growth, driven by recovering markets, new business wins, and robust product launches, particularly in the Institutional & Specialty segments. The CEO expressed confidence in continued performance, expecting a strong finish to 2021 despite near-term challenges from rising inflation and variant infections.

### Q4 ALGN 2019-04-24 → label I: RMD 2019-05-02  (Health Care)
- encoders: **contrastive_v2**  | mean=4.50
- same_dynamic=4  same_regime=5  same_surprise=5  mental_precedent=4
- notes: _Stesso settore e settimana, ottime trimestrali, direzione grafica diversa_
- summary: ResMed Inc. reported a strong third quarter with year-over-year revenue growth of 12%, driven by contributions from MatrixCare and international device sales, leading to operating profit up 15%. The company remains optimistic about its future prospects, highlighting the expansion of its mask portfolio and a robust product pipeline.

### Q9 CPB 2021-09-01 → label I: KMB 2021-10-25  (Consumer Staples)
- encoders: **concat_eq**  | mean=4.50
- same_dynamic=5  same_regime=5  same_surprise=5  mental_precedent=3
- notes: _Stesso settore e allarme inflazione, grafici divergenti_
- summary: Kimberly-Clark reported third-quarter 2021 results showing organic sales growth of 4% and earnings per share of $1.62, but the company's outlook was downgraded due to significant input cost inflation. Despite these challenges, Chairman and CEO Mike Hsu expressed confidence in the company’s strategy and its ability to create long-term shareholder value.

### Q12 NDSN 2020-05-20 → label H: LIN 2020-05-07  (Materials)
- encoders: **concat_eq**  | mean=4.50
- same_dynamic=4  same_regime=5  same_surprise=4  mental_precedent=5
- notes: _Stessa macro nel 2020, grafici altamente sintonizzati_
- summary: Linde reported strong first-quarter 2020 financial results, including a 26% increase in operating cash flow and robust balance sheet liquidity, driven by improved pricing and operational efficiency despite a 1% decrease in sales due to the COVID-19 pandemic. CEO Steve Angel expressed confidence in the company's ability to create shareholder value through its resilient business model and opportunities to mitigate economic challenges.

### Q14 EMR 2023-08-02 → label D: MLM 2023-07-27  (Materials)
- encoders: **concat_eq**  | mean=4.50
- same_dynamic=4  same_regime=5  same_surprise=5  mental_precedent=4
- notes: _Stesso clima e notizia beat+raise, grafici speculari_
- summary: Martin Marietta reported record-breaking second-quarter 2023 results with significant increases in revenues and profitability, driven by strong pricing gains and a successful commercial strategy despite lower aggregates shipments. The company expressed confidence in its ability to deliver superior shareholder value, raising full-year Adjusted EBITDA guidance and expecting an even stronger performance in the second half of 2023.

### Q15 URI 2020-04-29 → label B: FCX 2020-04-24  (Materials)
- encoders: **contrastive_v2**  | mean=4.50
- same_dynamic=4  same_regime=5  same_surprise=5  mental_precedent=4
- notes: _Stessa macro e tagli Covid, ottima sintonizzazione_
- summary: Freeport-McMoRan announced revised operating plans aimed at reducing costs and capital expenditures by $1.3 billion, $800 million, and $100 million respectively in response to the COVID-19 pandemic's negative economic impact, while maintaining strong liquidity. President Richard C. Adkerson expressed confidence that these measures will protect long-term asset values and position the company for improved performance as economic conditions recover.

### Q15 URI 2020-04-29 → label F: LIN 2020-05-07  (Materials)
- encoders: **concat_eq**  | mean=4.50
- same_dynamic=4  same_regime=5  same_surprise=4  mental_precedent=5
- notes: _Stessa macro nel 2020, grafici altamente sintonizzati_
- summary: Linde reported strong first-quarter 2020 financial results, including a 26% increase in operating cash flow and robust balance sheet liquidity, driven by improved pricing and operational efficiency despite a 1% decrease in sales due to the COVID-19 pandemic. CEO Steve Angel expressed confidence in the company's ability to create shareholder value through its resilient business model and opportunities to mitigate economic challenges.

### Q2 HPE 2020-05-21 → label B: FCX 2020-04-24  (Materials)
- encoders: **concat_eq**  | mean=4.25
- same_dynamic=4  same_regime=5  same_surprise=5  mental_precedent=3
- summary: Freeport-McMoRan announced revised operating plans aimed at reducing costs and capital expenditures by $1.3 billion, $800 million, and $100 million respectively in response to the COVID-19 pandemic's negative economic impact, while maintaining strong liquidity. President Richard C. Adkerson expressed confidence that these measures will protect long-term asset values and position the company for improved performance as economic conditions recover.

### Q2 HPE 2020-05-21 → label H: CPAY 2020-11-05  (Financials)
- encoders: **contrastive_v2**  | mean=4.25
- same_dynamic=4  same_regime=5  same_surprise=5  mental_precedent=3
- notes: _Stesso impatto Covid sui ricavi, ma CPAY lancia buyback_
- summary: FLEETCOR Technologies reported a 14% decrease in third-quarter 2020 revenues due to the global business environment's challenges but noted sequential improvements across its lines of business driven by increased client usage and improved new sales performance. The company remains cautious about full-year outlooks, citing uncertain recovery sustainability, while expressing optimism through plans for an expanded share repurchase program worth $1 billion.

### Q4 ALGN 2019-04-24 → label G: ULTA 2018-05-31  (Consumer Discretionary)
- encoders: **concat_eq**  | mean=4.25
- same_dynamic=3  same_regime=4  same_surprise=5  mental_precedent=5
- notes: _Titoli growth speculari, stessa dinamica sell-the-news_
- summary: Ulta Beauty reported strong first-quarter fiscal 2018 results with net sales up 17.4% and diluted EPS increasing by 31.7%, driven by better-than-expected sales growth and the adoption of new revenue recognition standards that boosted net sales. The company remains optimistic, raising its guidance for diluted EPS for the full year, citing a solid start to 2018 with healthy retail comparable store sales and strong e-commerce performance.

### Q11 URI 2021-04-28 → label F: DE 2021-02-19  (Industrials)
- encoders: **concat_eq**  | mean=4.25
- same_dynamic=4  same_regime=4  same_surprise=5  mental_precedent=4
- notes: _Stesso settore e notizia beat+raise coerente_
- summary: Deere & Company reported a first-quarter net income of $1.224 billion, more than doubling from the previous year due to a 23% gain in net sales and successful execution of their new operating strategy. The company remains optimistic, forecasting full-year earnings in the range of $4.6 to $5.0 billion and citing improved conditions in agricultural and construction sectors as key drivers for future strong performance.

### Q13 MMM 2019-04-25 → label A: DOW 2019-07-25  (Materials)
- encoders: **concat_eq**  | mean=4.25
- same_dynamic=4  same_regime=4  same_surprise=4  mental_precedent=5
- notes: _Stesso ciclo manifatturiero 2019, grafici altamente sintonizzat
_
- summary: Dow reported second quarter 2019 results with GAAP EPS from continuing operations of $0.10 and operating EBIT of $1.1 billion, down significantly due to local price declines and lower sales in key segments like polyethylene, siloxanes, and isocyanates; however, the company highlighted cost synergy savings and disciplined operational management as positive factors. The tone is cautiously optimistic, acknowledging challenges while emphasizing progress and efficiency improvements.

### Q2 HPE 2020-05-21 → label E: VICI 2020-04-30  (Real Estate)
- encoders: **concat_eq**  | mean=4.00
- same_dynamic=4  same_regime=5  same_surprise=4  mental_precedent=3
- notes: _Stesso shock pandemico, ma dinamiche settoriali differenti_
- summary: VICI Properties Inc. reported its financial results for the quarter ended March 31, 2020, showing mixed performance; the company cited ongoing operational challenges due to the pandemic as the primary driver of its results. The tone is cautiously optimistic, with a focus on navigating through current difficulties.

### Q3 STE 2021-08-09 → label A: CPRT 2021-09-08  (Industrials)
- encoders: **contrastive_v2**  | mean=4.00
- same_dynamic=2  same_regime=5  same_surprise=5  mental_precedent=4
- notes: _Stesso mese e tassi, ottime trimestrali in crescita_
- summary: Copart, Inc. reported strong financial results for its fourth quarter and fiscal year ended July 31, 2021, with significant increases in revenue, gross profit, and net income driven by higher demand from the automotive salvage market; the company's tone is confident as it highlights robust growth and positive performance metrics.

### Q3 STE 2021-08-09 → label C: TSCO 2021-10-21  (Consumer Discretionary)
- encoders: **concat_eq**  | mean=4.00
- same_dynamic=2  same_regime=5  same_surprise=5  mental_precedent=4
- notes: _Stesso ciclo 2021 ed entrambi beat+raise_
- summary: Tractor Supply Company reported record third-quarter financial results with a 15.8% increase in net sales and a 20.4% rise in diluted earnings per share to $1.95, driven by robust demand for everyday merchandise and continued growth in summer seasonal categories. The company's President and CEO expressed optimism about the business's resilience amid supply chain challenges, stating that despite these pressures, they are raising their fiscal 2021 guidance and expecting a record year of sales and earnings.

### Q12 NDSN 2020-05-20 → label C: AAPL 2020-04-30  (Information Technology)
- encoders: **concat_eq**  | mean=4.00
- same_dynamic=3  same_regime=5  same_surprise=4  mental_precedent=4
- notes: _Stessa macro nel 2020, solidi rally post-evento
_
- summary: Apple reported a second-quarter revenue growth of 1 percent to $58.3 billion, driven by an all-time record in Services revenue reaching $13.3 billion, while maintaining a resilient business performance despite the global impact of COVID-19; the company's CFO expressed confidence in its future and continued significant investments, indicating an optimistic outlook.

## Encoder share among Hard Failures / Top Performers

| encoder | hard count | top count |
|---|---|---|
| contrastive_v2 | 16 | 5 |
| concat_eq | 4 | 15 |
| random | 26 | 0 |
