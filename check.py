from pymilvus import connections, utility, MilvusException

try:
    connections.connect(host="localhost", port="19530")
    print("Successfully connected to Milvus.")

    collections = utility.list_collections()
    print(f"List of collections:\n{collections}")

except MilvusException as e:
    print(f"An error occurred: {e}")

except Exception as e:
    print(f"An unexpected error occurred: {e}")


    
