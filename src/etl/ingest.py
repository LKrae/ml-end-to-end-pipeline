from prefect import flow, task

@task
def say_hello():
    print("ETL pipeline placeholder — ready to build!")

@flow
def etl_flow():
    say_hello()

if __name__ == "__main__":
    etl_flow()
