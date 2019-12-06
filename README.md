# CS6360-database

Database project for CS6360

Program is only compatible with Python 3
Required libraries are listed in the requirements folder.

Commands supported:
	CREATE	
	DEBUG
	DELETE
	DROP
	EOF
	EXIT
	HELP
	INSERT
	SELECT
	SHOW
	UPDATE

Value types supported:
	python primitives (namely INT and string as TEXT)
	Date
	DateTime
	Time
	Year
	
************************************
Assumptions:
************************************
1) Used a "is_unique" field instead of the column_key field for uniqueness mechanism.
2) In the B+1 table implementation, in a overflow split of an interior node, only the last child is split, such that the sibiling overflow node is a degree one node, with no cells.
3) The data points are all small enough to fit in a page.
