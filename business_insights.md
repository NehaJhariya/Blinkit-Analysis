# Business Insights

Derived from the SQL analysis and Python EDA on the 2024 order dataset.

1. Orders with delivery time under 10 minutes cancel at roughly half the
   rate of orders that cross the 30-minute mark — delivery delay is a
   direct driver of cancellations, not just a satisfaction issue.
2. Cancellation rate is not uniform across cities — a handful of cities
   consistently run above the network average, pointing to localized
   store or delivery-partner capacity problems rather than a company-wide issue.
3. Revenue is concentrated in a small set of categories (Staples, Dairy &
   Breakfast, Snacks) — these are the categories that must never stock out.
4. Loyal customers are a minority of the customer base by count but
   contribute a disproportionate share of revenue — retention economics
   clearly outweigh pure acquisition economics here.
5. The repeat purchase rate shows a meaningful share of one-time buyers
   never return — the biggest single lever for growth is converting
   "New" customers into a second order.
6. Festive months (October–November) show a clear seasonal spike in both
   order volume and delivery time — capacity planning needs to happen
   ahead of, not during, the festive rush.
7. Weekends consistently show higher order volumes and slightly higher
   average order values than weekdays.
8. Coupon-used orders have a higher average order value but a visibly
   thinner profit margin — discounting is driving basket size, at a cost.
9. A subset of delivery partners show both slower average delivery times
   and higher cancellation rates on their orders — performance is not
   evenly distributed across the partner network.
10. Ratings decline as delivery time increases — customer satisfaction is
    measurably tied to delivery speed, reinforcing insight #1.
11. Store-level performance varies widely even within the same city —
    the gap between the best and worst store per city is a specific,
    fixable operational target.
12. Cash-on-delivery orders make up a meaningful share of volume and skew
    toward slightly higher cancellation risk than prepaid methods.
13. Certain categories (e.g. Home Care, Personal Care) show healthy
    revenue but comparatively thin margins — pricing or vendor-cost
    review is warranted there.
14. Order volume peaks in the early evening hours, suggesting staffing
    and delivery-partner allocation should be weighted toward that window.
15. High-value customers who also give below-average ratings represent a
    small but high-priority "at risk of churn" segment — losing them
    costs disproportionately more than losing an average customer.
16. Month-over-month revenue growth is uneven rather than steadily
    increasing — a few months show visible slowdowns worth investigating
    against marketing spend and delivery performance for that period.
17. The Web platform and iOS devices represent a small share of total
    orders relative to Android/App — there may be untapped growth in
    improving that experience.
18. Average order value differs by marketing channel — some channels
    bring in more orders, others bring in higher-value orders; treating
    all acquisition spend the same undercounts channel quality.
19. A visible cluster of extreme delivery-time outliers exists beyond the
    typical range — these are likely operational failures worth root-cause
    investigation rather than statistical noise to be ignored.
20. Overall, the data supports the project's core hypothesis: delivery
    performance, not pricing or product mix, is the primary lever behind
    the cancellation problem.
