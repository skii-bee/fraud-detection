---- MODULE fraud_check_working ----
EXTENDS Integers, TLC

VARIABLES amount, q1, q3, iqr, is_anomaly

Init == /\ amount \in 1..5
        /\ q1 \in 1..5
        /\ q3 \in 1..5
        /\ iqr = q3 - q1
        /\ iqr >= 0
        /\ is_anomaly = FALSE

(* The next-state action: compute anomaly flag based on IQR *)
Next ==
    LET
        lower == q1 - ((3 * iqr) \div 2)
        upper == q3 + ((3 * iqr) \div 2)
    IN
        is_anomaly' = (amount < lower \/ amount > upper)
        /\ UNCHANGED <<amount, q1, q3, iqr>>

Spec == Init /\ [][Next]_<<amount, q1, q3, iqr, is_anomaly>>

(* Type invariant *)
TypeOK == /\ amount \in 1..5
          /\ q1 \in 1..5
          /\ q3 \in 1..5
          /\ iqr \in 0..5
          /\ is_anomaly \in {TRUE, FALSE}

(* Safety: no false positives *)
NoFalsePositive ==
    LET
        lower == q1 - ((3 * iqr) \div 2)
        upper == q3 + ((3 * iqr) \div 2)
    IN
        (is_anomaly = TRUE) => (amount < lower \/ amount > upper)

====