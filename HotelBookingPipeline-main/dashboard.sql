select avg(total_amount) as average_booking_price from gold_booking_clean;

select sum(num_guests) as total_guests from gold_booking_clean;

select COUNT(*) TOTAL_BOOKINGS
from GOLD_BOOKING_CLEAN;


select SUM(TOTAL_AMOUNT) AS TOTAL_REVEUNUE
from GOLD_BOOKING_CLEAN


SELECT date, total_revenue
FROM GOLD_AGG_DAILY_BOOKING
ORDER BY date;

SELECT date, number_of_bookings
FROM GOLD_AGG_DAILY_BOOKING
ORDER BY date;

select HOTEL_CITY, TOTAL_REVENUE,
from GOLD_AGG_CITY_BOOKING
where TOTAL_REVENUE is not null
order by TOTAL_REVENUE desc
limit 5;

select BOOKING_STATUS AS status, count(*) as total_bookings
from PUBLIC.GOLD_BOOKING_CLEAN
where status is not null
group by status
order by total_bookings desc;

select room_type, count(*) as total_bookings
from PUBLIC.GOLD_BOOKING_CLEAN
where room_type is not null
group by room_type
order by total_bookings DESC
