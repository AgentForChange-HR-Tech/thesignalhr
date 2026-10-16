# Three regional insight articles (October 16, 2026). Body HTML is the prose only; build_articles.py wraps it.
ARTICLES = [
dict(
 slug="americas-ai-hiring-notice-2027",
 region="americas",
 tag=("Regulation", "tag-coral"),
 title="The January 1, 2027 cliff: one AI-hiring notice for a patchwork that didn't go away",
 h1='The January 1, 2027 cliff: one AI-hiring notice for a patchwork that <em>didn\'t go away</em>',
 crumb="The January 1, 2027 AI-hiring cliff",
 seo_title="AI Hiring Laws in the Americas: The January 1, 2027 Deadline — The Signal HR",
 desc="Colorado and California's AI-in-hiring rules start January 1, 2027, joining New York City, Illinois and Ontario. Federal preemption hasn't displaced them. The rules converge on notice, explanation, human review and records: build one standard.",
 standfirst="Washington has moved to preempt state AI laws and has stepped back from disparate-impact enforcement. The states kept going. By January the rules converge on four things: tell people, explain adverse outcomes, offer a human, and keep the records.",
 minutes=4,
 body='''
    <p>On <strong>January 1, 2027</strong>, two of the most closely watched AI-in-hiring regimes in the United States start at once. Colorado's rewritten AI law, SB 26-189, requires notice before AI "materially influences" a hiring decision, a plain-language explanation within 30 days of an adverse outcome, and meaningful human review. California's privacy agency starts enforcing its rules on automated decision-making technology: a pre-use notice, an opt-out or human-appeal route, and a written risk assessment before the tool is used.</p>
    <p>They join rules already in force: New York City's bias-audit law, Illinois's requirement to tell people when AI is used in employment decisions, and Ontario's requirement to say in every public job posting whether AI screens, assesses or selects applicants. Connecticut's notice duties follow on October 1, 2027.</p>
    <p>If your AI-hiring compliance plan is "wait for Washington to sort it out," this is the quarter to change it.</p>
    <h2>What Washington did, and didn't do</h2>
    <p>Federal policy has moved in the opposite direction from the states. Executive Order 14365 (December 11, 2025) called for a national AI framework that preempts conflicting state laws, and the Justice Department set up an AI Litigation Task Force in January 2026. Its first visible move was joining xAI's challenge to Colorado's original AI Act, which led to a stipulated stay of enforcement on April 27, 2026. Separately, the EEOC's June 2026 enforcement plan stops disparate-impact investigations, the main federal theory used against biased selection tools.</p>
    <p>Here is what that doesn't change. No state employment AI law has been displaced. Private plaintiffs can still bring Title VII disparate-impact claims. New Jersey codified disparate-impact rules that expressly cover automated decision tools in December 2025. California's civil-rights regulations, in force since October 1, 2025, make the quality of your bias testing evidence in a discrimination claim and require four years of records, including the tool's inputs and outputs. And in New York City, the State Comptroller's December 2025 audit found the enforcement agency had flagged one issue where auditors found seventeen. The agency agreed to tighten up.</p>
    <blockquote>Federal retreat moved the risk. It didn't remove it.</blockquote>
    <h2>Where the rules converge</h2>
    <p>Read side by side, the patchwork has a common core:</p>
    <ul>
      <li><strong>Notice before use.</strong> New York City (ten business days before use), Illinois (statute in force; implementing rules pending), Colorado (before the tool materially influences a decision), California's privacy rules (a pre-use notice) and Ontario (in the posting itself). Connecticut adds written pre-decision notices from October 2027.</li>
      <li><strong>An explanation or appeal route.</strong> Colorado requires an explanation within 30 days of an adverse outcome. California gives candidates a right to information about the tool's logic and how its output was used, and an opt-out unless a qualified human appeal is offered or a narrow hiring exception applies. Quebec requires notice and a route to a human reviewer when a decision is fully automated.</li>
      <li><strong>A human with real authority.</strong> Colorado expects meaningful human review where commercially reasonable. California's appeal exception only works if the reviewer understands the output and can change the decision. California's SB 947 extends the idea to discipline and termination from July 1, 2027.</li>
      <li><strong>Bias testing.</strong> Mandatory and published only in New York City. Everywhere else it is your evidence: California weighs its quality, Connecticut lets courts consider it, and Texas treats it as part of an affirmative defense.</li>
      <li><strong>Records.</strong> Three years in Colorado and Ontario, four years under California's civil-rights rules.</li>
    </ul>
    <h2>Build one standard, not twelve</h2>
    <p>The practical answer for a multinational is a single Americas standard built to the highest common denominator, then switched on everywhere:</p>
    <ol>
      <li><strong>Inventory every tool that scores, ranks, filters or talks to candidates.</strong> Include AI features that arrived quietly inside your ATS, scheduling tool or career-site chatbot; those are the ones most often missed.</li>
      <li><strong>Write one notice.</strong> What the tool does, what data it uses, how its output feeds the decision, how to ask for an alternative or an accommodation, and a human contact. Put it in job postings (Ontario requires it there, and Illinois's draft rules pointed the same way) and on your careers site.</li>
      <li><strong>Design the adverse-outcome path.</strong> A plain-language explanation within 30 days and a named reviewer who can change the decision. Log how often reviewers actually overturn the tool; zero is not oversight.</li>
      <li><strong>Test for bias on a schedule.</strong> Annually at minimum, after every model or criteria change, and before expanding to a new population. Keep four years of inputs, outputs and test results.</li>
      <li><strong>Put it in the vendor contract.</strong> Audit support, the information you need for notices (Connecticut requires developers to provide it), data retention, and notice of model changes.</li>
    </ol>
    <p>Then treat each new law as a configuration change: a new jurisdiction in the notice, a new retention period, a new review route. That's a far cheaper posture than starting a project every time a legislature adjourns.</p>
    <p>The patchwork didn't go away. It converged. Build to the common core once, before January 1.</p>
''',
 sources=[
  ("Epstein Becker Green — Inside Colorado's SB 26-189", "https://www.ebglaw.com/workforce-bulletin/inside-colorados-senate-bill-26-189-impacts-and-implications-for-employers"),
  ("Proskauer — Major developments put Colorado's AI law on ice", "https://www.proskauer.com/blog/major-developments-put-colorados-ai-law-on-ice-ahead-of-implementation"),
  ("Bass Berry — The CPPA's regulations on automated decision-making", "https://bassberry.com/news/ccpa-sept-2025-update/"),
  ("Mayer Brown — California's employment AI regulations, effective October 1, 2025", "https://www.mayerbrown.com/en/insights/publications/2025/08/california-adopts-new-employment-ai-regulations-effective-october-1-2025"),
  ("Proskauer — What Executive Order 14365 means for employers", "https://www.proskauer.com/blog/what-president-trumps-ai-executive-order-14365-means-for-employers"),
  ("Epstein Becker Green — The death of disparate impact?", "https://www.ebglaw.com/workforce-bulletin/the-death-of-disparate-impact-what-recent-doj-guidance-signals-to-employers"),
  ("Morgan Lewis — New Jersey codifies disparate impact rules", "https://www.morganlewis.com/pubs/2025/12/new-jersey-codifies-existing-disparate-impact-rules"),
  ("DLA Piper — Critical audit of NYC's AI hiring law", "https://www.dlapiper.com/en/insights/publications/2026/01/critical-audit-of-nyc-ai-hiring-law-signals-increased-risk-for-employers"),
  ("Osler — Ontario's AI job-posting disclosure", "https://www.osler.com/en/insights/blogs/employment-and-labour-law-blog/ai-in-hiring-ontario-employers-grappling-with-new-job-posting-disclosure-requirement/"),
  ("Ropes & Gray — Connecticut's CART Act", "https://www.ropesgray.com/en/insights/alerts/2026/06/connecticut-enacts-sweeping-ai-law-covering-employment-healthcare-and-online-safety"),
  ("Sheppard Mullin — Texas TRAIGA employer takeaways", "https://www.sheppard.com/insights/blogs/texas-joins-the-ai-regulation-wave-key-employer-takeaways-from-the-texas-responsible-artificial-intelligence-governance-act"),
 ]),
dict(
 slug="eu-pay-transparency-2026-payroll",
 region="emea",
 tag=("Pay", "tag-amber"),
 title="Your 2026 payroll is already your first EU pay-gap report",
 h1='Your 2026 payroll is already your first <em>EU pay-gap report</em>',
 crumb="Your 2026 payroll is your first EU pay-gap report",
 seo_title="EU Pay Transparency Directive: Why 2026 Payroll Is Your First Report — The Signal HR",
 desc="Most EU countries missed the June 7, 2026 deadline to transpose the Pay Transparency Directive, and Brussels refused to delay it. First pay-gap reports, due June 7, 2027, cover 2026 pay. What HR should do this quarter.",
 standfirst="Most EU countries missed the June 7 deadline to transpose the Pay Transparency Directive, and Brussels has refused to delay it. The first reports, due June 7, 2027, cover calendar-year 2026, which ends in eleven weeks.",
 minutes=4,
 body='''
    <p>The EU Pay Transparency Directive (2023/970) had to be written into national law by <strong>June 7, 2026</strong>. Only four member states made it on time: Italy, Malta, Slovakia and Lithuania. Greece followed, with its main provisions taking effect on November 1. Most of the rest have draft bills, partial measures or nothing published yet. On May 22, 2026, the Commission said it "does not envisage" including the directive in any simplification or "stop-the-clock" package.</p>
    <p>That combination has led many multinationals to conclude they have time. They have less than they think.</p>
    <h2>Why "not transposed yet" doesn't mean "not yet"</h2>
    <p>The directive's reporting dates are fixed in the directive itself. Employers with <strong>250 or more workers</strong> report every year, and those with <strong>150 to 249</strong> report every three years, with the first reports for both due by <strong>June 7, 2027</strong>. Employers with 100 to 149 workers start on June 7, 2031. Each report covers the previous calendar year.</p>
    <p>So the data for your first report is the payroll you are running right now. When Germany, France or the Netherlands finally pass their laws, they will ask about 2026. Some countries already add earlier steps: Slovakia required compliant pay structures by July 31, 2026, and Lithuania requires a documented pay system by December 31, 2026.</p>
    <blockquote>The reporting year started on January 1. The national laws are catching up to it.</blockquote>
    <h2>The 5% trigger</h2>
    <p>The part that worries reward teams most is Article 10. If your report shows a gender pay gap of <strong>5% or more in any category of workers</strong>, you can't justify it with objective, gender-neutral criteria, and you don't fix it within six months, you must run a <strong>joint pay assessment</strong> with workers' representatives. "Category of workers" means people doing the same work or work of equal value, which is a job-architecture question before it is a pay question. If your job levels don't map cleanly to comparable work, you can't defend a gap you can't define.</p>
    <h2>What already applies at hiring</h2>
    <p>Where the directive is in force, and soon everywhere in the EU, the candidate-facing rules change your recruiting process:</p>
    <ul>
      <li>Tell candidates the starting pay or pay range before the interview, or in the job ad.</li>
      <li>Stop asking about current or past pay.</li>
      <li>Use gender-neutral job titles and vacancy notices.</li>
      <li>Make the criteria for pay and pay progression accessible to employees (countries may exempt employers under 50 from the progression rule).</li>
      <li>Answer an employee's request for pay information within two months, and remind everyone of that right every year.</li>
    </ul>
    <h2>Where the big countries stand</h2>
    <p>Trackers maintained by law firms and reward vendors differ in the details, but the picture in mid-October is consistent. Germany has not published a draft, and reporting there may not start until 2028. France's bill is in the Senate, with a vote expected before spring 2027. The Netherlands has scheduled its plenary debate for January 11, 2027, so its January 1 target will slip. Denmark's bill would take effect March 1, 2027, and Finland targets January 1, 2027. Ireland has not prioritized its bill, and Sweden has asked for more time. None of that moves the directive's reporting dates.</p>
    <h2>The plan for Q4 2026 to Q1 2027</h2>
    <ol>
      <li><strong>Run a privileged pay-equity audit on 2026 data</strong>, country by country and by category of comparable work. Do it with counsel so findings you can't yet explain stay protected while you fix them.</li>
      <li><strong>Repair the job architecture.</strong> Define categories by skills, effort, responsibility and working conditions. This is the foundation of every other step.</li>
      <li><strong>Fix the hiring pipeline EU-wide.</strong> Pay ranges in job ads, salary-history questions removed from ATS forms and recruiter scripts, gender-neutral templates.</li>
      <li><strong>Stand up the pay-information request process</strong> with a two-month service level and an annual reminder to employees.</li>
      <li><strong>Close unexplained gaps of 5% or more before you report them.</strong> A gap fixed before reporting is a budget line; a gap reported and left open is a joint pay assessment.</li>
      <li><strong>Brief works councils early.</strong> They will be your partners in any joint pay assessment.</li>
    </ol>
    <p>The countries that missed the deadline bought themselves time. They didn't buy any for you.</p>
''',
 sources=[
  ("Directive (EU) 2023/970 on pay transparency (EUR-Lex)", "https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32023L0970"),
  ("Trusaic — EU Pay Transparency Directive member state transposition monitor", "https://trusaic.com/resources/eu-pay-transparency-directive-member-state-transposition-monitor/"),
  ("Ius Laboris — Which countries have transposed", "https://iuslaboris.com/insights/eu-pay-transparency-directive-which-countries-have-transposed/"),
  ("Ius Laboris — EU pay transparency: no delay", "https://iuslaboris.com/insights/eu-pay-transparency-no-delay/"),
 ]),
dict(
 slug="apac-automated-hiring-clock",
 region="apac",
 tag=("Regulation", "tag-coral"),
 title="Asia-Pacific's automated-hiring clock: three deadlines in seven months",
 h1='Asia-Pacific\'s automated-hiring clock: three deadlines in <em>seven months</em>',
 crumb="Asia-Pacific's automated-hiring clock",
 seo_title="AI in Hiring Across Asia-Pacific: Australia, Korea, India and China Deadlines — The Signal HR",
 desc="There's no single Asia-Pacific AI law, but Australia (December 10, 2026), South Korea (fines from about January 2027) and India (May 13, 2027) each start a clock on automated hiring decisions, and China's rights already apply. Build one regional standard.",
 standfirst="There's no single Asia-Pacific AI law. But Australia, South Korea and India each start a clock on automated hiring between December 2026 and May 2027, and China's explanation rights already apply. One regional standard beats five country projects.",
 minutes=4,
 body='''
    <p>US and EU rules dominate the conversation about AI in hiring. For multinationals with Asia-Pacific operations, the nearer deadlines are in the region itself:</p>
    <ul>
      <li><strong>Australia, December 10, 2026:</strong> privacy policies must disclose automated decisions that significantly affect people.</li>
      <li><strong>South Korea, from about January 2027:</strong> the AI Basic Act's grace period on fines, which began when the law took effect on January 22, 2026 and runs for at least a year, starts to run out. Hiring AI is classed as "high-impact."</li>
      <li><strong>India, May 13, 2027:</strong> the Digital Personal Data Protection Act's substantive duties apply, including to candidate data.</li>
    </ul>
    <p>And China's Personal Information Protection Law already gives people the right to an explanation of automated decisions with a major effect on them, and to refuse decisions made solely by automation.</p>
    <h2>Australia: disclose the decisions, not just the data</h2>
    <p>From December 10, new Australian Privacy Principles 1.7 to 1.9 require a privacy policy to describe the kinds of personal information used in computer programs that make decisions which could significantly affect someone, the kinds of decisions made solely by a program, and the kinds where a program does something "substantially and directly related" to the decision. The regulator, the OAIC, published guidance on September 30, 2026. The disclosure is by category, not per candidate, and it applies to decisions made after commencement even if the data was collected earlier.</p>
    <p>One question isn't settled: how the employee-records exemption interacts with job applicants. Candidates aren't employees, so the safer reading is that automated screening and assessment scoring are in scope.</p>
    <h2>South Korea: "high-impact" means hiring</h2>
    <p>The AI Basic Act puts AI that significantly affects people's rights, including in hiring, into a high-impact category with duties to explain outcomes and the main criteria behind them, keep human oversight, notify users in advance, and maintain risk-management and user-protection plans. Fines run to KRW 30 million, deferred during a grace period of at least one year.</p>
    <p>Most duties fall on "AI business operators." Whether an employer that uses a vendor's screening tool only for its own hiring counts as one is still unresolved, so get a Korean counsel view. Either way, your vendor almost certainly is one, and its compliance becomes your due-diligence question.</p>
    <h2>India: candidate data needs a notice and a reason</h2>
    <p>India notified its DPDP Rules on November 13, 2025, with consent-manager provisions from November 13, 2026 and the substantive obligations from May 13, 2027: itemized plain-language notices, consent where consent is the basis, security safeguards, breach reporting within 72 hours, data-subject rights, and erasure once the purpose is served (while keeping logs for at least a year). The Act lets employers process data for employment purposes without consent, but it is not clear that covers candidates. Plan for candidate notices and consent flows.</p>
    <h2>China: explanation and refusal rights already apply</h2>
    <p>Under the PIPL, automated decisions must be transparent and fair. People can ask for an explanation and refuse decisions made solely by automation when the effect is major, and a personal-information impact assessment is required before automated decision-making. Separately, since September 1, 2025, AI-generated content distributed online, such as AI-written job ads or avatar recruiter videos, must be labeled.</p>
    <p>Around these, the region is tightening in the same direction. Vietnam's data protection law (in force January 1, 2026) requires impact-assessment filings within 60 days of starting processing. Singapore's Workplace Fairness Act is expected to commence at the end of 2027, and its tripartite guidance already says AI should inform hiring decisions, not make them.</p>
    <blockquote>Five countries, one pattern: tell people, explain the outcome, keep a human who can change it.</blockquote>
    <h2>One regional standard</h2>
    <ol>
      <li><strong>Run one Asia-Pacific inventory</strong> of every tool that screens, scores, ranks, interviews or chats with candidates, by country.</li>
      <li><strong>Update the Australian privacy policy before December 10</strong> with the kinds of information and the kinds of decisions involved.</li>
      <li><strong>Ask vendors for their Korean high-impact self-assessment</strong>, explanation capability and override design, and put them in the contract.</li>
      <li><strong>Build one explanation-plus-human-review step</strong> that satisfies China's right to refuse and Korea's explanation duty, and offer it everywhere.</li>
      <li><strong>Rewrite candidate notices for India</strong> and agree a 72-hour breach workflow with every HR vendor before May 2027.</li>
      <li><strong>Label AI-generated recruiting content</strong> in China, and keep a record of what was generated.</li>
    </ol>
    <p>Asia-Pacific won't hand you one law to comply with. It will hand you a calendar, and the first date is eight weeks away.</p>
''',
 sources=[
  ("OAIC — New resources on transparency for AI and automated decision-making", "https://www.oaic.gov.au/news/media-centre/new-resources-on-transparency-for-use-of-ai-and-automated-decision-making"),
  ("Gilbert + Tobin — Automated decision-making transparency under the Privacy Act", "https://www.gtlaw.com.au/insights/automated-decision-making-transparency-under-the-privacy-act"),
  ("Cooley — South Korea's AI Basic Act: overview and key takeaways", "https://www.cooley.com/news/insight/2026/2026-01-27-south-koreas-ai-basic-act-overview-and-key-takeaways"),
  ("U.S. International Trade Administration — South Korea AI Basic Act", "https://www.trade.gov/market-intelligence/south-korea-ai-basic-act"),
  ("S.S. Rana & Co. — MeitY notifies final DPDP Rules 2025", "https://ssrana.in/articles/meity-notifies-final-digital-personal-data-protection-rules-2025/"),
  ("DigiChina — Translation: Personal Information Protection Law of the PRC", "https://digichina.stanford.edu/work/translation-personal-information-protection-law-of-the-peoples-republic-of-china-effective-nov-1-2021/"),
  ("Covington — China's labeling requirements for AI-generated content", "https://www.covingtonblogs.com/2025/03/18/china-releases-new-labeling-requirements-for-ai-generated-content/"),
  ("Rajah & Tann Asia — Vietnam's decree implementing the Personal Data Protection Law", "https://www.rajahtannasia.com/viewpoints/new-decree-implementing-the-law-on-personal-data-protection-passed/"),
  ("TAFEP — Fair hiring first, AI second", "https://www.tal.sg/tafep/resources/articles/2025/fair-hiring-first-ai-second"),
 ]),
]
