
  create or replace   view banking.analytics.my_second_dbt_model
  
  
  
  
  as (
    -- Use the `ref` function to select from other models

select *
from banking.analytics.my_first_dbt_model
where id = 1
  );

