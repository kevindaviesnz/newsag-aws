# see https://docs.aws.amazon.com/code-library/latest/ug/python_3_dynamodb_code_examples.html

# Create news article table
# @see https://docs.aws.amazon.com/goto/boto3/dynamodb-2012-08-10/CreateTable

# @see https://github.com/awsdocs/aws-doc-sdk-examples
# @see https://github.com/awsdocs/aws-doc-sdk-examples/tree/main/python/example_code/dynamodb

# python -m pip install -r requirements.txt

# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""
Purpose

Shows how to use the AWS SDK for Python (Boto3) with Amazon DynamoDB to
create and use a table that stores data about movies.

1. Load the table with data from a JSON file
2. Perform basic operations like adding, getting, and updating data for individual movies.
3. Use conditional expressions to update movie data only when it meets certain criteria.
4. Query and scan the table to retrieve movie data that meets varying criteria.
"""

# snippet-start:[python.example_code.dynamodb.helper.Movies.imports]
from decimal import Decimal
from io import BytesIO
import json
import logging
import os
from pprint import pprint
import requests
from zipfile import ZipFile
import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
#from question import Question

from datetime import datetime
from scraper import fetch_html
from scraper import get_article_containers
from foxnews import foxnews_parse_article_content
from bs4 import BeautifulSoup
from typing import List, Dict
import requests
import time
from boto3.dynamodb.conditions import Attr

logger = logging.getLogger(__name__)
# snippet-end:[python.example_code.dynamodb.helper.Movies.imports]


# snippet-start:[python.example_code.dynamodb.helper.Movies.class_full]
# snippet-start:[python.example_code.dynamodb.helper.Movies.class_decl]
class NewsArticles:

    def __init__(self, dyn_resource, news_articles):
        """
        :param dyn_resource: A Boto3 DynamoDB resource.
        :param news_articles: List of news articles. Each article id is a dictionary object.
        """
        self.dyn_resource = dyn_resource
        self.news_articles = news_articles
        # The table variable is set during the scenario in the call to
        # 'exists' if the table exists. Otherwise, it is set by 'create_table'.
        self.table = None

    # snippet-end:[python.example_code.dynamodb.helper.Movies.class_decl]

    def remove_dead_news_articles(self):
        """
        Removes records where there is no 'ttl' field or where the sum of 'ttl' and 'time_added' is less than the current time.
        """
        try:
            current_timestamp = Decimal(str(time.mktime(datetime.now().timetuple())))

            # Scan the table to fetch all items
            response = self.table.scan()

            # Iterate through the scanned items and remove those that meet the criteria
            for item in response["Items"]:
                ttl = item.get("ttl")
                time_added = item.get("timestamp")

                if ttl is None or (time_added is not None and (ttl + time_added) < current_timestamp):
                    self.table.delete_item(Key={"uuid": item["uuid"]})
        except ClientError as err:
            logger.error(
                "Couldn't remove expired records. Here's why: %s: %s",
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise



    # snippet-start:[python.example_code.dynamodb.DescribeTable]
    def exists(self, table_name):
        """
        Determines whether a table exists. As a side effect, stores the table in
        a member variable.

        :param table_name: The name of the table to check.
        :return: True when the table exists; otherwise, False.
        """
        try:
            table = self.dyn_resource.Table(table_name)
            table.load()
            exists = True
        except ClientError as err:
            if err.response["Error"]["Code"] == "ResourceNotFoundException":
                exists = False
            else:
                logger.error(
                    "Couldn't check for existence of %s. Here's why: %s: %s",
                    table_name,
                    err.response["Error"]["Code"],
                    err.response["Error"]["Message"],
                )
                raise
        else:
            self.table = table
        return exists

    # snippet-end:[python.example_code.dynamodb.DescribeTable]

    # snippet-start:[python.example_code.dynamodb.CreateTable]
    def create_table(self, table_name):
        """
        Creates an Amazon DynamoDB table that can be used to store movie data.
        The table uses the release year of the movie as the partition key and the
        title as the sort key.

        :param table_name: The name of the table to create.
        :return: The newly created table.
        """
        try:
            self.table = self.dyn_resource.create_table(
                TableName=table_name,
                KeySchema=[
                    {"AttributeName": "year", "KeyType": "HASH"},  # Partition key
                    {"AttributeName": "title", "KeyType": "RANGE"},  # Sort key
                ],
                AttributeDefinitions=[
                    {"AttributeName": "year", "AttributeType": "N"},
                    {"AttributeName": "title", "AttributeType": "S"},
                ],
                ProvisionedThroughput={
                    "ReadCapacityUnits": 10,
                    "WriteCapacityUnits": 10,
                },
            )
            self.table.wait_until_exists()
        except ClientError as err:
            logger.error(
                "Couldn't create table %s. Here's why: %s: %s",
                table_name,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise
        else:
            return self.table

    # snippet-end:[python.example_code.dynamodb.CreateTable]

    # snippet-start:[python.example_code.dynamodb.ListTables]
    def list_tables(self):
        """
        Lists the Amazon DynamoDB tables for the current account.

        :return: The list of tables.
        """
        try:
            tables = []
            for table in self.dyn_resource.tables.all():
                print(table.name)
                tables.append(table)
        except ClientError as err:
            logger.error(
                "Couldn't list tables. Here's why: %s: %s",
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise
        else:
            return tables

    def write_news_articles(self, news_articles, batch_size):
        """
        Fills an Amazon DynamoDB table with the specified data, using batch writing for better performance.

        :param news_articles: The data to put in the table. Each item must contain at least
                    the keys required by the schema that was specified when the
                    table was created.
        """
        try:
            with self.table.batch_writer() as writer:
                for i in range(0, len(news_articles), batch_size):
                    batch = news_articles[i:i+batch_size]
                    for news_article in batch:
                        response = self.table.get_item(Key={"uuid": news_article["uuid"]})
                        if "Item" not in response:
                            news_article["timestamp"] = Decimal(str(time.mktime(datetime.now().timetuple())))
                            writer.put_item(Item=news_article)
        except ClientError as err:
            logger.error(
                "Couldn't load data into table using write_news_articles %s. Here's why: %s: %s",
                self.table.name,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise


    def add_news_article(self, news_article):
        """
        Adds a news article to the table if there is no existing record with the same uuid.

        :param news_article: Dictionary object containing news article data
        """
        # Adding timestamp to the news article
        news_article["timestamp"] = Decimal(str(time.mktime(datetime.now().timetuple())))

        try:
            # Check if a record with the same uuid already exists
            response = self.table.get_item(Key={"uuid": news_article["uuid"]})
            if response.get("Item"):
                logger.warning("Skipping addition of news article %s. Record with the same uuid already exists.", news_article["uuid"])
                return
            
            # If no existing record found, add the news article
            self.table.put_item(Item=news_article)
        except ClientError as err:
            logger.error(
                "Couldn't add news article %s to table %s. Here's why: %s: %s",
                news_article,
                self.table.name,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise

    # "uuid" is used as a unique field
    def get_news_article(self, uuid):
        """
        Gets news article from dynamoDB

        :param uuid: Unique value to identify the news article. 
        :return: News article data.
        """
        try:
            response = self.table.get_item(Key={"uuid": uuid})
        except ClientError as err:
            logger.error(
                "Couldn't get news article %s from table %s. Here's why: %s: %s",
                uuid,
                self.table.name,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise
        else:
            return response["Item"]


    # snippet-start:[python.example_code.dynamodb.UpdateItem.UpdateExpression]
    def update_movie(self, title, year, rating, plot):
        """
        Updates rating and plot data for a movie in the table.

        :param title: The title of the movie to update.
        :param year: The release year of the movie to update.
        :param rating: The updated rating to the give the movie.
        :param plot: The updated plot summary to give the movie.
        :return: The fields that were updated, with their new values.
        """
        try:
            response = self.table.update_item(
                Key={"year": year, "title": title},
                UpdateExpression="set info.rating=:r, info.plot=:p",
                ExpressionAttributeValues={":r": Decimal(str(rating)), ":p": plot},
                ReturnValues="UPDATED_NEW",
            )
        except ClientError as err:
            logger.error(
                "Couldn't update movie %s in table %s. Here's why: %s: %s",
                title,
                self.table.name,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise
        else:
            return response["Attributes"]

    # snippet-end:[python.example_code.dynamodb.UpdateItem.UpdateExpression]

    # snippet-start:[python.example_code.dynamodb.Query]
    def query_movies(self, year):
        """
        Queries for movies that were released in the specified year.

        :param year: The year to query.
        :return: The list of movies that were released in the specified year.
        """
        try:
            response = self.table.query(KeyConditionExpression=Key("year").eq(year))
        except ClientError as err:
            logger.error(
                "Couldn't query for movies released in %s. Here's why: %s: %s",
                year,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise
        else:
            return response["Items"]

    # snippet-end:[python.example_code.dynamodb.Query]

    # snippet-start:[python.example_code.dynamodb.Scan]
    def scan_movies(self, year_range):
        """
        Scans for movies that were released in a range of years.
        Uses a projection expression to return a subset of data for each movie.

        :param year_range: The range of years to retrieve.
        :return: The list of movies released in the specified years.
        """
        movies = []
        scan_kwargs = {
            "FilterExpression": Key("year").between(
                year_range["first"], year_range["second"]
            ),
            "ProjectionExpression": "#yr, title, info.rating",
            "ExpressionAttributeNames": {"#yr": "year"},
        }
        try:
            done = False
            start_key = None
            while not done:
                if start_key:
                    scan_kwargs["ExclusiveStartKey"] = start_key
                response = self.table.scan(**scan_kwargs)
                movies.extend(response.get("Items", []))
                start_key = response.get("LastEvaluatedKey", None)
                done = start_key is None
        except ClientError as err:
            logger.error(
                "Couldn't scan for movies. Here's why: %s: %s",
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise

        return movies

    # snippet-end:[python.example_code.dynamodb.Scan]

    # snippet-start:[python.example_code.dynamodb.DeleteItem]
    def delete_news_article(self, uuid):
        """
        Deletes a news article from the table.

        :param uuid: The uuid of the news article to delete.
        """
        try:
            self.table.delete_item(Key={"uuid": uuid})
        except ClientError as err:
            logger.error(
                "Couldn't delete news article %s. Here's why: %s: %s",
                uuid,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise

    # snippet-end:[python.example_code.dynamodb.DeleteItem]

    # snippet-start:[python.example_code.dynamodb.DeleteTable]
    def delete_table(self):
        """
        Deletes the table.
        """
        try:
            self.table.delete()
            self.table = None
        except ClientError as err:
            logger.error(
                "Couldn't delete table. Here's why: %s: %s",
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise

    # snippet-end:[python.example_code.dynamodb.DeleteTable]


# snippet-end:[python.example_code.dynamodb.helper.Movies.class_full]


# snippet-start:[python.example_code.dynamodb.helper.get_sample_movie_data]
def get_sample_movie_data(movie_file_name):
    """
    Gets sample movie data, either from a local file or by first downloading it from
    the Amazon DynamoDB developer guide.

    :param movie_file_name: The local file name where the movie data is stored in JSON format.
    :return: The movie data as a dict.
    """
    if not os.path.isfile(movie_file_name):
        print(f"Downloading {movie_file_name}...")
        movie_content = requests.get(
            "https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/samples/moviedata.zip"
        )
        movie_zip = ZipFile(BytesIO(movie_content.content))
        movie_zip.extractall()

    try:
        with open(movie_file_name) as movie_file:
            movie_data = json.load(movie_file, parse_float=Decimal)
    except FileNotFoundError:
        print(
            f"File {movie_file_name} not found. You must first download the file to "
            "run this demo. See the README for instructions."
        )
        raise
    else:
        # The sample file lists over 4000 movies, return only the first 250.
        return movie_data[:250]


# snippet-end:[python.example_code.dynamodb.helper.get_sample_movie_data]

    

# snippet-start:[python.example_code.dynamodb.Scenario_GettingStartedMovies]
def run_scenario(table_name, movie_file_name, dyn_resource):
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    print("-" * 88)
    print("Welcome to the Amazon DynamoDB getting started demo.")
    print("-" * 88)

    movies = Movies(dyn_resource)
    movies_exists = movies.exists(table_name)
    if not movies_exists:
        print(f"\nCreating table {table_name}...")
        movies.create_table(table_name)
        print(f"\nCreated table {movies.table.name}.")

    my_movie = Question.ask_questions(
        [
            Question(
                "title", "Enter the title of a movie you want to add to the table: "
            ),
            Question("year", "What year was it released? ", Question.is_int),
            Question(
                "rating",
                "On a scale of 1 - 10, how do you rate it? ",
                Question.is_float,
                Question.in_range(1, 10),
            ),
            Question("plot", "Summarize the plot for me: "),
        ]
    )
    movies.add_movie(**my_movie)
    print(f"\nAdded '{my_movie['title']}' to '{movies.table.name}'.")
    print("-" * 88)

    movie_update = Question.ask_questions(
        [
            Question(
                "rating",
                f"\nLet's update your movie.\nYou rated it {my_movie['rating']}, what new "
                f"rating would you give it? ",
                Question.is_float,
                Question.in_range(1, 10),
            ),
            Question(
                "plot",
                f"You summarized the plot as '{my_movie['plot']}'.\nWhat would you say now? ",
            ),
        ]
    )
    my_movie.update(movie_update)
    updated = movies.update_movie(**my_movie)
    print(f"\nUpdated '{my_movie['title']}' with new attributes:")
    pprint(updated)
    print("-" * 88)

    if not movies_exists:
        movie_data = get_sample_movie_data(movie_file_name)
        print(f"\nReading data from '{movie_file_name}' into your table.")
        movies.write_batch(movie_data)
        print(f"\nWrote {len(movie_data)} movies into {movies.table.name}.")
    print("-" * 88)

    title = "The Lord of the Rings: The Fellowship of the Ring"
    if Question.ask_question(
        f"Let's move on...do you want to get info about '{title}'? (y/n) ",
        Question.is_yesno,
    ):
        movie = movies.get_movie(title, 2001)
        print("\nHere's what I found:")
        pprint(movie)
    print("-" * 88)

    ask_for_year = True
    while ask_for_year:
        release_year = Question.ask_question(
            f"\nLet's get a list of movies released in a given year. Enter a year between "
            f"1972 and 2018: ",
            Question.is_int,
            Question.in_range(1972, 2018),
        )
        releases = movies.query_movies(release_year)
        if releases:
            print(f"There were {len(releases)} movies released in {release_year}:")
            for release in releases:
                print(f"\t{release['title']}")
            ask_for_year = False
        else:
            print(f"I don't know about any movies released in {release_year}!")
            ask_for_year = Question.ask_question(
                "Try another year? (y/n) ", Question.is_yesno
            )
    print("-" * 88)

    years = Question.ask_questions(
        [
            Question(
                "first",
                f"\nNow let's scan for movies released in a range of years. Enter a year: ",
                Question.is_int,
                Question.in_range(1972, 2018),
            ),
            Question(
                "second",
                "Now enter another year: ",
                Question.is_int,
                Question.in_range(1972, 2018),
            ),
        ]
    )
    releases = movies.scan_movies(years)
    if releases:
        count = Question.ask_question(
            f"\nFound {len(releases)} movies. How many do you want to see? ",
            Question.is_int,
            Question.in_range(1, len(releases)),
        )
        print(f"\nHere are your {count} movies:\n")
        pprint(releases[:count])
    else:
        print(
            f"I don't know about any movies released between {years['first']} "
            f"and {years['second']}."
        )
    print("-" * 88)

    if Question.ask_question(
        f"\nLet's remove your movie from the table. Do you want to remove "
        f"'{my_movie['title']}'? (y/n)",
        Question.is_yesno,
    ):
        movies.delete_movie(my_movie["title"], my_movie["year"])
        print(f"\nRemoved '{my_movie['title']}' from the table.")
    print("-" * 88)

    if Question.ask_question(f"\nDelete the table? (y/n) ", Question.is_yesno):
        movies.delete_table()
        print(f"Deleted {table_name}.")
    else:
        print(
            "Don't forget to delete the table when you're done or you might incur "
            "charges on your account."
        )

    print("\nThanks for watching!")
    print("-" * 88)



if __name__ == "__main__":
    try:
        logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
        html = fetch_html("https://www.foxnews.com/")
        #print(html)
        # @see https://www.crummy.com/software/BeautifulSoup/bs4/doc/
        soup = BeautifulSoup(html, features="html.parser")
        news_articles = get_article_containers(soup=soup, tag="article", parse_fn=foxnews_parse_article_content)
        news_articles_object = NewsArticles(dyn_resource=boto3.resource("dynamodb"), news_articles=news_articles)
        table = news_articles_object.dyn_resource.Table("NewsArticles")
        table.load()
        news_articles_object.table = table
        # def add_news_article(self, news_article):
        #i = 2
        #news_articles_object.add_news_article(news_articles[i])
        #print(news_articles[i]["uuid"])
        #news_article_from_dynamodb = news_articles_object.get_news_article(news_articles[i]["uuid"])
        news_articles_object.remove_dead_news_articles()
        news_articles_from_dynamodb = news_articles_object.write_news_articles(news_articles=news_articles, batch_size=25)
        print(news_articles_from_dynamodb)

        """
        run_scenario(
            "doc-example-table-movies", "moviedata.json", boto3.resource("dynamodb")
        )
        """
    except Exception as e:
        print(f"Something went wrong with the demo! Here's what: {e}")

# snippet-end:[python.example_code.dynamodb.Scenario_GettingStartedMovies]