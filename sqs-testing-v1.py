#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   sqs-testing-v1.py
@Modified:   2023/10/10 22:24:30
@Author  :   Yash Pareek 
@Version :   1.0
@Contact :   yashpareek.workmail@gmail.com
@License :   MIT
@Desc    :   App to transcribe and translate Video files uploaded to Amazon S3 bucket.
'''

import warnings
warnings.simplefilter('ignore')
import boto3
import time
import os
import whisper
import logging
logging.basicConfig(filename='/home/ubuntu/final-v2/sqs-testing-v1.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
from utils import process_message

logging.basicConfig(filename='/home/ubuntu/final-v2/sqs-testing-v1.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

import time
import mysql.connector
from mysql.connector import Error

def main():
    """
    Main function to process messages from the database.
    """
    connection = None
    try:
        logging.info("Loading Model --> Whisper base")
        start_time = time.time()
        model = whisper.load_model("base").to('cuda')
        logging.info(f"Model loaded in {time.time() - start_time:.2f} seconds")

        # Connect to the database
        connection = mysql.connector.connect(
            host='',
            port=3306,
            database='',
            user='',
            password=''
        )

        if connection.is_connected():
            db_Info = connection.get_server_info()
            logging.info(f"Connected to MySQL Server version {db_Info}")
            cursor = connection.cursor()
            empty_polls = 0

            while True:
                try:
                    
                    # Query the database for new files
                    cursor.execute("SELECT id, s3file_url FROM upload_s3_files WHERE VTT_gen = FALSE AND picked = FALSE LIMIT 1")
                    record = cursor.fetchone()

                    if record:
                        file_id, s3_url, target_languages = record

                        # Mark the file as picked
                        cursor.execute("UPDATE upload_s3_files SET picked = TRUE WHERE id = %s", (file_id,))
                        connection.commit()

                        # Process the message
                        process_message(s3_url, file_id, target_languages, model, connection, cursor)  # Assuming the message body is the s3_url
                        
                        empty_polls = 0  # Reset the empty poll counter
                    else:
                        empty_polls += 1
                        logging.info("No new files in this polling cycle.")
                        connection.commit()

                        # If we've polled for 300 seconds without new files, shut down
                        if empty_polls >= 15:
                            logging.info("No new files for 300 seconds. Exiting.")
                            connection.commit()
                            break

                    # Sleep for a bit before the next poll
                    time.sleep(20)

                except Error as e:
                    logging.error(f"Error while processing database records. Error: {e}")
                    # You might want to add some retry logic here

    except Error as e:
        logging.error(f"Error in main function. Error: {e}")

    finally:
        if connection is not None and connection.is_connected():
            cursor.close()
            connection.close()
            logging.info("MySQL connection is closed")

if __name__ == "__main__":
    main()