import os
import logging
import json
import azure.functions as func
from pymongo import MongoClient
from bson.objectid import ObjectId

# Lazy-initialized MongoDB client
_client = None
def get_client():
    global _client
    if _client is None:
        uri = os.getenv("MONGODB_ATLAS_URI")
        if not uri:
            raise ValueError("MONGODB_ATLAS_URI is not set")
        _client = MongoClient(uri)
    return _client

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("MongoApi triggered")

    # Read query parameters
    db_name   = req.params.get("db")
    coll_name = req.params.get("coll")
    doc_id    = req.params.get("id")

    if not db_name or not coll_name:
        return func.HttpResponse(
            "Please pass both ?db=<database>&coll=<collection>",
            status_code=400
        )

    try:
        collection = get_client()[db_name][coll_name]

        if doc_id:
            # Fetch a single document
            doc = collection.find_one({"_id": ObjectId(doc_id)})
            if not doc:
                return func.HttpResponse(
                    f"Document with id {doc_id} not found",
                    status_code=404
                )
            # Convert the _id to a string
            doc["_id"] = str(doc["_id"])
            # Dump with default=str to handle datetimes, ObjectIds, etc.
            payload = json.dumps(doc, default=str)
            return func.HttpResponse(
                body=payload,
                mimetype="application/json",
                status_code=200
            )

        else:
            # List up to 100 documents
            docs = list(collection.find().limit(100))
            for d in docs:
                d["_id"] = str(d["_id"])
            payload = json.dumps(docs, default=str)
            return func.HttpResponse(
                body=payload,
                mimetype="application/json",
                status_code=200
            )

    except Exception as e:
        logging.error(f"Error querying MongoDB: {e}")
        return func.HttpResponse(
            f"Server error: {e}",
            status_code=500
        )
