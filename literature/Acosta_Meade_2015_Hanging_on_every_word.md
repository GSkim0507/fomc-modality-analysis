# Hanging on every word: Semantic analysis of the FOMC's postmeeting statement

**Authors:** Miguel Acosta and Ellen E. Meade  
**Venue:** FEDS Notes, Board of Governors of the Federal Reserve System, September 30, 2015  
**DOI:** https://doi.org/10.17016/2380-7172.1580  
**Source URL:** https://www.federalreserve.gov/econresdata/notes/feds-notes/2015/semantic-analysis-of-the-FOMCs-postmeeting-statement-20150930.html  
**Note:** FEDS Notes are published as HTML only (no PDF). Text below was extracted from the HTML page with pandoc on 2026-08-28; charts are not included.

---

### Hanging on every word: Semantic analysis of the FOMC's postmeeting statement

Miguel Acosta and [Ellen Meade](/econresdata/ellen-meade.htm) [<sup>1</sup>](#fn1 "footnote 1")<span id="f1"></span>



**Introduction**
The Federal Open Market Committee's (FOMC or "Committee") postmeeting statements constitute one of the key vehicles through which the Committee communicates its assessment of the economy, its policy actions, and its thinking about future policy. In this note, we use techniques developed in natural language processing (NLP, also referred to as computational linguistics) to study how the content of the FOMC's postmeeting statement has changed from May 1999--when the Committee began releasing statements consistently--through December 2014. We show that, to the untutored reader, the statements appear to be highly similar from one FOMC meeting to the next. Indeed, the semantic persistence of the statements has risen notably in recent years relative to the early years of our sample period. Importantly, we find that, after using some tools commonly employed in computational linguistics to prepare the text, the semantic persistence of FOMC statements from one meeting to the next is revealed to be much lower than casual reading would suggest and is also more variable. We see this as evidence of a greater information content present in the postmeeting statement than might be apparent at a first glance. We highlight the December 2008 statement--an historically significant statement because of the policy actions taken at that FOMC meeting--to illustrate the more general point that NLP techniques offer a new lens through which to view the Federal Reserve's communications. Our analysis shows that natural language processing can strip away false impressions and uncover hidden truths about complex communications such as those of the Federal Reserve.

**Background on the FOMC statement**
More than two decades ago, in February 1994, Chairman Greenspan issued the first postmeeting statement following the FOMC's decision to tighten monetary policy--the first increase in the target for the federal funds rate since 1989. For the next five years, a statement was released only after FOMC meetings at which the Committee changed its target for the federal funds rate. In May 1999, the FOMC began releasing statements at the conclusion of every meeting regardless of whether it had decided to make a change to the policy interest rate or not. Later, in May 2002, the FOMC decided to provide voting information in the postmeeting statements, including a short explanation of any dissenting votes, thereby accelerating the provision of this information to the public by several weeks.[<sup>2</sup>](#fn2 "footnote 2")<span id="f2"></span>

The FOMC's statements have become substantially longer and more informative over time. The first statement issued in February 1994 was a mere 99 words in 4 sentences, compared with 564 words in 22 sentences in December 2014.[<sup>3</sup>](#fn3 "footnote 3") <span id="f3"></span> Chart 1 provides the word count for FOMC statements since May 1999. Hernández-Murillo and Shell (2014)[<sup>4</sup>](#fn4 "footnote 4") <span id="f4"></span> analyze the linguistic complexity of the FOMC statement using the well-known Flesch-Kincaid Grade Level index, which measures the reading grade level of a particular text. They find that, while the early statements are written at a reading grade level of 9 to 14 years of schooling, the more recent statements are written at a reading grade level of three years beyond a 4-year college degree.


<span id="figure1"></span>

|  |
|----|
| **Chart 1. FOMC statements, word count by meeting** |
| *<img src="/econresdata/notes/feds-notes/2015/gifjpg/meade-acosta-chart1-20150925.png" width="378" height="398" alt="Chart 1. FOMC statements, word count by meeting. See accessible link for data." />* |


Note: Excludes voting information

[Accessible version](semantic-analysis-of-the-FOMCs-postmeeting-statement-accessible-20150930.html#fig1)



Early statements included a brief economic rationale for the change in monetary policy; more recent statements include an assessment of current economic conditions and a discussion of the economic outlook, as well as the rationale for current monetary policy and forward guidance about the evolution of policy in the future. Chart 2 provides some word-count-based evidence about the references to specific topics in the statements over time. For example, the weather and global developments have been mentioned in the statement relatively infrequently; movements in energy or other commodity prices have received greater attention, as has growth in productivity, which figured frequently in statements prior to mid-2006. In contrast, references to inflation expectations have become more frequent since the financial crisis with at least one reference in each statement since September 2009.[<sup>5</sup>](#fn5 "footnote 5")<span id="f5"></span>


<span id="figure2"></span>

|  |
|----|
| **Chart 2. Selected word counts from FOMC statements** |
| *<img src="/econresdata/notes/feds-notes/2015/gifjpg/meade-acosta-chart2-20150925.png" width="608" height="783" alt="Chart 2. Selected word counts from FOMC statements. See accessible link for data." />* |


[Accessible version](semantic-analysis-of-the-FOMCs-postmeeting-statement-accessible-20150930.html#fig2)



**Measuring semantic similarity**
Recently, economists have begun to use techniques from the computational linguistics literature that have been employed extensively in political science and other disciplines to examine complex texts.[<sup>6</sup>](#fn6 "footnote 6") <span id="f6"></span> Fed watchers and others in the public who pay close attention to the Committee's statements commonly examine a "tracked changes" version of the statement upon its release in order to look closely at words that have been added or dropped for clues about changes in the Committee's views on the economy or its policy intentions. Here, the tools we employ measure one aspect that is closely related to that "tracked changes" approach: the correlation of words used in two consecutive postmeeting statements.

More formally, we compute the "cosine similarity" between the "vector-space models" of consecutive FOMC statements to tell us how persistent the content of the statements has been over time. First, we create a 1302-by-126 matrix in which each row corresponds to one of the 1302 unique words contained in our sample of FOMC statements and each column corresponds to a single statement. We then populate the cells of the matrix with the frequency of each word in each statement making each column of the matrix a vector-space model of the corresponding FOMC statement. The cosine similarity between two FOMC statements, *a* and *b*, is equal to:

|  |  |
|:--:|---:|
| <img src="/econresdata/notes/feds-notes/2015/gifjpg/meade-acosta-img1-20150925.png" data-border="0" width="186" height="60" alt="\begin{displaymath} \frac{\sum_{i=1}^{n}a_ib_i}{(\sqrt{\sum_{i=1}^{n}a_i^2})(\sqrt{\sum_{i=1}^{n}b_i^2})},\notag \end{displaymath}" /> |   |

where *n* is the number of unique words (1302 in this case); *a<sub>i</sub>* and *b<sub>i</sub>* represent the number of times that word *i* occurs in statements *a* and *b*, respectively. From this definition, we see that two unrelated or "orthogonal" documents will have a cosine similarity equal to zero because they share no words (one or both of *a<sub>i</sub>* or *b<sub>i</sub>* equals zero, for all *i*).[<sup>7</sup>](#fn7 "footnote 7") <span id="f7"></span> Documents that use the same words in nearly the same proportion will have a cosine similarity that is close to unity. Thus, cosine similarity in NLP measures something very close to a correlation coefficient in data analysis. Measuring the cosine similarity for each pair of consecutive statements permits us to examine how consistent word usage is from statement to statement, with values close to unity representing high semantic similarity and persistence.

**Semantic similarity of raw postmeeting statements**
In this section, we examine the cosine similarity of the raw postmeeting statements. By "raw," we mean that the statements have not been subjected to any of the preprocessing that is common in natural language processing. That is, after downloading the statements from the Federal Reserve Board of Governors web site, we removed only punctuation, the paragraph(s) that provides voting information and an explanation of dissenting votes, if any, and the paragraphs at the end of some statements that report changes to the discount rate approved by the Board of Governors.

Returning to the "tracked changes" analogy, if the same words are used in consecutive FOMC statements (and we ignore changes in word order), we will see no red ink--that is, no changes--and cosine similarity will equal unity. The addition or subtraction of words or the use of the same words in different proportions will cause us to see some red ink and thus reduce cosine similarity. We illustrate this in table 1 with a tracked-changes version of the FOMC statement from December 2008. At that meeting, the Committee reduced its target for the federal funds rate to a range of 0 to 1/4 percent, noted in paragraph 1 of the statement, and added a lengthy new fifth paragraph discussing the Federal Reserve's balance sheet and asset purchase programs. The Committee also updated its views of economic activity and inflation in paragraphs 2 and 3. Significant policy changes were undertaken at the December 2008 meeting; such large changes in the statement language between the October and December 2008 meetings would be expected to result in a relatively low value of cosine similarity.


<span id="table1"></span>

<table width="700">
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr>
<th scope="col" data-bgcolor="#7c8f7c" height="25" data-valign="middle"><strong>Table 1. Tracking changes in the December 2008 FOMC statement</strong><br />
(Strikeout shows language that appeared in the October 2008 postmeeting statement but did not appear in the December 2008 statement; red language appeared in the December statement but not in the October statement; and words in black but not strikeout appeared in both statements.)</th>
</tr>
<tr>
<th scope="col"><em><img src="/econresdata/notes/feds-notes/2015/gifjpg/meade-acosta-table1-20150925.png" width="665" height="600" alt="Table 1. Tracking changes in the December 2008 FOMC statement." /></em></th>
</tr>
&#10;</tbody>
</table>


[Accessible version](semantic-analysis-of-the-FOMCs-postmeeting-statement-accessible-20150930.html#tab1)



Chart 3 shows the cosine similarity of consecutive, raw FOMC statements (the blue line) and an 8-meeting moving average (the red line);[<sup>8</sup>](#fn8 "footnote 8") <span id="f8"></span> note that cosine similarity dropped sharply in December 2008 to about 0.8, as predicted by our analysis of the tracked changes in the statement. Over the entire sample period, the meeting-to-meeting persistence in the raw statements has averaged 0.93.[<sup>9</sup>](#fn9 "footnote 9") <span id="f9"></span> Between the start of the sample in May 1999 and mid-2003, persistence averaged 0.86, before increasing to 0.94 between mid-2003 and mid-2007. Average persistence declined during the financial crisis and then rose to a very high level between 2009 and 2014. In addition, linguistic persistence was quite variable until about mid-2009, but has shown little meeting-to-meeting variation since then.


<span id="figure3"></span>

|  |
|----|
| **Chart 3. Semantic similarity of consecutive, raw FOMC statements** |
| *<img src="/econresdata/notes/feds-notes/2015/gifjpg/meade-acosta-chart3-20150925.png" width="390" height="402" alt="Chart 3. Semantic similarity of consecutive, raw FOMC statements. See accessible link for data." />* |


[Accessible version](semantic-analysis-of-the-FOMCs-postmeeting-statement-accessible-20150930.html#fig3)



**Preparation of the text using standard tools from natural language processing**
While cosine similarity of the raw documents provides a simple illustration of the semantic correlation of FOMC statements from meeting to meeting, it may not accurately represent the similarity of the intended or understood semantic content, which also depends on word complexity, multiple meanings of the same words, and different variations of the same root words. To get a handle on these issues, we employ some simple tools that are commonly used in computational linguistics to prepare-- or "preprocess"--the text; computing cosine similarities after such preparation provides a more meaningful and useful interpretation of how persistent the FOMC statements have been over time.

We subject each statement to three standard preprocessing steps: First, we remove common words that provide little semantic content, including pronouns, articles, conjunctions, dates, numbers, and geographic words.[<sup>10</sup>](#fn10 "footnote 10") <span id="f10"></span> Next, we concatenate phrases when words used together take on a particular meaning--for example, *Federal Open Market Committee* or *federal funds rate--*so that different uses of the component words can be distinguished. In the final preprocessing step, we "stem" all words down to a root, meaning, for example, that *increase*, *increased*, *increases* and *increasing* are all shortened to *increas*--the original words are removed from the term-document matrix and a row for each stem is added that contains the sum of the counts of the original words. Table 2 provides some examples of the effects of the preprocessing steps for particular words. After the preprocessing is completed, the term-document matrix contains 721 rows (one for each stemmed term) and 126 columns (one for each FOMC statement).


<span id="table2"></span>

| **Table 2. Effects of text preparation** |
|------------------------------------------|

| Original word or term | After stemming or concatenation | Words that share stem | Total occurrences of stem | Number of documents containing stem | TFIDF score |
|----|----|----|----|----|----|
| decisionmaking | decisionmak | -- | 1 | 1 | 4.83 |
| inflation | infl | inflationary | 548 | 114 | 0.1 |
| federal funds rate | fedfundsrate | -- | 188 | 125 | 0.08 |


 

Finally, we apply a standard weighting scheme known as term frequency–inverse document frequency (TFIDF) to the now-smaller term-document matrix. Again, in the term-document matrix, the *ij*<sup>th</sup> entry represents the number of times that the stemmed term *i* is used in document *j*. We compute the number of documents in which term *i* occurs, *n<sub>i</sub>* , and then weight each row--that is, each word--of the matrix by *ln(n/n<sub>i</sub>)*. The effect of this procedure is to give a lower weight to terms that occur in many documents.

The final column of table 2 lists the TFIDF score for each stemmed term. To better illustrate how the weighting works, chart 4 provides a histogram of the number of documents in which each term is used, *n<sub>i</sub>* (the blue bars), and the TFIDF score (the black line) associated with each value of *n<sub>i</sub>*. The blue bars at the right hand side of the graph represent words that occur often in FOMC statements, and thus receive a lower weight. For instance, words that occur in every postmeeting statement, such as "Committee," have a TFIDF score of zero because such words don't help to distinguish semantic content between documents. Of course, there are meaningful terms--such as "inflation" or "federal funds rate"--that also have a very low TFIDF score. In such cases, the context in which the term is used is what allows us to assign meaning. And, the rarer are these context words, the higher is their TFIDF weight.


<span id="figure4"></span>

|  |
|----|
| **Chart 4. Computing the TFIDF score** |
| *<img src="/econresdata/notes/feds-notes/2015/gifjpg/meade-acosta-chart4-20150925.png" width="413" height="400" alt="Chart 4. Computing the TFIDF score. See accessible link for data." />* |


[Accessible version](semantic-analysis-of-the-FOMCs-postmeeting-statement-accessible-20150930.html#fig4)



**Semantic similarity of prepared FOMC statements**
Charts 5.a and 5.b illustrate the effects of the text preparation steps on the cosine similarity of consecutive FOMC statements: 5.a folds in the three text preprocessing steps while 5.b includes both the preprocessing steps and the weighting scheme. The preparation of the text reduces the level of cosine similarity, though the upward trend and overall shape of persistence is similar to our baseline case. However, for the treated documents there is a level shift downward from the baseline case, which tells us that the postmeeting statements are less similar when closer attention is paid to their semantic content. This is especially so when the TFIDF weighting is included, as this weighting is based on the importance of individual words over the entire sample of FOMC statements. This is most readily seen in chart 6, which shows the moving average of cosine similarity from the baseline case with no preprocessing (the solid line), the moving average when text preprocessing is included (the dash-dotted line), and the moving average when both the preprocessing steps and TFIDF weighting are included (the dashed line). Here it is clear that cosine similarity with text preparation is more volatile than the baseline and that there is lower semantic similarity than in the baseline, particularly when the TFIDF weighting is included.


<span id="figure5a"></span>

|  |
|----|
| **Chart 5.a. Semantic similarity of consecutive, prepared FOMC statements** |
| *<img src="/econresdata/notes/feds-notes/2015/gifjpg/meade-acosta-chart5a-20150925.png" width="390" height="402" alt="Chart 5.a. Semantic similarity of consecutive, prepared FOMC statements." />* |


Note: Text preprocessing only.

[Accessible version](semantic-analysis-of-the-FOMCs-postmeeting-statement-accessible-20150930.html#fig5a)




<span id="figure5b"></span>

|  |
|----|
| **Chart 5.b. Semantic similarity of consecutive, prepared FOMC statements** |
| *<img src="/econresdata/notes/feds-notes/2015/gifjpg/meade-acosta-chart5b-20150925.png" width="390" height="402" alt="Chart 5.b. Semantic similarity of consecutive, prepared FOMC statements. See accessible link for data." />* |


Note: Text preprocessing and TFIDF weighting.

[Accessible version](semantic-analysis-of-the-FOMCs-postmeeting-statement-accessible-20150930.html#fig5b)




<span id="figure6"></span>

|  |
|----|
| **Chart 6. Semantic similarity moving averages** |
| *<img src="/econresdata/notes/feds-notes/2015/gifjpg/meade-acosta-chart6-20150925.png" width="390" height="402" alt="Chart 6. Semantic similarity moving averages. See accessible link for data." />* |


[Accessible version](semantic-analysis-of-the-FOMCs-postmeeting-statement-accessible-20150930.html#fig6)



Earlier we noted that the December 2008 statement had a low value of cosine similarity (0.8) when compared with the statement issued in October 2008. With text preprocessing, cosine similarity drops substantially--to about 0.5--largely because of the removal of commonly-used words and the fact that the December statement contained many words not present in the October statement (increasing the denominator relative to the numerator in the computation of cosine similarity). Furthermore, when the TFIDF weighting is included, the cosine similarity value of the December statement falls to almost 0.1 giving it the lowest score in terms of meeting-to-meeting semantic persistence of any statement in chart 5.b. This tells us that the words introduced in the December statement were also relatively rare--thus, the TFIDF weighting gives more prominence to them (increasing the denominator in the cosine similarity computation even further). For example, the terms "sheet" (as in "balance sheet"), "benefit," and "est" (the root of "establish") are highly unusual and present in the December statement (but absent from the October one).

**Conclusion**
The FOMC postmeeting statement is one of the Federal Reserve's most important communications vehicles. In this note, we have used techniques developed in computational linguistics to demonstrate that FOMC statements have become steadily more similar in content from meeting to meeting, particularly since the financial crisis. Moreover, once we look beyond the raw language in the statements, we find that the semantic content of the statements from one FOMC meeting to the next is less similar and more variable than would appear at first glance. We focused on the postmeeting statement that the FOMC issued in December 2008, which announced significant changes in monetary policy, illustrating that NLP tools can help us to uncover just how unusual the FOMC statement issued after that meeting was and suggesting how useful these tools can be in studying FOMC communications more generally.


------------------------------------------------------------------------


<span id="fn1">1.</span> The authors thank Steve Meyer and Robert Tetlow for helpful comments. [Return to text](#f1)

<span id="fn2">2.</span> The voting information had previously been included only in the meeting minutes, which at that time were released about six weeks after an FOMC meeting. [Return to text](#f2)

<span id="fn3">3.</span> In order to make the December 2014 statement comparable to the February 1994 one, we stripped out the voting information from the former before taking the word and sentence counts. [Return to text](#f3)

<span id="fn4">4.</span> Hernández-Murillo, Rubén and Hannah G. Shell (2014), "[Rising Complexity of the FOMC Statement](http://research.stlouisfed.org/publications/es/article/10252)," *Economic Synopses*, Number 23. [Return to text](#f4)

<span id="fn5">5.</span> Each panel in Chart 2 shows how many times the given words ("productive" and "productivity," for example) are used in each postmeeting statement. Because there are eight FOMC meetings per year, there are eight data points for each set of words each year. Some panels also show a related macroeconomic data series from FRED. [Return to text](#f5)

<span id="fn6">6.</span> For a discussion of techniques, see David Bholat, Stephen Hansen, Pedro Santos and Cheryl Schonhardt-Bailey (2015), "[Text mining for central banks (PDF)](http://www.bankofengland.co.uk/education/Documents/ccbs/handbooks/pdf/ccbshb33.pdf)," CCBS Handbook No. 33, Bank of England; for application of the techniques to central bank texts, see Miguel Acosta (2015), "FOMC Responses to Calls for Transparency," Finance and Economic Discussion Series 2015-060, Board of Governors of the Federal Reserve System; Stephen Hansen, Michael McMahon, and Andrea Prat (2014), "Transparency and Deliberation within the FOMC: a Computational Linguistics Approach," CEP Discussion Papers DP 1276, Centre for Economic Performance, London School of Economics; Cheryl Schonhardt-Bailey (2013), *Deliberating American Monetary Policy: A Textual Analysis*, MIT Press, Cambridge, MA. [Return to text](#f6)

<span id="fn7">7.</span> Note that the cosine similarity measure does not increase or reduce the similarity of two documents based on differences in document length--this is because of the normalization that occurs in the denominator. See the discussion in Bholat et al. (2015). [Return to text](#f7)

<span id="fn8">8.</span> There are eight FOMC meetings per year, so an 8-meeting moving average is essentially a 1-year window. [Return to text](#f8)

<span id="fn9">9.</span> Taking the average of cosine similarity through 2008 allows for a comparison with measures of FOMC minutes and transcript persistence presented in Acosta (2015): FOMC statement persistence from 1999 through 2008 (0.90) is just slightly higher than the raw persistence of FOMC minutes (0.85) or transcripts (0.89). [Return to text](#f9)

<span id="fn10">10.</span> For example, the word "the" occurs 2,629 times in the statements in our sample. Common text preparation includes the removal of all numbers, a procedure we follow here; however, certain numbers--such as the Committee's target for the federal funds rate or the dates in its calendar-based forward guidance, may be important to retain. See Bill McDonald's *Textual Analysis* webpage for the lists used here: Generic; Dates and Numbers; and Geographic. In natural language processing, parts of speech such as pronouns, articles, and conjunctions are termed "stop words." [Return to text](#f10)


**Please cite as:**

Meade, Ellen E., and Miguel Acosta (2015). "Hanging on every word: Semantic analysis of the FOMC's postmeeting statement," FEDS Notes. Washington: Board of Governors of the Federal Reserve System, September 30, 2015. https://doi.org/10.17016/2380-7172.1580





***Disclaimer:** FEDS Notes are articles in which Board economists offer their own views and present analysis on a range of topics in economics and finance. These articles are shorter and less technically oriented than FEDS Working Papers.*

