# `datetime` module

The `datetime` module consists of several functions that assist with date and time related tasks. Additionally, it includes two classes (`DateTime` and `DTDiff`).

<center>

Variable    | Contents
---         | ---
MONTHS      | `["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]`
WEEKDAYS    | `["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]`

Function                    | Use
---                         | ---
`sleep_seconds(seconds)`    | Pauses execution for `seconds` seconds.
`sleep_minutes(minutes)`    | Pauses execution for `minutes` minutes.
`is_leap_year(year)`        | Returns `1` if the year is a leap year, `0` otherwise.
`days_in_month(year, month)`| Returns the amount of days in a given month keeping in track leapyears.
`month_name(n)`             | Gives the name of a numbered month where `1` is `January`.
`weekday_name(n)`           | Gives the day of a week from a number<br>where `1` is a `Monday` and `7` is `Sunday`.
`timestamp_utc([ts])`       | Yields the `UTC` timestamp using the provided timestamp or current time.

</center>

## DateTime

<center>

Method                      | Use
---                         | ---
`subtract(other)`           | Subtract two DateTime objects, returns a DTDiff object.
`to_timestamp()`            | Returns the date & time as a Unix timestamp in milliseconds.
`from_timestamp()` (static) | Returns a DateTime object from a Unix timestamp in milliseconds.
`!`                         | Return the date and time in the format `Y-M-D h:m:s.z`.

</center>
