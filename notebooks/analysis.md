
**Q1:**
The United Kingdom accounts for approximately 88.3% of total revenue lost through returns (€636.9K out of €721.6K), making it by far the largest contributor to revenue leakage.


PAPER CRAFT, LITTLE BIRDIE generated the highest return value (€168.5K) from a single return transaction. This is explained by a full return of 80,995 units only 12 minutes after the original purchase, suggesting a bulk-order cancellation/return rather than typical customer return behavior.
The **REGENCY CAKESTAND 3 TIER** has the highest return frequency, with **359 return transactions**, followed by the **BAKING SET 9 PIECE RETROSPOT** (213) and the **STRAWBERRY CERAMIC TRINKET BOX** (190). This indicates that these products are frequently returned, even though their total financial impact is much lower than the high-value outlier identified in the return-value analysis.

Revenue leakage is highly concentrated in a few months. **December 2011 recorded the highest leakage rate at 28.31%, with €174.1K in returned value against €615.0K in gross revenue.** January 2011 follows with a leakage rate of 13.64%. After these peaks, leakage rates remain substantially lower, with most months below 6.5%. This indicates that certain periods experienced unusually high return activity and may require further investigation for seasonal or operational drivers.

12,340 (69.2%) negative-quantity rows were matched to a prior positive purchase of the same product and customer within the previous month and were classified as True Returns.
5,484 (30.8%) negative-quantity rows could not be matched to a prior purchase within the defined one-month window and were classified as Standalone.
Overall, 17,824 negative-quantity return entries were identified.

**Q2:**

Customer ID 0 was excluded because it represents guest/anonymously recorded transactions rather than an identifiable customer, so it is not suitable for per-customer RFM analysis.


**The results show that the three RFM variables are positively skewed, but to different degrees:
Recency (skewness = 0.89): moderately right-skewed, indicating that most customers have relatively recent purchases, while a smaller number of customers have much higher recency values.
Frequency (skewness = 12.04): highly right-skewed. Most customers have a relatively low number of invoices, while a small number of customers make purchases very frequently.
Monetary (skewness = 25.55): extremely right-skewed, indicating that most customers generate relatively low revenue, while a small number of customers have exceptionally high spending.

**The quantiles confirm this strong concentration. For Monetary, the median is 880.04, meaning that 50% of customers generate revenue below this value. At the 75th percentile, Monetary reaches 2,282.28, while 90% of customers are below 5,490.07. However, the maximum value reaches 603,421.65. This shows that the upper tail contains a small number of extremely high-value customers.

Overall, the distributions are clearly not balanced and contain substantial differences between the majority of customers and a small group of high-frequency or high-value customers. Therefore, quantile-based binning is appropriate because it ranks customers according to their relative position within each distribution rather than relying on fixed numerical intervals.

Selection of the Number of Buckets

We compared 3, 4, and 5 quantile-based buckets for each RFM variable. Recency and Monetary produced relatively balanced customer groups across all three options. Frequency, however, remained highly concentrated in the lower ranges because many customers have a low number of invoices, reflecting the strong right-skewness observed in the distribution.

We selected four buckets as a balance between granularity and interpretability. Three buckets would provide a relatively coarse segmentation, while five buckets would add limited additional business value and would further highlight the concentration of customers in the lowest Frequency group. Four buckets therefore provide sufficient differentiation between customers while keeping the resulting RFM segments practical to interpret.

==>
Champions are the most valuable customers, combining recent purchases, high purchase frequency, and high monetary value. At-risk customers show lower recency despite relatively strong purchasing activity, indicating potential future churn. Low-value or lost customers have both low engagement and low monetary contribution.


- **Q3 — Churn Definition (statistically derived)**

Sensitivity analysis: Increasing the churn cutoff from 106 to 166 days reduced the number of churned customers from 2,847 to 2,464. The baseline cutoff of 136 days resulted in 2,635 churned customers. This shows that the estimated churn population is sensitive to the cutoff choice, although the overall number of churned customers remains within a similar range.

- **Q4 — Cohort Retention**

Cohort retention analysis shows a substantial drop in customer activity after the acquisition month. Retention varies across acquisition cohorts, indicating differences in customer engagement over time. The analysis allows us to identify cohorts with stronger or weaker retention and evaluate how customer activity evolves after acquisition.


- **Q5 — Customer Lifetime Value**

Historical CLV varies substantially across customers, with a small number of customers generating very high cumulative revenue. Customer 18102 has the highest observed CLV at 603,421.65, followed by customer 14646 at 526,751.52. This concentration of revenue highlights the importance of identifying and retaining high-value customers.

# Phase 2 — Feature Engineering & Churn Model

## 1. Feature Engineering and Time-Aware Split

Instead of using a random 80/20 split, I used a time-aware approach based on observation dates. Customer features are calculated using only transactions available up to each observation date, while future purchases are used to define the churn target. This helps prevent data leakage and better reflects a real-world prediction scenario.

I created a reusable `customer_feature_engineering()` function and generated two snapshots:

| Snapshot | Observation Date | Number of Customers |
|---|---|---:|
| Snapshot 1 | 2010-03-31 | 2,135 |
| Snapshot 2 | 2010-08-31 | 3,299 |

Each snapshot contains the following features: `customer_id`, `recency`, `frequency`, `monetary`, `cohort_month`, `days_since_first_purchase`, `average_order_value`, and `distinct_products_bought`.

The churn target is defined using the following 136 days after each observation date. Customers with no valid purchase during this period are labelled `churned = 1`; otherwise, they are labelled `churned = 0`.

Snapshot 1 is used for training, while Snapshot 2 is reserved for testing. The target windows do not overlap, and the training target window ends before the test observation date.

## 2. Baseline Model — Logistic Regression

Logistic Regression achieved **66% accuracy** and a **PR-AUC of 0.589**. For the churned class, precision was 54%, recall was 74%, and the F1-score was 0.62.

The model identified 920 of the 1,242 churned customers. However, it also produced 784 false positives. Overall, the model identified a substantial proportion of churned customers, but its precision indicates room for improvement.

## 3. XGBoost Model

The initial XGBoost model achieved **65% accuracy** and a **PR-AUC of 0.549**. Its churn precision was 55%, while recall was 50%. Compared with Logistic Regression, it performed worse in terms of recall, F1-score, and PR-AUC.

## 4. XGBoost with Bayesian Optimization

I used Bayesian Optimization with Optuna to tune the XGBoost hyperparameters, using cross-validation on the training data and Average Precision as the optimization objective.

After optimization, XGBoost achieved **68% accuracy** and a **PR-AUC of 0.583**. Churn precision increased to 60%, but recall decreased to 47%. Although the optimized model improved accuracy and precision compared with the initial XGBoost model, its PR-AUC remained slightly below the Logistic Regression baseline.

## Why Bayesian Optimization?**

Bayesian Optimization can be more sample-efficient than grid or random search because it uses the results of previous trials to guide the selection of the next hyperparameter configurations. Instead of testing combinations blindly, it builds a probabilistic model of the objective function and focuses on promising configurations. This is particularly useful when model evaluation is computationally expensive. In this project, Bayesian Optimization with Optuna aims to find better XGBoost hyperparameters with a limited number of trials, reducing unnecessary evaluations.

## the Brier score
The optimized XGBoost model achieved a Brier Score of 0.1985. This metric evaluates the accuracy of predicted probabilities by comparing them with the actual outcomes. A lower score indicates better probabilistic predictions. However, the Brier Score alone does not confirm whether the model is well-calibrated.

## Feature Importance Analysis**

The feature importance plot shows that `monetary` is the most important feature, followed by `frequency` and `distinct_products_bought`. This suggests that customers' total spending, purchase frequency, and product diversity play an important role in the model's churn predictions. In contrast, `cohort_month` and `days_since_first_purchase` have lower importance. However, feature importance does not show whether a feature increases or decreases churn probability.

### SHAP Analysis

The SHAP summary plot shows that `monetary` and `frequency` are the most influential features in the model's predictions, followed by `recency` and `distinct_products_bought`. Higher monetary values and purchase frequency generally push predictions towards non-churn, while higher recency tends to push predictions towards churn. The impact of `average_order_value` varies across customers, whereas `cohort_month` and `days_since_first_purchase` have relatively smaller effects. Overall, SHAP helps explain how different customer behaviors influence churn predictions.

## ======================================================================================================================

### FastAPI Project Structure

The `api/` folder contains four files, each with a specific responsibility:

- **`main.py`**: Defines the API endpoints and handles incoming requests.
- **`schemas.py`**: Defines Pydantic models for input validation and response formatting.
- **`database.py`**: Manages the connection to the SQLite database.
- **`__init__.py`**: Marks the folder as a Python package.

