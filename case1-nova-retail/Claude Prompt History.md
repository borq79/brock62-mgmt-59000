1. Create app.py and requirements.txt; answer "which customers generate the most revenue" with a bar chart of CustomerID (x) vs. total PurchaseAmount (y).
2. The x-axis is wrong — CustomerID is a label, not a monetary value. Change to a histogram.
3. Go back to a bar chart, but treat the x-axis as categorical (not numeric).
4. The x-axis is incremental — only show CustomerIDs that exist in the file.
5. Add a CustomerID filter on the left side of the page; color-code bars by ProductCategory with a legend below; add a ProductCategory filter.
6. Move filters to the left sidebar; color-code bars by ProductCategory; add ProductCategory filter.
7. Add filters for Customer Segment, Region, and Retail Channel to the sidebar; add tabs for Growth Opportunities, Decline & Risk, and Strategic Recommendations with the charts you recommended.
8. Fix TypeError: '<' not supported between instances of 'float' and 'str' on the label sort.
9. The charts only go to February 1, 2023 — why is February data excluded?
10. Drop any row with NaN or null values from the data.
11. Change charts so January is on the left and February is on the right.
12. The Revenue by Customer chart is too busy — is there a better way to visualize it?
13. Use option 2 (treemap).
14. Also add option 1 (simple bar chart) above the treemap.
15. Create ClaudePrompt.md with everything needed to recreate the dashboard from scratch in a single prompt.

It didn't show up in the Claude history for whatever reason, but I did use Claude to help recommend the right data sets visualizations based on the questions to be answered. It recommended quite a few for me to chose from and I use it to generate the first draft. After refinement I asked it (step 15) to generate a single prompt for me based on our history to recreate the entire dashboard in a single prompt, similar to your example in the Video Lab (week 3 video 2)