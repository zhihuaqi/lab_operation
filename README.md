# Dependencies:
1. anaconda for python 3
2. sqlit3

# Data:
The raw data is a sqlite database file that contains 3 tables:
1. batch - Each row represents a "batch" of samples processed together. It has a primary key, a name, and a value of a sequencing quality metric associated with the batch.
2. component - Each row represents a component that may be used in the processing of the batch. Each component has a primary key, a name, and a component type.
3. batch_to_component - This is a many to many lookup table that is used to join the batch and component table. It has a primary key, a foreign key reference to batch and a foreign key to component.

# Instructions for running:

Put the input sqlite file in the same folder of the script run.py and the Makefile.
- `make run`
	It will run the run.py with the path to the sqlite file and the result will be saved in result.csv.
- `make clean`
	It will remove the result file.




