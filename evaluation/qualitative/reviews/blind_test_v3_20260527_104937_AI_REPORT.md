# Blind Test V2 — Analysis Report

- responses : blind_test_v3_20260527_104937_AI_responses.json
- key       : blind_test_v3_20260527_104937_KEY.md
- data      : blind_test_v3_20260527_104937_data.json
- queries with answers: 15; total rated rows: 127; cannot_evaluate: 0

## Per encoder × metric

| encoder | same_dynamic | same_regime | same_surprise | mental_precedent |
|---|---|---|---|---|
| **concat_eq_plus** | 1.91 (med 2.0, n=45) | 3.11 (med 3.0, n=45) | 2.84 (med 3.0, n=45) | 1.87 (med 2.0, n=45) |
| **concat_eq** | 1.93 (med 2.0, n=45) | 3.22 (med 3.0, n=45) | 2.98 (med 3.0, n=45) | 1.87 (med 2.0, n=45) |
| **contrastive_v2** | n/a | n/a | n/a | n/a |
| **random** | 1.38 (med 1.0, n=45) | 1.84 (med 2.0, n=45) | 2.47 (med 3.0, n=45) | 1.36 (med 1.0, n=45) |

### High (≥4) / Low (≤2) per encoder × metric

| encoder | metric | hi | lo | n |
|---|---|---|---|---|
| concat_eq_plus | same_dynamic | 2 | 36 | 45 |
| concat_eq_plus | same_regime | 12 | 9 | 45 |
| concat_eq_plus | same_surprise | 8 | 10 | 45 |
| concat_eq_plus | mental_precedent | 1 | 37 | 45 |
| concat_eq | same_dynamic | 0 | 36 | 45 |
| concat_eq | same_regime | 16 | 10 | 45 |
| concat_eq | same_surprise | 10 | 10 | 45 |
| concat_eq | mental_precedent | 0 | 38 | 45 |
| contrastive_v2 | same_dynamic | 0 | 0 | 0 |
| contrastive_v2 | same_regime | 0 | 0 | 0 |
| contrastive_v2 | same_surprise | 0 | 0 | 0 |
| contrastive_v2 | mental_precedent | 0 | 0 | 0 |
| random | same_dynamic | 0 | 43 | 45 |
| random | same_regime | 2 | 37 | 45 |
| random | same_surprise | 4 | 21 | 45 |
| random | mental_precedent | 0 | 44 | 45 |

## Statistical tests

### Kruskal-Wallis (3-way) per metric

| metric | H | p | significant |
|---|---|---|---|
| same_dynamic | 17.428 | 0.0002 | **p<0.05** |
| same_regime | 49.630 | 0.0000 | **p<0.05** |
| same_surprise | 8.995 | 0.0111 | **p<0.05** |
| mental_precedent | 16.989 | 0.0002 | **p<0.05** |

### Pairwise Mann-Whitney U (two-sided)

| metric | pair | U | p | sig |
|---|---|---|---|---|
| same_dynamic | concat_eq_plus vs concat_eq | 967.5 | 0.6956 |  |
| same_dynamic | concat_eq_plus vs random | 1389.5 | 0.0008 | ** |
| same_dynamic | concat_eq vs random | 1452.0 | 0.0001 | ** |
| same_regime | concat_eq_plus vs concat_eq | 949.0 | 0.5850 |  |
| same_regime | concat_eq_plus vs random | 1733.0 | 0.0000 | ** |
| same_regime | concat_eq vs random | 1738.0 | 0.0000 | ** |
| same_surprise | concat_eq_plus vs concat_eq | 957.5 | 0.6219 |  |
| same_surprise | concat_eq_plus vs random | 1268.5 | 0.0248 | ** |
| same_surprise | concat_eq vs random | 1334.5 | 0.0050 | ** |
| mental_precedent | concat_eq_plus vs concat_eq | 994.0 | 0.8729 |  |
| mental_precedent | concat_eq_plus vs random | 1395.5 | 0.0006 | ** |
| mental_precedent | concat_eq vs random | 1431.5 | 0.0002 | ** |

## Hard Failures (mean of 4 metrics ≤ 2.0)  —  60 candidates

### Q2 HPE 2020-05-21 → label A: GWW 2019-01-24  (Industrials)
- encoders: **random**  | mean=1.00
- same_dynamic=1  same_regime=1  same_surprise=1  mental_precedent=1
- notes: _Strong beat vs COVID miss; opposite macro regime_
- summary: Grainger reported strong financial results for the 2018 fourth quarter and full year, with sales and margins exceeding expectations, driven by U.S. segment volume growth and cost reductions across the organization. Chairman DG Macpherson expressed confidence in maintaining high operating margins and driving continued growth in 2019.
- text[:600]: > Exhibit GRAINGER REPORTS RESULTS FOR THE 2018 FOURTH QUARTER AND FULL YEAR Full year sales increase 8 percent; reported operating margin of 10 percent; adjusted operating margin of 12 percent; company provides 2019 guidance 2018 Financial Highlights • Sales of $11.2 billion, up 8 percent • Reported operating earnings of $1.2 billion, up 12 percent; adjusted operating earnings of $1.3 billion, up 17 percent • Reported operating margin of 10.3 percent, up 40 basis points; adjusted operating margin of 12.0 percent, up 100 basis points • Reported EPS of $13.73, up 37 percent; adjusted EPS of $16.7

### Q15 URI 2020-04-29 → label A: PWR 2024-05-02  (Industrials)
- encoders: **random**  | mean=1.00
- same_dynamic=1  same_regime=1  same_surprise=1  mental_precedent=1
- notes: _Crisis withdrawal vs confident raise, opposite macro_
- summary: Quanta Services, Inc. reported strong first quarter 2024 results, including double-digit growth in revenue, adjusted EBITDA, and earnings per share, driven by increased demand for energy transition initiatives and solid performance across its segments. The company remains confident in its full-year 2024 expectations despite potential uncertainties from weather, regulatory, and economic factors.
- text[:600]: > FOR IMMEDIATE RELEASE 24-06 Contacts: Jayshree Desai, CFO Media – Liz James Kip Rupp, CFA, IRC - Investors FGS Global Quanta Services, Inc. (281) 881-5170 (713) 629-7600 QUANTA SERVICES REPORTS FIRST QUARTER 2024 RESULTS First Quarter Consolidated Revenues of $5.03 Billion* First Quarter GAAP Diluted EPS of $0.79 and Adjusted Diluted EPS of $1.41* Net Income Attributable to Common Stock of $118.4 Million and Adjusted EBITDA of $387.3 Million* Cash Flow From Operations of $238.0 Million* and Free Cash Flow of $181.2 Million* Remaining Performance Obligations of $14.9 Billion* and Total Backlog 

### Q2 HPE 2020-05-21 → label F: HBAN 2022-07-21  (Financials)
- encoders: **random**  | mean=1.25
- same_dynamic=1  same_regime=2  same_surprise=1  mental_precedent=1
- notes: _IT miss vs financials record beat, opposite_
- summary: Huntington Bancshares Incorporated reported record second-quarter earnings, achieving $539 million in net income or $0.35 per common share, up from the prior quarter due to robust loan growth, increased deposit balances, and higher interest rates. CEO Steve Steinour expressed satisfaction with the performance, highlighting cost synergies from recent acquisitions and strong credit metrics, while emphasizing the franchise's growth potential and commitment to customer satisfaction.
- text[:600]: > Document Exhibit 99.1 July 21, 2022 Analysts: Tim Sedabres (timothy.sedabres@huntington.com), 952.745.2766 Media: Allison Gabrys (corpmedia@huntington.com), 248.961.3978 HUNTINGTON BANCSHARES INCORPORATED REPORTS 2022 SECOND-QUARTER EARNINGS Delivers Record Net Income and Achievement of Medium-Term Financial Targets Net Interest Income Increased 10% Sequentially and Continued Expense Reductions Drive Record PPNR 2022 Second-Quarter Highlights: • Earnings per common share (EPS) for the quarter were $0.35, an increase of $0.06 from the prior quarter. Excluding $0.01 per common share after-tax of

### Q9 CPB 2021-09-01 → label C: FTV 2021-02-04  (Industrials)
- encoders: **concat_eq_plus**  | mean=1.25
- same_dynamic=1  same_regime=2  same_surprise=1  mental_precedent=1
- notes: _CPB miss post-COVID bump; FTV beat recovery_
- summary: Fortive reported fourth-quarter 2020 results showing a 4.9% total revenue growth, driven by sequential improvements and strong SaaS revenue performance, with core operating margin expansion and significant increases in operating and free cash flow; the CEO expressed optimism about continued progress despite near-term uncertainties.
- text[:600]: > Document Exhibit 99.1 Fortive Reports Fourth Quarter 2020 Results • Continued sequential improvement drove total revenue growth of 4.9%, including a return to positive core revenue growth of 0.7% • Top-line performance supported by strong SaaS revenue growth • Strong core operating margin expansion (OMX), with positive core OMX at all segments • Operating cash flow +33% Y/Y to $329M; free cash flow +39% Y/Y to $313M EVERETT, WA, February 4, 2021 - Fortive Corporation (“Fortive”) (NYSE: FTV) today announced results for the fourth quarter 2020. For the fourth quarter ended December 31, 2020, net

### Q9 CPB 2021-09-01 → label G: PEG 2023-08-01  (Utilities)
- encoders: **random**  | mean=1.25
- same_dynamic=1  same_regime=1  same_surprise=2  mental_precedent=1
- notes: _Consumer staples normalization vs utility regulated growth_
- summary: PSEG reported strong second-quarter earnings with net income of $591 million and non-GAAP operating earnings of $351 million, up significantly from the previous year due to growth in regulated operations and higher average hedged prices. The company remains optimistic, re-affirming its full-year 2023 guidance range of $3.40 to $3.50 per share while highlighting ongoing investments in electric and natural gas infrastructure.
- text[:600]: > Public Service Enterprise Group 80 Park Plaza Newark, NJ 07102 CONTACTS: Media Relations Investor Relations Marijke Shugrue Carlotta Chan 908-531-4253 973-430-6565 Marijke.Shugrue@pseg.com Carlotta.Chan@pseg.com PSEG Announces Second Quarter 2023 Results $1.18 Per Share Net Income $0.70 Per Share Non-GAAP Operating Earnings Re-Affirms Full-Year 2023 Non-GAAP Operating EPS Guidance Range of $3.40 - $3.50 (NEWARK, N.J. – August 1, 2023) Public Service Enterprise Group (NYSE: PEG) reported second quarter 2023 Net Income of $591 million, or $1.18 per share, compared to Net Income of $131 million, 

### Q11 URI 2021-04-28 → label E: AFL 2020-10-27  (Financials)
- encoders: **random**  | mean=1.25
- same_dynamic=1  same_regime=1  same_surprise=2  mental_precedent=1
- notes: _Industrial recovery vs insurance tax windfall_
- summary: Aflac Incorporated reported third-quarter net earnings of $2.5 billion, driven primarily by a $1.4 billion benefit from new U.S. tax regulations that allowed for the release of valuation allowances on deferred tax benefits. The company remains optimistic about its financial performance despite challenges in its Japan segment, where revenues and profits declined due to limited-pay products reaching paid-up status.
- text[:600]: > Document News Release FOR IMMEDIATE RELEASE Aflac Incorporated Announces Third Quarter Results, Reports Third Quarter Net Earnings of $2.5 Billion, Results Reflect a Benefit from New Tax Regulations, Declares Fourth Quarter Cash Dividend COLUMBUS, Ga. - October 27, 2020 - Aflac Incorporated (NYSE: AFL) today reported its third quarter results. Total revenues were $5.7 billion in the third quarter of 2020, compared with $5.5 billion in the third quarter of 2019. Net earnings were $2.5 billion, or $3.44 per diluted share, compared with $777 million, or $1.04 per diluted share a year ago. The inc

### Q12 NDSN 2020-05-20 → label A: CLX 2020-05-01  (Consumer Staples)
- encoders: **concat_eq_plus**  | mean=1.25
- same_dynamic=1  same_regime=2  same_surprise=1  mental_precedent=1
- notes: _NDSN modest decline, CLX pandemic winner_
- summary: Clorox reported a 15% sales growth and a 31% increase in diluted EPS for its third quarter of fiscal year 2020, driven by the extraordinary demand for disinfecting products amid the COVID-19 pandemic. The company maintains an optimistic outlook, citing resilience during past recessions and strong future investments in their IGNITE strategy.
- text[:600]: > DATED MAY 1, 2020 OF THE CLOROX COMPANY PRESS RELEASE Clorox Reports Q3 Fiscal Year 2020 Results, Updates Fiscal Year Outlook OAKLAND, Calif., May 1, 2020 – The Clorox Company (NYSE:CLX) reported sales growth of 15% and an increase in diluted net earnings per share (diluted EPS) of 31% for its third quarter of fiscal year 2020, which ended March 31, 2020. The company delivered sales and earnings growth in all reportable segments. “Our hearts go out to everyone who has been affected by the COVID-19 pandemic. We’re privileged to be in a position to serve the public health during this time,” said

### Q12 NDSN 2020-05-20 → label C: TRGP 2024-08-01  (Energy)
- encoders: **random**  | mean=1.25
- same_dynamic=1  same_regime=1  same_surprise=2  mental_precedent=1
- notes: _COVID industrial miss vs energy record beat_
- summary: Targa Resources Corp. reported record second-quarter 2024 results with adjusted EBITDA reaching $984.3 million, driven by higher volumes across its Gathering and Processing and Logistics and Transportation systems, and announced a new $1 billion share repurchase program, signaling confidence in future growth.
- text[:600]: > 811 Louisiana, Suite 2100 Houston, TX 77002 713.584.1000 Targa Resources Corp. Reports Record Second Quarter 2024 Results and Increases Full Year 2024 Outlook HOUSTON – August 1, 2024 - Targa Resources Corp. (NYSE: TRGP) (“TRGP,” the “Company” or “Targa”) today reported second quarter 2024 results. Second quarter 2024 net income attributable to Targa Resources Corp. was $298.5 million compared to $329.3 million for the second quarter of 2023. The Company reported adjusted earnings before interest, income taxes, depreciation and amortization, and other non-cash items (“adjusted EBITDA”) (1) of 

### Q12 NDSN 2020-05-20 → label I: HD 2021-05-18  (Consumer Discretionary)
- encoders: **random**  | mean=1.25
- same_dynamic=1  same_regime=2  same_surprise=1  mental_precedent=1
- notes: _COVID drag vs COVID boom, opposite dynamics_
- summary: The Home Depot reported a significant increase in first-quarter sales by $9.2 billion, or 32.7%, driven by strong comparable sales growth of 31.0% and robust U.S. sales of 29.9%. The company attributes this success to strategic investments and the resilience of its associates amid unprecedented demand for home improvement projects, maintaining a confident tone throughout the release.
- text[:600]: > Document Exhibit 99.1 The Home Depot Announces First Quarter Results ATLANTA, May 18, 2021 -- The Home Depot ® , the world's largest home improvement retailer, today reported sales of $37.5 billion for the first quarter of fiscal 2021, an increase of $9.2 billion, or 32.7 percent from the first quarter of fiscal 2020. Comparable sales for the first quarter of fiscal 2021 increased 31.0 percent, and comparable sales in the U.S. increased 29.9 percent. Net earnings for the first quarter of fiscal 2021 were $4.1 billion, or $3.86 per diluted share, compared with net earnings of $2.2 billion, or $

### Q13 MMM 2019-04-25 → label A: PEG 2023-08-01  (Utilities)
- encoders: **random**  | mean=1.25
- same_dynamic=1  same_regime=2  same_surprise=1  mental_precedent=1
- notes: _miss+restructure vs beat+reaffirm, different sectors_
- summary: PSEG reported strong second-quarter earnings with net income of $591 million and non-GAAP operating earnings of $351 million, up significantly from the previous year due to growth in regulated operations and higher average hedged prices. The company remains optimistic, re-affirming its full-year 2023 guidance range of $3.40 to $3.50 per share while highlighting ongoing investments in electric and natural gas infrastructure.
- text[:600]: > Public Service Enterprise Group 80 Park Plaza Newark, NJ 07102 CONTACTS: Media Relations Investor Relations Marijke Shugrue Carlotta Chan 908-531-4253 973-430-6565 Marijke.Shugrue@pseg.com Carlotta.Chan@pseg.com PSEG Announces Second Quarter 2023 Results $1.18 Per Share Net Income $0.70 Per Share Non-GAAP Operating Earnings Re-Affirms Full-Year 2023 Non-GAAP Operating EPS Guidance Range of $3.40 - $3.50 (NEWARK, N.J. – August 1, 2023) Public Service Enterprise Group (NYSE: PEG) reported second quarter 2023 Net Income of $591 million, or $1.18 per share, compared to Net Income of $131 million, 

### Q13 MMM 2019-04-25 → label F: REG 2020-05-08  (Real Estate)
- encoders: **random**  | mean=1.25
- same_dynamic=1  same_regime=1  same_surprise=2  mental_precedent=1
- notes: _Different sector, COVID shock vs industrial slowdown_
- summary: Regency Centers reported first quarter 2020 results showing a net loss per diluted share of ($0.15) due to a non-cash goodwill impairment charge, while NAREIT FFO remained strong at $0.98 per diluted share. Despite the impact of the COVID-19 pandemic, which led to a decline in same property Net Operating Income by 0.7%, Regency expressed confidence in its well-positioned portfolio and healthy balance sheet, emphasizing its dedication to tenant support during these challenging times.
- text[:600]: > reg-ex991_121.htm Exhibit 99.1 NEWS RELEASE For immediate release Laura Clark 904 598 7831 LauraClark@RegencyCenters.com Regency Centers Reports First Quarter 2020 Results and Provides Business Update Related to COVID-19 JACKSONVILLE, FL (May 7, 2020) – Regency Centers Corporation (“Regency” or the “Company”) today reported financial and operating results for the period ended March 31, 2020, and provided a business update related to COVID-19. First Quarter 2020 Highlights • For the three months ended March 31, 2020, Net (Loss) Income Attributable to Common Stockholders (“Net Loss”) of ($0.15) 

### Q14 EMR 2023-08-02 → label C: VICI 2020-04-30  (Real Estate)
- encoders: **random**  | mean=1.25
- same_dynamic=1  same_regime=1  same_surprise=2  mental_precedent=1
- notes: _Industrials beat vs REIT pandemic stress_
- summary: VICI Properties Inc. reported its financial results for the quarter ended March 31, 2020, showing mixed performance; the company cited ongoing operational challenges due to the pandemic as the primary driver of its results. The tone is cautiously optimistic, with a focus on navigating through current difficulties.
- text[:600]: > Item 2.02. Results of Operations and Financial Condition. On April 30, 2020, VICI Properties Inc. (the “Company”) issued a press release announcing its financial results for the quarter ended March 31, 2020, and made available supplemental financial and operating information concerning the Company as of March 31, 2020. A copy of the press release and a copy of this supplemental information are furnished herewith as Exhibit 99.1 and Exhibit 99.2, respectively, to this Current Report on Form 8-K and are incorporated herein by reference.

### Q15 URI 2020-04-29 → label F: DGX 2021-10-21  (Health Care)
- encoders: **random**  | mean=1.25
- same_dynamic=1  same_regime=1  same_surprise=2  mental_precedent=1
- notes: _URI crisis withdrawal vs DGX raise guidance_
- summary: Quest Diagnostics reported third-quarter 2021 revenues of $2.77 billion, down slightly from the previous year but raised its full-year outlook due to higher-than-expected COVID-19 testing volumes and base business performance, reflecting a confident tone despite some softness in the base business during late summer.
- text[:600]: > Document Quest Diagnostics Reports Third Quarter 2021 Financial Results, Raises Outlook for Full Year 2021 • Third quarter revenues of $2.77 billion, down 0.4% from 2020 • Third quarter reported diluted earnings per share ("EPS") of $4.02, down 2.8% from 2020; and adjusted diluted EPS of $3.96, down 7.9% from 2020 • Year to date cash provided by operations of $1.75 billion, up 19.6% from 2020 • Raises full year 2021 outlook to reflect higher than anticipated COVID-19 testing volumes and base business performance SECAUCUS, N.J., Oct. 21, 2021 - Quest Diagnostics Incorporated (NYSE: DGX), the wo

### Q1 COHR 2020-08-13 → label F: NRG 2019-05-02  (Utilities)
- encoders: **random**  | mean=1.50
- same_dynamic=1  same_regime=1  same_surprise=3  mental_precedent=1
- notes: _IT vs Utilities, macro regime very different_
- summary: NRG Energy, Inc. reported strong first-quarter results with a focus on capital allocation and operational readiness, including the completion of $500 million in its $1 billion 2019 share repurchase program and the planned return to service of the Gregory plant, while reaffirming its 2019 guidance. The company's confident tone reflects progress on strategic initiatives despite challenges in the retail sector.
- text[:600]: > Document Exhibit 99.1 NRG Energy, Inc. Reports First Quarter 2019 Results • Completed $500 million of the $1 billion 2019 share repurchase program • Returning to service 385 MW Combined Cycle Gas Turbine Gregory plant in ERCOT this summer • Reaffirming 2019 guidance PRINCETON, NJ - May 2, 2019 - NRG Energy, Inc. (NYSE: NRG) today reported first quarter 2019 income from continuing operations of $94 million , or $1.72 per diluted common share and Adjusted EBITDA for the first quarter was $333 million . “Our integrated platform delivered strong first quarter results,” said Mauricio Gutierrez, NRG

### Q2 HPE 2020-05-21 → label E: FDX 2020-09-15  (Industrials)
- encoders: **random**  | mean=1.50
- same_dynamic=1  same_regime=3  same_surprise=1  mental_precedent=1
- notes: _HPE miss+restructure vs FDX beat+volume surge_
- summary: FedEx Corp. reported strong first-quarter results with significant growth in revenue and operating income, driven by volume increases and yield improvements across its services. The company's CEO highlighted strategic investments and team efforts amid global challenges, while the CFO expressed cautious optimism about future earnings despite ongoing uncertainties.
- text[:600]: > fdx-ex991_6.htm Exhibit 99.1 FedEx Corp. Reports Strong First Quarter Results MEMPHIS, Tenn., September 15, 2020 ... FedEx Corp. (NYSE: FDX) today reported the following consolidated results for the first quarter ended August 31 (adjusted measures exclude TNT Express integration expenses as described below): Fiscal 2021 Fiscal 2020 As Reported (GAAP) Adjusted (non-GAAP) As Reported (GAAP) Adjusted (non-GAAP) Revenue $19.3 billion $19.3 billion $17.0 billion $17.0 billion Operating income $1.59 billion $1.64 billion $0.98 billion $1.05 billion Operating margin 8.2% 8.5% 5.7% 6.1% Net income $1.

### Q4 ALGN 2019-04-24 → label C: ES 2023-11-06  (Utilities)
- encoders: **random**  | mean=1.50
- same_dynamic=1  same_regime=2  same_surprise=2  mental_precedent=1
- notes: _Different sector, story, macro regime entirely_
- summary: Eversource Energy and its subsidiaries reported their financial performance for the third quarter of 2023 in a press release, highlighting operational results; the driver mentioned was strong utility operations and stable customer demand. The tone is cautiously optimistic, with management set to discuss these results during an upcoming conference call.
- text[:600]: > false 0000072741 8-K 2023-11-06 false 0000023426 ̈ ̈ ̈ ̈ 8-K 2023-11-06 false 0000013372 ̈ ̈ ̈ ̈ 0000315256 ̈ 8-K 2023-11-06 false ̈ ̈ ̈ 0000072741 2023-11-06 2023-11-06 0000072741 es:TheConnecticutLightAndPowerCompanyMember 2023-11-06 2023-11-06 0000072741 es:NstarElectricCompanyMember 2023-11-06 2023-11-06 0000072741 es:PublicServiceCompanyOfNewHampshireMember 2023-11-06 2023-11-06 iso4217:USD xbrli:shares iso4217:USD xbrli:shares UNITED STATES SECURITIES AND EXCHANGE COMMISSION Washington, D.C. 20549 FORM 8-K CURRENT REPORT Pursuant to Section 13 or 15(d) of the Securities Exchange Act of 1

### Q6 EQR 2024-01-30 → label C: PFE 2021-05-04  (Health Care)
- encoders: **random**  | mean=1.50
- same_dynamic=1  same_regime=1  same_surprise=3  mental_precedent=1
- notes: _REIT vs pharma, totally different drivers_
- summary: Pfizer reported strong first-quarter 2021 results, with revenues growing 42% to $14.6 billion, driven primarily by the updated expectations for contributions from BNT162b2 and the company's continued strong performance across its business. The company remains optimistic about its future prospects, as evidenced by the raised full-year guidance and maintained dividend, despite increased R&D investments in vaccines and other programs.
- text[:600]: > Document Exhibit 99 PFIZER REPORTS STRONG FIRST-QUARTER 2021 RESULTS ▪ First-Quarter 2021 Revenues of $14.6 Billion, Reflecting 42% Operational Growth; Excluding Revenues for BNT162b2 of $3.5 Billion, Revenues Grew 8% Operationally Including a Negative 5% Impact from Pricing ▪ First-Quarter 2021 Reported Diluted EPS (1) of $0.86, Adjusted Diluted EPS (2) of $0.93 ▪ Raises Full-Year 2021 Guidance (3) for Revenues to a Range of $70.5 to $72.5 Billion and Adjusted Diluted EPS (2) to a Range of $3.55 to $3.65, Primarily Reflecting Updates to Anticipated Contributions from BNT162b2 Partially Offset

### Q6 EQR 2024-01-30 → label H: YUM 2021-07-29  (Consumer Discretionary)
- encoders: **random**  | mean=1.50
- same_dynamic=1  same_regime=1  same_surprise=3  mental_precedent=1
- notes: _REIT vs QSR, macro regimes opposite_
- summary: Yum! Brands reported strong second-quarter results with record unit development and significant same-store sales growth of 23%, attributing the success to investments in digital and off-premise capabilities, as well as the resilience of its diversified global business. CEO David Gibbs expressed optimism about future growth, reinstating a higher unit guidance range of 4% to 5%.
- text[:600]: > Document NEWS Jodi Dyer Vice President, Investor Relations and CFO, Digital & Technology Yum! Brands Reports Second-Quarter Results; Record 603 Net-New Units; Digital System Sales of Over $5 Billion; Same-Store Sales Growth of 23%; Reinstates Long-Term Growth Algorithm with Raised Unit Guidance Louisville, KY (July 29, 2021) - Yum! Brands, Inc. (NYSE: YUM) today reported results for the second-quarter ended June 30, 2021. Worldwide system sales excluding foreign currency translation grew 26%, with 23% same-store sales and 2% unit growth. Second-quarter GAAP EPS was $1.29, an increase of 91% ov

### Q7 NUE 2023-04-20 → label G: RMD 2020-08-05  (Health Care)
- encoders: **random**  | mean=1.50
- same_dynamic=1  same_regime=1  same_surprise=3  mental_precedent=1
- notes: _Steel cyclical vs healthcare COVID; macro regimes opposite_
- summary: ResMed Inc. reported strong fourth-quarter results with year-over-year revenue growth of 9% and a 24% increase in non-GAAP operating profit, driven by the company's resilience during an uncertain environment and increased manufacturing for COVID-19 responses. The CEO expressed confidence in navigating through ongoing challenges while supporting the reopening of sleep labs and physician practices and accelerating digital health solutions adoption.
- text[:600]: > For investors For media Amy Wakeham Jayme Rubenstein +1 858-836-5000 +1 858-836-6798 investorrelations@resmed.com news@resmed.com ResMed Inc. Announces Results for the Fourth Quarter of Fiscal Year 2020 – Year-over-year revenue grows 9%, non-GAAP operating profit up 24% Note: A webcast of ResMed’s conference call will be available at 4:30 p.m. ET today at http://investor.resmed.com SAN DIEGO, August 5, 2020 – ResMed Inc. (NYSE: RMD, ASX: RMD), a world-leading digital health company, today announced results for its quarter ended June 30, 2020. Fourth Quarter 2020 Highlights All comparisons are 

### Q8 OXY 2018-08-08 → label E: ES 2025-02-11  (Utilities)
- encoders: **random**  | mean=1.50
- same_dynamic=1  same_regime=1  same_surprise=3  mental_precedent=1
- notes: _Energy vs Utilities, macro regimes totally different_
- summary: Eversource Energy reported strong full-year 2024 earnings of $811.7 million, or $2.27 per share, compared to a loss in the previous year, driven by operational excellence and strategic divestitures. The company remains optimistic about future growth, projecting long-term earnings per share growth between 5% to 7%, despite some near-term headwinds.
- text[:600]: > Eversource Energy Reports Full-Year & Fourth Quarter 2024 Results HARTFORD, Conn. and BOSTON, Mass. (February 11, 2025) – Eversource Energy (NYSE: ES) today reported full-year 2024 earnings of $811.7 million, or $2.27 per share, compared with a full-year 2023 loss of $(442.2) million, or $(1.26) per share. Eversource also reported fourth quarter 2024 earnings of $72.5 million, or $0.20 per share, compared with a fourth quarter 2023 loss of $(1,288.5) million, or $(3.68) per share. Non-GAAP recurring earnings totaled $1,634.0 million 1 , or $4.57 per share 1 , for the full-year 2024, and $370.8

### Q8 OXY 2018-08-08 → label G: MNST 2022-05-05  (Consumer Staples)
- encoders: **random**  | mean=1.50
- same_dynamic=1  same_regime=2  same_surprise=2  mental_precedent=1
- notes: _Energy vs staples, different drivers entirely_
- summary: Monster Beverage reported a 22.1% increase in first-quarter net sales to $1.52 billion, driven by significant cost increases due to higher freight rates, fuel costs, and input prices. The company remains optimistic despite these challenges, as evidenced by its strategic acquisition of CANarchy Craft Brewery Collective LLC and plans for a price increase effective September 1, 2022.
- text[:600]: > PondelWilkinson Inc. 2945 Townsgate Road, Suite 200 Westlake Village, CA 91361 Investor Relations T (310) 279 5980 Strategic Public Relations W www.pondel.com CONTACTS: Rodney C. Sacks Chairman and Co-Chief Executive Officer (951)739-6200 NEWS RELEASE Hilton H. Schlosberg Vice Chairman and Co-Chief Executive Officer (951)739-6200 Roger S. Pondel / Judy Lin Sfetcu PondelWilkinson Inc. (310)279-5980 MONSTER BEVERAGE REPORTS 2022 FIRST QUARTER RESULTS -- Record First Quarter Net Sales Rise 22.1 Percent to $1.52 Billion – -- Company Completes its Acquisition of CANarchy Craft Brewery Collective LL

### Q8 OXY 2018-08-08 → label H: VEEV 2025-03-05  (Health Care)
- encoders: **random**  | mean=1.50
- same_dynamic=1  same_regime=1  same_surprise=3  mental_precedent=1
- notes: _Energy vs SaaS, macro regimes totally different_
- summary: Veeva Systems Inc. reported strong fourth quarter and fiscal year 2025 results, with total revenues up 16% year over year to $2,746.6 million, driven by a 20% increase in subscription services revenues. CEO Peter Gassner expressed optimism about the company's future, highlighting recent innovations and strategic partnerships that position Veeva well for continued growth.
- text[:600]: > Document Exhibit 99.1 FOR IMMEDIATE RELEASE Veeva Announces Fourth Quarter and Fiscal Year 2025 Results Fiscal Year 2025 Total Revenues of $2,746.6M, up 16% Year Over Year Q4 Total Revenues of $720.9M, up 14% Year Over Year Fiscal Year 2025 Subscription Services Revenues of $2,284.7M, up 20% Year Over Year Q4 Subscription Services Revenues of $608.6M, up 17% Year Over Year PLEASANTON, CA - March 5, 2025 - Veeva Systems Inc. (NYSE: VEEV), a leading provider of industry cloud solutions for the global life sciences industry, today announced results for its fourth quarter and fiscal year ended Jan

### Q9 CPB 2021-09-01 → label B: OXY 2019-05-06  (Energy)
- encoders: **concat_eq**  | mean=1.50
- same_dynamic=1  same_regime=2  same_surprise=2  mental_precedent=1
- notes: _Consumer staples miss vs energy beat, unrelated_
- summary: Occidental Petroleum reported strong first quarter 2019 results, exceeding guidance across all business segments due to higher production volumes and favorable pricing, with the CEO expressing pride in executing its returns-focused strategy. The company returned over $800 million to shareholders through dividends and share repurchases, maintaining a confident tone.
- text[:600]: > Occidental Announces 1st Quarter 2019 Results · Returned over $800 million to shareholders through dividends and share repurchases · Exceeded pre-tax income guidance for both Chemical and Midstream and Marketing · Exceeded the high end of guidance with production of 719,000 BOE per day · Permian Resources production of 261,000 BOE per day · of $631 million, or $0.84 per diluted share. Net and core income for the fourth quarter of 2018 was $706 million, or $0.93 per diluted share, and $922 million, or $1.22 per diluted share, respectively. “We’re proud to have completed another strong quarter w

### Q9 CPB 2021-09-01 → label F: SMCI 2021-11-02  (Information Technology)
- encoders: **random**  | mean=1.50
- same_dynamic=1  same_regime=3  same_surprise=1  mental_precedent=1
- notes: _Opposite stories: CPB miss, SMCI beat+raise_
- summary: Supermicro reported first quarter fiscal year 2022 financial results with a 35% year-over-year revenue growth, exceeding $1 billion for the second consecutive quarter, driven by strong design win momentum and shipment growth to key global customers in various markets. The company remains optimistic about future growth, projecting significant increases in net sales and earnings per share for the upcoming quarters despite ongoing supply chain challenges.
- text[:600]: > Document Exhibit 99.1 Supermicro Announces First Quarter Fiscal Year 2022 Financial Results SAN JOSE, Calif. -- November 2 , 2021 (BUSINESS WIRE) -- Super Micro Computer, Inc. (Nasdaq: SMCI) , a global leader in high-performance, high-efficiency server and storage technology and green computing, today announced financial results for its first quarter of fiscal year 2022 ended September 30, 2021. First Quarter Fiscal Year 2022 Highlights • Net sales of $1.03 billion versus $1.07 billion in the fourth quarter of fiscal year 2021 and $762 million in the same quarter of last year. • Gross margin o

### Q9 CPB 2021-09-01 → label H: BAX 2022-07-28  (Health Care)
- encoders: **random**  | mean=1.50
- same_dynamic=1  same_regime=2  same_surprise=2  mental_precedent=1
- notes: _Different sector, different direction, different cause_
- summary: Baxter International Inc. reported strong second-quarter 2022 results with revenue increasing 21% on a reported basis, driven by the acquisition of Hillrom and a diverse portfolio of essential healthcare products. The company remains optimistic despite macroeconomic headwinds, expecting full-year sales growth in the high teens on a reported basis and adjusted earnings per share between $3.60 to $3.70.
- text[:600]: > Document Exhibit 99.1 FOR IMMEDIATE RELEASE BAXTER REPORTS SECOND-QUARTER 2022 RESULTS • Second-quarter revenue of $3.75 billion increased 21% on a reported basis, 26% on a constant currency basis and 3% on an operational basis 1 • Second-quarter U.S. GAAP earnings per share (EPS) totaled $0.50; Adjusted EPS totaled $0.87 • Baxter now expects full-year 2022 sales growth to advance in the high teens on a reported basis, mid-20s on a constant currency basis and 2% to 3% on an operational basis • Baxter now expects full-year U.S. GAAP EPS of $1.82 to $1.92 and adjusted EPS of $3.60 to $3.70 DEERF

### Q10 TAP 2021-04-29 → label G: LOW 2020-11-18  (Consumer Discretionary)
- encoders: **random**  | mean=1.50
- same_dynamic=1  same_regime=2  same_surprise=2  mental_precedent=1
- notes: _TAP miss+reaffirm vs LOW beat+raise_
- summary: Lowe's reported a third-quarter 2020 sales increase of 30.4% with diluted EPS of $0.91, driven by strong execution amid continued high demand and significant investments in store safety and community support due to the pandemic; the company remains confident in its strategic investments for long-term growth despite a $1.1 billion pre-tax loss from debt extinguishment.
- text[:600]: > Document Exhibit 99.1 November 18, 2020 For 6:00 am ET Release LOWE’S REPORTS THIRD QUARTER 2020 SALES AND EARNINGS RESULTS — U.S. Comparable Sales Increased 30.4% — — Diluted EPS of $0.91 which Includes $1.05 Negative Impact from Extinguishment of Debt — — Adjusted Diluted EPS of $1.98 1 — — Lowes.com Sales Increased 106% — — Company Invested over $1.1 Billion Year-to-Date to Support Associates, Store Safety and Communities in Response to COVID-19 — — Company Provides Fourth Quarter 2020 Financial Outlook — MOORESVILLE, N.C. - Lowe’s Companies, Inc. (NYSE: LOW) today reported net earnings of 

### Q12 NDSN 2020-05-20 → label B: VRTX 2020-04-29  (Health Care)
- encoders: **concat_eq_plus**  | mean=1.50
- same_dynamic=1  same_regime=3  same_surprise=1  mental_precedent=1
- notes: _NDSN mild miss; VRTX strong beat+raise_
- summary: Vertex Pharmaceuticals reported strong first-quarter financial results, with product revenues increasing 77% year-over-year due to the uptake of TRIKAFTA in the U.S. and following key reimbursement agreements outside the U.S., leading to a significant increase in revenue and raising full-year guidance for total cystic fibrosis (CF) product revenues. CEO Reshma Kewalramani expressed confidence in Vertex's ability to continue delivering on its mission despite global challenges posed by the COVID-19 pandemic, highlighting the rapid uptake of TRIKAFTA and ongoing pipeline investments.
- text[:600]: > Exhibit Vertex Reports First-Quarter 2020 Financial Results -Product revenues of $ 1.52 billion , a 77% increase compared to Q1 2019- -Company raises revenue guidance; now expects 2020 CF revenues of $5.3 to $5.6 billion- BOSTON -- Vertex Pharmaceuticals Incorporated (Nasdaq: VRTX) today reported consolidated financial results for the first quarter ended March 31, 2020 and revised upward its full-year 2020 financial guidance for total cystic fibrosis (CF) product revenues. "The COVID-19 pandemic has presented unprecedented challenges to societies, communities and businesses around the world, a

### Q13 MMM 2019-04-25 → label H: URI 2018-07-18  (Industrials)
- encoders: **concat_eq_plus**  | mean=1.50
- same_dynamic=1  same_regime=3  same_surprise=1  mental_precedent=1
- notes: _MMM miss+restructure vs URI beat+raise_
- summary: United Rentals, Inc. reported strong second-quarter 2018 results with significant revenue growth driven by higher volume and rates, and raised its 2018 guidance following the tax rate reduction from the Tax Cuts and Jobs Act. The company's CEO expressed confidence in a durable cycle and continued industry discipline, emphasizing a balanced strategy of growth and returns.
- text[:600]: > Exhibit Exhibit 99.1 United Rentals, Inc. 100 First Stamford Place Suite 700 Stamford, CT 06902 Telephone: 203 622 3131 Fax: 203 622 6080 unitedrentals.com United Rentals Announces Second Quarter 2018 Results and Raises 2018 Guidance STAMFORD, Conn. – July 18, 2018 – United Rentals, Inc. (NYSE: URI) today announced financial results for the second quarter 2018 1 . Total revenue was $ 1.891 billion and rental revenue was $ 1.631 billion for the second quarter, compared with $ 1.597 billion and $ 1.367 billion , respectively, for the same period last year. On a GAAP basis, the company reported s

### Q14 EMR 2023-08-02 → label B: MET 2024-10-30  (Financials)
- encoders: **random**  | mean=1.50
- same_dynamic=1  same_regime=2  same_surprise=2  mental_precedent=1
- notes: _Industrials automation vs insurance financials, unrelated_
- summary: MetLife, Inc. reported a significant increase in third-quarter 2024 net income to $1.3 billion, or $1.81 per share, compared to $422 million, or $0.56 per share, in the same period last year, driven by strong book value growth and an adjusted return on equity of 14.6%. The company's CEO expressed confidence in its business model despite lower variable investment income, indicating a cautious but optimistic tone.
- text[:600]: > Document Exhibit 99.1 For Immediate Release İ Global Communications İ MetLife, Inc. METLIFE ANNOUNCES THIRD QUARTER 2024 RESULTS NEW YORK, October 30, 2024 - MetLife, Inc. (NYSE: MET) today announced its third quarter 2024 results. Third Quarter Results Summary • Net income of $1.3 billion, or $1.81 per share, compared to net income of $422 million, or $0.56 per share, in the third quarter of 2023. • Adjusted earnings of $1.4 billion, or $1.95 per share, compared to adjusted earnings of $1.5 billion, or $1.97 per share, in the third quarter of 2023. • Book value of $39.02 per share, up 33 perc

### Q15 URI 2020-04-29 → label I: COP 2021-08-03  (Energy)
- encoders: **random**  | mean=1.50
- same_dynamic=1  same_regime=2  same_surprise=2  mental_precedent=1
- notes: _Crisis defense vs post-recovery beat; opposite contexts_
- summary: ConocoPhillips delivered strong second-quarter 2021 financial results with earnings of $2.1 billion, driven by higher realized prices and volumes following the company's recent 10-year market update that reaffirmed its commitment to the energy transition while maintaining sector-leading returns on capital. The CEO expressed confidence in the company’s multi-year plan and resilience, emphasizing its unique position to deliver through industry price cycles.
- text[:600]: > ConocoPhillips Delivers Strong Second-Quarter 2021 Financial and Operational Results Following Recent 10-Year Market Update Reported earnings of $2.1 billion; adjusted earnings of $1.7 billion. Generated cash provided by operating activities of $4.3 billion; cash from operations of $4.0 billion. Produced 1,547 MBOED excluding Libya. HOUSTON--(BUSINESS WIRE)--August 3, 2021--ConocoPhillips (NYSE: COP) today reported second-quarter 2021 earnings of $2.1 billion, or $1.55 per share, compared with second-quarter 2020 earnings of $0.3 billion, or $0.24 per share. Excluding special items, second-qua

### Q1 COHR 2020-08-13 → label B: OXY 2022-02-24  (Energy)
- encoders: **random**  | mean=1.75
- same_dynamic=1  same_regime=2  same_surprise=3  mental_precedent=1
- notes: _Tech vs energy, totally different drivers_
- summary: Occidental Petroleum reported strong fourth-quarter 2021 earnings, exceeding guidance and setting new operational records, driven by higher commodity prices and efficient production. The company also announced a new shareholder return framework and significant debt reduction targets, positioning itself for continued financial improvement in 2022.
- text[:600]: > Document PRESS RELEASE Occidental Announces 4th Quarter 2021 Results • Announced new shareholder return framework and additional debt reduction target • Earnings per share of $1.37 per diluted share and adjusted earnings per share of $1.48 per diluted share • Cash flow from continuing operations of $3.2 billion and cash flow from continuing operations, before working capital of $3.9 billion • Capital spending of $937 million, resulting in record free cash flow, excluding working capital of over $2.9 billion • Reduced debt maturities by $2.2 billion through debt tender and 2022 maturity call pr

### Q2 HPE 2020-05-21 → label G: ESS 2020-08-03  (Real Estate)
- encoders: **concat_eq_plus**  | mean=1.75
- same_dynamic=1  same_regime=3  same_surprise=2  mental_precedent=1
- notes: _IT hardware miss vs REIT stable income_
- summary: Essex Property Trust, Inc. reported its financial results for the three and six months ended June 30, 2020, highlighting strong performance driven by robust rental income and occupancy rates; the press release maintains a confident tone regarding future prospects.
- text[:600]: > Item 2.02. Results of Operations and Financial Condition. On August 3, 2020, Essex Property Trust, Inc. (the “Company”) issued a press release and supplemental information announcing the Company’s financial results for the three and six months ended June 30, 2020. The Company has posted a copy of the press release and supplemental information on the Company’s website at www.essex.com. A copy of the press release and supplemental information is attached hereto as Exhibit 99.1 and incorporated by reference herein. The information in this report (including Exhibit 99.1) is being furnished pursuan

### Q2 HPE 2020-05-21 → label I: VICI 2020-04-30  (Real Estate)
- encoders: **concat_eq**  | mean=1.75
- same_dynamic=1  same_regime=3  same_surprise=2  mental_precedent=1
- notes: _Different sector, story, reaction direction_
- summary: VICI Properties Inc. reported its financial results for the quarter ended March 31, 2020, showing mixed performance; the company cited ongoing operational challenges due to the pandemic as the primary driver of its results. The tone is cautiously optimistic, with a focus on navigating through current difficulties.
- text[:600]: > Item 2.02. Results of Operations and Financial Condition. On April 30, 2020, VICI Properties Inc. (the “Company”) issued a press release announcing its financial results for the quarter ended March 31, 2020, and made available supplemental financial and operating information concerning the Company as of March 31, 2020. A copy of the press release and a copy of this supplemental information are furnished herewith as Exhibit 99.1 and Exhibit 99.2, respectively, to this Current Report on Form 8-K and are incorporated herein by reference.

### Q3 STE 2021-08-09 → label F: KMB 2021-10-25  (Consumer Staples)
- encoders: **random**  | mean=1.75
- same_dynamic=1  same_regime=3  same_surprise=2  mental_precedent=1
- notes: _STE beat+raise; KMB miss+cut on costs_
- summary: Kimberly-Clark reported third-quarter 2021 results showing organic sales growth of 4% and earnings per share of $1.62, but the company's outlook was downgraded due to significant input cost inflation. Despite these challenges, Chairman and CEO Mike Hsu expressed confidence in the company’s strategy and its ability to create long-term shareholder value.
- text[:600]: > EARNINGS RELEASE Document Exhibit 99.1 KIMBERLY-CLARK ANNOUNCES THIRD QUARTER 2021 RESULTS DALLAS, October 25, 2021-Kimberly-Clark Corporation (NYSE: KMB) today reported third quarter 2021 results. Executive Summary • Third quarter 2021 net sales of $5.0 billion increased 7 percent compared to the year-ago period, with an organic sales increase of 4 percent. • Diluted net income per share for the third quarter was $1.39 in 2021 and $1.38 in 2020. • Third quarter adjusted earnings per share were $1.62 in 2021 compared to $1.72 in 2020. Adjusted earnings per share exclude certain items described

### Q4 ALGN 2019-04-24 → label B: CBOE 2018-11-02  (Financials)
- encoders: **concat_eq**  | mean=1.75
- same_dynamic=1  same_regime=2  same_surprise=3  mental_precedent=1
- notes: _Different sector, story, macro regime entirely_
- summary: Cboe Global Markets reported strong financial results for the third quarter of 2018, with diluted EPS up 43% and adjusted diluted EPS increasing by 19%, driven by successful product launches and a diverse offering that positioned the company well to deliver value. The tone is optimistic as the CEO highlights ongoing growth initiatives and long-term shareholder value despite facing some market challenges.
- text[:600]: > cboe_Ex99_1 Exhibit 99.1 News Release Page 1 of 12 Cboe Global Markets Reports Results for Third Quarter 2018 Third Quarter 2018 Highlights* · Diluted EPS of $0.76, up 43 Percent · Adjusted Diluted EPS of $1.061, up 19 Percent · Net Revenue of $270.5 Million Compared to $269.7 Million in Third Quarter 2017 · $84 Million of Capital Returned to Shareholders CHICAGO, IL – November 2, 2018 - Cboe Global Markets, Inc. (Cboe: CBOE) today reported financial results for the third quarter of 2018. Consolidated results for year-to-date 2017 include Bats Global Markets (Bats) for the period March 1 throu

### Q4 ALGN 2019-04-24 → label D: CF 2021-02-17  (Materials)
- encoders: **concat_eq_plus**  | mean=1.75
- same_dynamic=1  same_regime=2  same_surprise=3  mental_precedent=1
- notes: _Different sectors, drivers, and business context_
- summary: CF Industries Holdings, Inc. reported strong financial results for 2020, including net earnings of $317 million and EBITDA of $1,316 million, driven by global demand and rising energy prices that positively impacted nitrogen products. The company remains optimistic about the outlook for 2021, citing favorable industry dynamics and a continued focus on clean energy as a growth platform.
- text[:600]: > Document 4 Parkway North, Suite 400 Deerfield, IL 60015 www.cfindustries.com CF Industries Holdings, Inc. Reports Full Year 2020 Net Earnings of $317 Million, EBITDA of $1,316 Million, Adjusted EBITDA of $1,350 Million Operational Performance: Safety, Production and Sales Volume Records Strong Global Demand, Rising Global Energy Prices Drive Positive Nitrogen Outlook Continued Focus on Clean Energy as Long-Term Growth Platform DEERFIELD, IL—February 17, 2021—CF Industries Holdings, Inc. (NYSE: CF), a leading global manufacturer of hydrogen and nitrogen products, today announced results for its

### Q5 AJG 2023-07-27 → label G: BMY 2023-04-27  (Health Care)
- encoders: **concat_eq_plus**  | mean=1.75
- same_dynamic=1  same_regime=2  same_surprise=3  mental_precedent=1
- notes: _Insurance broker vs pharma, unrelated dynamics_
- summary: Bristol Myers Squibb reported first-quarter revenues of $11.3 billion, driven by strong growth from in-line products and new product portfolio, despite a 3% decrease due to Revlimid generic erosion and foreign exchange impacts. The company remains confident in its strategic priorities, affirming its non-GAAP financial guidance for 2023 while adjusting GAAP EPS guidance upward.
- text[:600]: > OF BRISTOL-MYERS SQUIBB COMPANY DATED APRIL 27, 2023 Document Exhibit 99.1 Bristol Myers Squibb Reports First Quarter Financial Results for 2023 • Reports First Quarter Revenues of $11.3 Billion • Posts First Quarter GAAP Earnings Per Share of $1.07 and Non-GAAP EPS of $2.05; Includes Net Impact of ($0.01) Per Share for GAAP and Non-GAAP EPS Due to Acquired IPRD Charges and Licensing Income • Delivers Strong Revenue Growth of 8% from In-Line Products and New Product Portfolio; or 10% When Adjusted for Foreign Exchange • Further Advances Portfolio Renewal Strategy, Achieving Important Milestone

### Q6 EQR 2024-01-30 → label F: NUE 2024-04-22  (Materials)
- encoders: **concat_eq**  | mean=1.75
- same_dynamic=1  same_regime=2  same_surprise=3  mental_precedent=1
- notes: _REIT vs steel; unrelated sectors and dynamics_
- summary: Nucor reported a strong first-quarter 2024 performance with net earnings attributable to Nucor stockholders of $844.8 million, or $3.46 per diluted share, driven by higher average selling prices and increased volumes, particularly at its sheet mills. The company remains optimistic despite steel market conditions easing from post-pandemic highs, as evidenced by Leon Topalian's comments on advancing growth, sustainability, and commercial strategies.
- text[:600]: > News Release Nucor Reports Results for the First Quarter of 2024 First Quarter of 2024 Highlights • Net earnings attributable to Nucor stockholders of $844.8 million, or $3.46 per diluted share. • Net sales of $8.14 billion. • Net earnings before noncontrolling interests of $959.0 million; EBITDA of $1.50 billion. CHARLOTTE, N.C. – April 22, 2024 - Nucor Corporation (NYSE: NUE) today announced consolidated net earnings attributable to Nucor stockholders of $844.8 million, or $3.46 per diluted share, for the first quarter of 2024. By comparison, Nucor reported consolidated net earnings attribut

### Q7 NUE 2023-04-20 → label C: ALB 2023-01-24  (Materials)
- encoders: **concat_eq_plus**  | mean=1.75
- same_dynamic=1  same_regime=3  same_surprise=2  mental_precedent=1
- notes: _Steel cycle vs lithium strategic update_
- summary: Albemarle Corporation released its fourth-quarter and fiscal-year-end financial results for 2022 along with a new five-year outlook on January 23, 2023, highlighting growth drivers in the lithium market; the press release maintains an optimistic tone regarding future prospects.
- text[:600]: > Item 2.02. Results of Operations and Financial Condition. On January 23, 2023, Albemarle Corporation (the “Company”) issued a press release announcing a strategic update including a new five-year outlook and preliminary financial results for the fourth quarter and fiscal year ended December 31, 2022. A copy of this press release is attached hereto as Exhibit 99.1 and incorporated by reference herein. In accordance with General Instruction B.2 of Form 8-K, the information in this Current Report on Form 8-K, including Exhibit 99.1, shall not be deemed “filed” for the purposes of Section 18 of th

### Q7 NUE 2023-04-20 → label D: HBAN 2022-07-21  (Financials)
- encoders: **random**  | mean=1.75
- same_dynamic=1  same_regime=2  same_surprise=3  mental_precedent=1
- notes: _Steel vs bank, unrelated drivers_
- summary: Huntington Bancshares Incorporated reported record second-quarter earnings, achieving $539 million in net income or $0.35 per common share, up from the prior quarter due to robust loan growth, increased deposit balances, and higher interest rates. CEO Steve Steinour expressed satisfaction with the performance, highlighting cost synergies from recent acquisitions and strong credit metrics, while emphasizing the franchise's growth potential and commitment to customer satisfaction.
- text[:600]: > Document Exhibit 99.1 July 21, 2022 Analysts: Tim Sedabres (timothy.sedabres@huntington.com), 952.745.2766 Media: Allison Gabrys (corpmedia@huntington.com), 248.961.3978 HUNTINGTON BANCSHARES INCORPORATED REPORTS 2022 SECOND-QUARTER EARNINGS Delivers Record Net Income and Achievement of Medium-Term Financial Targets Net Interest Income Increased 10% Sequentially and Continued Expense Reductions Drive Record PPNR 2022 Second-Quarter Highlights: • Earnings per common share (EPS) for the quarter were $0.35, an increase of $0.06 from the prior quarter. Excluding $0.01 per common share after-tax of

### Q7 NUE 2023-04-20 → label E: KMB 2019-10-22  (Consumer Staples)
- encoders: **concat_eq**  | mean=1.75
- same_dynamic=1  same_regime=2  same_surprise=3  mental_precedent=1
- notes: _Steel vs consumer staples, unrelated dynamics_
- summary: Kimberly-Clark reported third-quarter 2019 results with strong organic sales growth of 4 percent and raised its full-year outlook, citing robust performance in profit margins and earnings per share. The company's CEO expressed optimism about ongoing progress despite increased investments for long-term success.
- text[:600]: > EARNINGS RELEASE Exhibit Exhibit 99.1 Terry Balluck 972-281-1397 terry.balluck@kcc.com KIMBERLY-CLARK ANNOUNCES THIRD QUARTER 2019 RESULTS DALLAS, October 22, 2019-Kimberly-Clark Corporation (NYSE: KMB) today reported third quarter 2019 results and raised its outlook for full-year 2019 organic sales growth and earnings per share. Executive Summary • Third quarter 2019 net sales of $4.6 billion increased 1 percent compared to the year-ago period. Organic sales increased 4 percent. • Diluted net income per share for the third quarter was $1.94 in 2019 and $1.29 in 2018. • Third quarter adjusted 

### Q7 NUE 2023-04-20 → label H: EIX 2024-02-22  (Utilities)
- encoders: **concat_eq**  | mean=1.75
- same_dynamic=1  same_regime=2  same_surprise=3  mental_precedent=1
- notes: _Steel cyclical vs regulated utility, unrelated_
- summary: Edison International reported fourth-quarter GAAP earnings per share of $0.99 and core EPS of $1.28, exceeding expectations due to higher revenue from a rate case decision and lower maintenance costs. The company remains optimistic about its long-term growth targets, reiterating an annual core EPS growth rate of 5%-7% through 2028.
- text[:600]: > EDISON Exhibit 99.1 ​ ​ NEWS ​ ​ ​ ​ ​ ​ ​ Investor Relations : Sam Ramraj, (626) 302-2540 Media Relations : (626) 302-2255 News@sce.com ​ Edison GAAP earnings per share of $0.99; Core EPS of $1.28 ● Full-year 2023 GAAP EPS of $3.12; Core EPS of $4.76 ● SCE exceeds WMP covered conductor target of 1,100 miles; total deployment of more than 5,580 miles ● EIX introduces 2024 EPS guidance of $4.75-$5.05 ● EIX reiterates long-term core EPS growth rate targets of 5%-7% for 2021-2025 and 5%-7% for 2025-2028 ​ ROSEMEAD, Calif., Feb. 22, 2024 — Edison International (NYSE: EIX) today reported fourth-qua

### Q8 OXY 2018-08-08 → label A: ICE 2020-02-06  (Financials)
- encoders: **concat_eq_plus**  | mean=1.75
- same_dynamic=1  same_regime=2  same_surprise=3  mental_precedent=1
- notes: _Energy vs Financials, totally different business dynamics_
- summary: Intercontinental Exchange reported record full-year revenues of $5.2 billion for the 14th consecutive year, driven by expanded risk management solutions across various asset classes and geographies. The company remains optimistic about continued growth and stockholder value creation in 2020 through innovation and operational efficiencies.
- text[:600]: > Intercontinental Exchange Reports Fourth Quarter & Full Year 2019 14th consecutive year of record full-year revenues Ÿ 2019 net revenues of $5.2 billion, +4% y/y Ÿ 2019 GAAP diluted EPS of $3.42 Ÿ 2019 adj. diluted EPS of $3.88, +8% y/y Ÿ 2019 operating margin of 51%; adj. operating margin of 58% Ÿ Over $2 billion returned to stockholders in 2019, +19% y/y Ÿ New $2.4 billion share repurchase program effective January 1, 2020 Jeffrey C. Sprecher , ICE Chairman & Chief Executive Officer , said , “We are pleased to report our 14 th consecutive year of record revenues. Leveraging our leading techn

### Q9 CPB 2021-09-01 → label E: SYY 2020-02-03  (Consumer Staples)
- encoders: **concat_eq_plus**  | mean=1.75
- same_dynamic=1  same_regime=3  same_surprise=2  mental_precedent=1
- notes: _CPB post-COVID normalization; SYY pre-COVID growth_
- summary: Sysco Corporation reported second-quarter fiscal 2020 results showing modest growth in sales and earnings, driven by improved local case growth in its U.S. Foodservice segment. The company remains confident in executing strategic initiatives to enhance long-term performance despite operating income falling short of expectations.
- text[:600]: > SYSCO REPORTS SECOND QUARTER FISCAL 2020 RESULTS The Company reaffirms its FY18-FY20 adjusted earnings per share guidance HOUSTON, February 3, 2020 - Sysco Corporation (NYSE: SYY) today announced financial results for its 13-week second fiscal quarter ended December 28, 2019. Second Quarter Fiscal 2020 Highlights • Sales increased 1.8% to $15.0 billion • Gross profit increased 2.0% to $2.8 billion; gross margin increased 5 basis points • Operating income increased 22.3% to $552.5 million; adjusted 1 operating income increased 3.9% to $626.9 million • EPS increased $0.23 to $0.74; adjusted 1 EP

### Q10 TAP 2021-04-29 → label B: ESS 2020-01-29  (Real Estate)
- encoders: **random**  | mean=1.75
- same_dynamic=1  same_regime=3  same_surprise=2  mental_precedent=1
- notes: _Different sector, story, news type entirely_
- summary: Essex Property Trust reported strong fourth-quarter and full-year 2019 earnings with same-property NOI growth at the high-end of guidance, driven by steady job growth in tech hubs like Northern California and Seattle. The company expressed optimism about continued stable operating fundamentals and consistent rent growth in 2020.
- text[:600]: > Essex Announces Fourth Quarter and Full-Year 2019 Results and 2020 Guidance San Mateo, California —January 29, 2020 —Essex Property Trust, Inc. (NYSE:ESS) announced today its fourth quarter and full-year 2019 earnings results and related business activities. Net Income and Funds from Operations (“FFO”) per diluted share for the quarter ended and year ended December 31, 2019 are detailed below. Three Months Ended December 31, % Year Ended December 31, % Per Diluted Share 2019 2018 Change 2019 2018 Change Net Income $1.95 $1.78 9.6% $6.66 $5.90 12.9% Total FFO $3.54 $3.02 17.2% $13.73 $12.76 7.6

### Q10 TAP 2021-04-29 → label F: LYB 2021-10-29  (Materials)
- encoders: **concat_eq**  | mean=1.75
- same_dynamic=1  same_regime=3  same_surprise=2  mental_precedent=1
- notes: _Different sector, opposite results, unrelated dynamics_
- summary: LyondellBasell reported robust third-quarter earnings with a net income of $1.8 billion, driven by strong demand and tight market conditions that supported high margins across most businesses. CEO Bob Patel expressed confidence in the company's growth strategy, emphasizing ongoing investments in sustainability goals and debt reduction while expecting continued strong demand from improving economic activity worldwide.
- text[:600]: > Document NEWS RELEASE FOR IMMEDIATE RELEASE HOUSTON and LONDON, October 29, 2021 LyondellBasell Reports Third Quarter 2021 Earnings Third Quarter 2021 Highlights • Robust demand and tight market conditions supported strong margins • Accelerated our climate goals: 30% CO 2 reduction by 2030 and net zero by 2050 (scope 1 and 2) • Net Income: $1.8 billion • Diluted earnings per share: $5.25 per share • EBITDA: $2.7 billion • Record cash from operating activities: $2.1 billion • Strong cash flow supported debt reduction of $0.7 billion with $2.4 billion year-to-date • Paid dividends and repurchase

### Q10 TAP 2021-04-29 → label H: COP 2021-08-03  (Energy)
- encoders: **concat_eq**  | mean=1.75
- same_dynamic=1  same_regime=3  same_surprise=2  mental_precedent=1
- notes: _Different sector, drivers, news type entirely_
- summary: ConocoPhillips delivered strong second-quarter 2021 financial results with earnings of $2.1 billion, driven by higher realized prices and volumes following the company's recent 10-year market update that reaffirmed its commitment to the energy transition while maintaining sector-leading returns on capital. The CEO expressed confidence in the company’s multi-year plan and resilience, emphasizing its unique position to deliver through industry price cycles.
- text[:600]: > ConocoPhillips Delivers Strong Second-Quarter 2021 Financial and Operational Results Following Recent 10-Year Market Update Reported earnings of $2.1 billion; adjusted earnings of $1.7 billion. Generated cash provided by operating activities of $4.3 billion; cash from operations of $4.0 billion. Produced 1,547 MBOED excluding Libya. HOUSTON--(BUSINESS WIRE)--August 3, 2021--ConocoPhillips (NYSE: COP) today reported second-quarter 2021 earnings of $2.1 billion, or $1.55 per share, compared with second-quarter 2020 earnings of $0.3 billion, or $0.24 per share. Excluding special items, second-qua

### Q10 TAP 2021-04-29 → label I: DVN 2021-02-17  (Energy)
- encoders: **concat_eq_plus**  | mean=1.75
- same_dynamic=1  same_regime=2  same_surprise=3  mental_precedent=1
- notes: _Different sector, story, headwinds vs strength_
- summary: Devon Energy Corporation reported strong financial and operational results for the fourth quarter and full year 2020, highlighting industry-first variable dividends and improved well productivity, particularly in the Delaware Basin. The company's CEO expressed confidence in its portfolio and strategy, emphasizing disciplined capital spending and a focus on free cash flow generation despite market uncertainties.
- text[:600]: > Devon Energy Corporation 333 West Sheridan Avenue Oklahoma City, OK 73102-5015 Devon Energy Reports Fourth-Quarter and Full-Year 2020 Financial and Operational Results OKLAHOMA CITY – Feb. 16, 2021 – Devon Energy Corp. (NYSE: DVN) today reported financial and operational results for the fourth quarter and full year 2020. On Jan. 7, 2021, Devon closed its merger with WPX Energy. Results discussed within this release represent legacy Devon operations and do not include amounts related to WPX unless specified. Supplemental financial tables, pro forma information combining certain Devon and WPX re

### Q11 URI 2021-04-28 → label H: GL 2024-10-23  (Financials)
- encoders: **random**  | mean=1.75
- same_dynamic=1  same_regime=2  same_surprise=3  mental_precedent=1
- notes: _Industrials rental vs financials insurance, unrelated_
- summary: Globe Life Inc. reported its third-quarter 2024 financial results on October 23, 2024, showing strong performance driven by robust underwriting margins and investment income growth. The press release maintains a confident tone, highlighting the company's resilience and positive outlook for future quarters.
- text[:600]: > Item 2.02 Results of Operations and Financial Condition. On October 23, 2024 , Globe Life Inc. issued a press release announcing its third quarter 2024 financial results. A copy of the press release is incorporated herein by reference and is provided as Exhibit 99.1. In accordance with General Instruction B.2 of Form 8-K, the information included or incorporated in this report (including Exhibit 99.1) shall not be deemed “filed” for purposes of Section 18 of the Securities Exchange Act of 1934 (the “Exchange Act”), nor shall such information be deemed incorporated by reference in any filing un

### Q13 MMM 2019-04-25 → label E: DLTR 2019-11-26  (Consumer Staples)
- encoders: **concat_eq_plus**  | mean=1.75
- same_dynamic=1  same_regime=3  same_surprise=2  mental_precedent=1
- notes: _Industrials miss vs staples modest beat_
- summary: Dollar Tree, Inc. reported a 3.7% increase in Q3-19 consolidated net sales and achieved same-store sales growth of 2.5%, driven by successful store optimization efforts and initiatives across both Dollar Tree and Family Dollar segments. The company remains optimistic despite facing challenges such as the global helium shortage and increased tariffs, projecting fourth-quarter earnings per share to be in the range of $1.70 to $1.80 due to anticipated tariff impacts.
- text[:600]: > Q3-19 EARNINGS PRESS RELEASE Exhibit Exhibit 99.1 DOLLAR TREE, INC. REPORTS RESULTS FOR THE THIRD QUARTER FISCAL 2019 ~ Consolidated Net Sales Increased 3.7% to $5.75 Billion ~ ~ Earnings per Diluted Share of $1.08 vs. Guidance Range of $1.07 to $1.16 ~ ~ Enterprise Same-Store Sales Increased 2.5% ~ ~ Same-Store Sales by Segment: Dollar Tree +2.8%, Family Dollar +2.3% ~ ~ Planning for 1,000+ Fiscal 2020 Family Dollar H2 Renovation Projects ~ CHESAPEAKE, Va. - November 26, 2019 - Dollar Tree, Inc. (NASDAQ: DLTR), North America's leading operator of discount variety stores, today reported financ

### Q14 EMR 2023-08-02 → label E: EXPD 2023-08-08  (Industrials)
- encoders: **concat_eq_plus, concat_eq**  | mean=1.75
- same_dynamic=1  same_regime=4  same_surprise=1  mental_precedent=1
- notes: _EMR beat+raise vs EXPD miss+cut_
- summary: Expeditors International reported a significant decline in second-quarter 2023 earnings, with EPS down 43% due to reduced freight volumes and pricing pressures as the market resets post-pandemic disruptions. The company remains cautious about near-term prospects, citing uncertain demand and excess capacity in both air and ocean freight markets.
- text[:600]: > EARNINGS RELEASE By: Expeditors International of Washington, Inc. 1015 Third Avenue Seattle, Washington 98104 CONTACTS : Jeffrey S. Musser Bradley S. Powell Geoffrey Buscher President and Chief Executive Officer Senior Vice President and Chief Financial Officer Director - Investor Relations (206) 674-3433 (206) 674-3412 (206) 892-4510 FOR IMMEDIATE RELEASE EXPEDITORS REPORTS SECOND QUARTER 2023 EPS OF $1.30 SEATTLE, WASHINGTON - August 8, 2023, Expeditors International of Washington, Inc. (NASDAQ:EXPD) today announced second quarter 2023 financial results including the following comparisons to

### Q1 COHR 2020-08-13 → label D: AMT 2020-07-30  (Real Estate)
- encoders: **concat_eq_plus**  | mean=2.00
- same_dynamic=1  same_regime=3  same_surprise=3  mental_precedent=1
- notes: _Different sectors, different stories entirely_
- summary: The company reported strong second-quarter earnings, driven by robust sales growth and cost-cutting measures. The press release maintains a confident tone, highlighting significant improvements in key financial metrics.
- text[:600]: > A copy of the Press Release is furnished herewith as Exhibit 99.1. Exhibit 99.1 is furnished and shall not be deemed to be “filed” for purposes of Section 18 of the Securities Exchange Act of 1934, as amended (the “Exchange Act”), or otherwise subject to the liabilities of that section, nor shall such exhibit be deemed incorporated by reference in any filing made by the Company under the Securities Act of 1933, as amended, or the Exchange Act, except as expressly set forth by specific reference in such a filing.

### Q4 ALGN 2019-04-24 → label H: LIN 2020-05-07  (Materials)
- encoders: **random**  | mean=2.00
- same_dynamic=2  same_regime=1  same_surprise=3  mental_precedent=2
- notes: _Different sector, COVID macro, unrelated drivers_
- summary: Linde reported strong first-quarter 2020 financial results, including a 26% increase in operating cash flow and robust balance sheet liquidity, driven by improved pricing and operational efficiency despite a 1% decrease in sales due to the COVID-19 pandemic. CEO Steve Angel expressed confidence in the company's ability to create shareholder value through its resilient business model and opportunities to mitigate economic challenges.
- text[:600]: > lin_ex991 Exhibit 99.1 Press Release Linde Reports First-Quarter 2020 Results Financial Highlights ➢ Strong operating cash flow of $1.3 billion, up 26% versus prior year ➢ Robust balance sheet with ample liquidity for growth opportunities ➢ Operating profit of $0.7 billion, up 20% versus prior year; adjusted operating profit of $1.4 billion up 11% ➢ Operating profit margin up 210 bps, adjusted operating profit margin up 240 bps versus prior year ➢ EPS of $1.07 up 35% versus prior year, adjusted EPS of $1.89 up 12% Guildford, UK, May 7, 2020 – Linde plc (NYSE: LIN; FWB: LIN) today reported firs

### Q7 NUE 2023-04-20 → label A: DASH 2023-05-04  (Consumer Discretionary)
- encoders: **concat_eq_plus**  | mean=2.00
- same_dynamic=1  same_regime=3  same_surprise=3  mental_precedent=1
- notes: _Steel vs food delivery, no structural overlap_
- summary: DoorDash reported strong first-quarter 2023 financial results, driven by robust growth in U.S. and international markets, improved operational efficiency, and disciplined expense management, leading to a 40% year-over-year increase in revenue and a 12.8% net revenue margin. The company remains optimistic about its future prospects, aiming for continued growth and efficient operations as it executes on strategic goals.
- text[:600]: > Document Exhibit 99.1 DoorDash Releases First Quarter 2023 Financial Results May 4, 2023 SAN FRANCISCO--(BUSINESS WIRE)-- DoorDash Inc. (NYSE: DASH) today announced its financial results for the quarter ended March 31, 2023. In addition to our financial results below, our letter to shareholders is available on the DoorDash investor relations website at http://ir.doordash.com. DoorDash continued to execute extremely well in Q1 2023 and we are proud of our team's outstanding performance in service of our stakeholders. In Q1 2023, our focus on inputs and deep attention to detail drove strong and 

### Q7 NUE 2023-04-20 → label I: TTD 2018-11-08  (Communication Services)
- encoders: **concat_eq**  | mean=2.00
- same_dynamic=1  same_regime=3  same_surprise=3  mental_precedent=1
- notes: _Steel vs adtech, no structural overlap_
- summary: The Trade Desk reported strong third-quarter financial results with a 50% year-over-year increase in revenue to $118.8 million, driven by growth across mobile, connected TV, audio, and video channels, as well as new customer wins and international expansion. The CEO expressed optimism about the company's momentum and revised its full-year 2018 outlook with higher revenue targets, reflecting continued success in winning major advertiser clients.
- text[:600]: > The Trade Desk Reports Third Quarter Financial Results LOS ANGELES--(BUSINESS WIRE)--November 8, 2018--The Trade Desk, Inc. (NASDAQ: TTD), a provider of a global technology platform for buyers of advertising, today announced financial results for its third quarter ended September 30, 2018. “As the worldwide programmatic advertising market grows, we continue to outpace that growth. The need for objective, data-driven media buying is increasing. A steady stream of new brands and agencies continues to join our platform. The market continues to validate our business model and we’re seeing the meas

### Q10 TAP 2021-04-29 → label A: SNA 2024-02-08  (Industrials)
- encoders: **random**  | mean=2.00
- same_dynamic=2  same_regime=1  same_surprise=3  mental_precedent=2
- notes: _Different sector, regime; both resilient beat narratives_
- summary: Snap-on reported strong fourth-quarter and full-year 2023 results with a 7.5% gain in diluted EPS to $4.75, driven by organic sales growth of 2.2% and improved operating margins. The company remains optimistic about its future prospects despite market turbulence, attributing its success to the resilience of its markets and the capabilities of its teams.
- text[:600]: > Snap-on Announces Fourth Quarter and Full Year 2023 Results Diluted EPS of $4.75 for the quarter represents a gain of 7.5% from Q4 2022; Sales of $1,196.6 million up 3.5% from Q4 2022, organic sales up 2.2%; Operating margin before financial services of 21.6% compares to 21.5% in Q4 2022 KENOSHA, Wis.--(BUSINESS WIRE)--February 8, 2024--Snap-on Incorporated (NYSE: SNA), a leading global innovator, manufacturer and marketer of tools, equipment, diagnostics, repair information and systems solutions for professional users performing critical tasks, today announced 2023 operating results for the f

### Q11 URI 2021-04-28 → label D: FCX 2022-10-20  (Materials)
- encoders: **random**  | mean=2.00
- same_dynamic=2  same_regime=1  same_surprise=3  mental_precedent=2
- notes: _Different sectors, macro regime very different_
- summary: Freeport-McMoRan reported strong third-quarter and year-to-date 2022 results, with copper and gold sales volumes above guidance due to robust production performance; however, unit net cash costs were slightly higher than expected. The company remains optimistic about its long-term market fundamentals and is confident in its strategy despite near-term uncertainties, as evidenced by significant debt retirements and a solid balance sheet.
- text[:600]: > Document Freeport-McMoRan Reports Third-Quarter and Nine-Month 2022 Results • Strong production performance; copper and gold sales volumes above July 2022 guidance • Unit net cash costs were 5% above July 2022 guidance • Solid balance sheet, liquidity and financial flexibility • Significant debt retirements through open-market transactions • Published updated climate report ▪ Net income attributable to common stock in third-quarter 2022 totaled $404 million, $0.28 per share, and adjusted net income attributable to common stock totaled $375 million, $0.26 per share, after excluding net credits 

### Q12 NDSN 2020-05-20 → label G: TSCO 2020-04-23  (Consumer Discretionary)
- encoders: **concat_eq**  | mean=2.00
- same_dynamic=2  same_regime=2  same_surprise=2  mental_precedent=2
- notes: _TSCO beat+accelerate vs NDSN mild miss_
- summary: Tractor Supply Company reported solid first-quarter 2020 financial results, with net sales increasing by 7.5% and diluted earnings per share up 12.7%, driven by strength in consumable and seasonal product categories despite softness in discretionary items; the company remains confident in its business model and is prioritizing investments in safety and convenience while adapting to changing customer needs amid the COVID-19 pandemic.
- text[:600]: > - PRESS RELEASE DATED APRIL 23, 2020 Document www.TractorSupply.com TRACTOR SUPPLY COMPANY REPORTS FIRST QUARTER 2020 FINANCIAL RESULTS • Net Sales Increased 7.5%; Comparable Store Sales Increased 4.3% • Diluted Earnings Per Share Increased 12.7% to $0.71 • Actions Taken to Prioritize Investments in Safety and Convenience and Improve Liquidity Brentwood, TN, April 23, 2020 - Tractor Supply Company (NASDAQ: TSCO) , the largest rural lifestyle retailer in the United States, today reported financial results for its first quarter ended March 28, 2020. “Our year-to-date results underscore the impor

### Q13 MMM 2019-04-25 → label B: CVX 2020-01-31  (Energy)
- encoders: **concat_eq**  | mean=2.00
- same_dynamic=2  same_regime=2  same_surprise=2  mental_precedent=2
- notes: _Different sector, write-offs vs structural slowdown_
- summary: Chevron reported a fourth-quarter loss of $6.6 billion, primarily due to upstream impairments and write-offs totaling $10.4 billion related to various projects, but still managed to deliver on core financial priorities with strong cash flow from operations and record annual oil-equivalent production. The company remains optimistic about its commitment to capital discipline and superior shareholder returns despite the quarter's challenges.
- text[:600]: > Exhibit news release FOR RELEASE AT 5:30 AM PDT JANUARY 31, 2020 Chevron Announces Fourth Quarter 2019 Results Delivers on core financial priorities, demonstrates commitment to capital discipline and superior shareholder returns • Fourth quarter loss $6.6 billion ; earnings excluding special items and FX $2.8 billion • Annual earnings $2.9 billion ; earnings excluding special items and FX $11.9 billion • Cash flow from operations of $27.3 billion in 2019 • Record annual net oil-equivalent production of 3.06 million barrels per day • Dividends and share repurchases of $13.0 billion in 2019 San 

### Q13 MMM 2019-04-25 → label G: PNR 2018-07-25  (Industrials)
- encoders: **concat_eq**  | mean=2.00
- same_dynamic=2  same_regime=3  same_surprise=2  mental_precedent=1
- notes: _PNR positive, MMM miss+restructure_
- summary: Pentair plc announced its earnings for the second quarter of 2018, highlighting core sales growth and adjusted financial metrics that exclude certain non-operational factors; the press release is cautiously optimistic about underlying operational strength while acknowledging the complexity in comparing these non-GAAP measures to those of other companies.
- text[:600]: > ITEM 2.02 Results of Operations and Financial Condition On July 25, 2018 , Pentair plc (the “Company”) issued a press release announcing its earnings for the second quarter of 2018 and a conference call in connection therewith. A copy of the release is attached hereto as Exhibit 99.1 and incorporated herein by reference. This press release refers to certain non-GAAP financial measures (core sales, segment income, return on sales, adjusted net income from continuing operations, adjusted diluted earnings per share from continuing operations and free cash flow) and a reconciliation of those non-G

## Top Performers (mean of 4 metrics ≥ 4.0)  —  1 candidates

### Q15 URI 2020-04-29 → label B: CAT 2020-04-28  (Industrials)
- encoders: **concat_eq_plus**  | mean=4.25
- same_dynamic=4  same_regime=5  same_surprise=4  mental_precedent=4
- notes: _Both industrials, COVID Q1, guidance withdrawn_
- summary: Caterpillar Inc. reported a 21% decrease in first-quarter 2020 sales and revenues due to lower end-user demand and changes in dealer inventories, resulting in a 39% decline in profit per share. Despite the challenges posed by the COVID-19 pandemic, the company remains optimistic about emerging stronger and is taking actions to enhance its financial position while continuing its strategy for profitable growth.

## Encoder share among Hard Failures / Top Performers

| encoder | hard count | top count |
|---|---|---|
| concat_eq_plus | 15 | 1 |
| concat_eq | 13 | 0 |
| contrastive_v2 | 0 | 0 |
| random | 33 | 0 |
