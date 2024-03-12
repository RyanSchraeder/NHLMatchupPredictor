import time

# Snowflake Connections
from connectors import get_snowflake_connection

def snowflake_query_exec(queries, method: str = 'standard'):

    try:
        # Cursor & Connection
        conn = get_snowflake_connection(method)
        print(f"Snowflake connection established: {conn}")

        response = {}

        if conn:
            curs = conn.cursor()

            # Retrieve formatted queries and execute - Snowflake Connector Form. Async
            for idx, query in queries.items():

                print(
                    f"""
                    Executing Query {idx}: \n
                    \t{query}\n
                    """
                )

                curs.execute_async(query)
                query_id = curs.sfqid
                print(f'Query added to queue: {query_id}')

                curs.get_results_from_sfqid(query_id)

                # IF THE SNOWFLAKE QUERY RETURNS DATA, STORE IT. ELSE, CONTINUE PROCESS.
                result = curs.fetchone()
                df = curs.fetch_pandas_all()

                if result:
                    print(f'Query result: {result}')
                    print(f'Query completed successfully and stored: {query_id}')
                    response[idx] = result[0]
                    if len(df):
                        response[idx] = df

                while conn.is_still_running(conn.get_query_status_throw_if_error(query_id)):
                    print(f'Awaiting query completion for {query_id}')
                    time.sleep(1)

            return response

    except Exception as err:
        print(f'Programming Error: {err}')
