import pyarrow.parquet as pq

table = pq.read_table("test.parquet").to_pandas()

print(table)



