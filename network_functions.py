'''
NETWORK ANALYSIS COURSEWORK 2 FUNCTIONS
========================================

Author: Jack Humble
Email: jack.humble@kcl.ac.uk
Date: 01/04/2019

This document contains functions creating the networks for the project as well
as the functions needed for the recommender system.
'''

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from itertools import compress
import random

def create_interaction_dataframe(csvFile, fileName, networkType = "colocation"):
    
    '''
    Contains the code for creating an interaction dataframe from the Foursquare kaggle 
    dataset (https://www.kaggle.com/chetanism/foursquare-nyc-and-tokyo-checkin-dataset/). 
    The returned interaction dataframe can be either a network of colocation or taste. 
    The returned dataframe is directly analysable by networkx using:

    nx.from_pandas_edgelist(interaction_df,
                             source=0,
                             target=1)

    Parameters
    ----------
    csvFile : pandas.DataFrame (required)
        pandas dataframe containing the desired rows from the Foursquare checkins dataset
    fileName : string (required)
        path to csv file in which csv will be written
    networkType : string ("colocation" or "taste") (optional)
        The type of network which will be created

    Returns
    -------
    interaction_df : pandas.DataFrame
        DataFrame containing interaction edges of user network
        source = integer 0
        target = integer 1
    '''
    
    # network types
    networkTypes = ["colocation", "taste"]
    
    # network type must be colocation of taste
    if networkType not in networkTypes:
        raise ValueError("Invalid network type. Expected one of: %s" % networkTypes)
        
    # networkType dictionary
    net_dict = {"colocation" : "venueId", "taste" : "venueCateg"}
    
    # Initialise list of list of venues/types each user has been to
    venuePerUser = []
    users = set(csvFile["userId"])
    
    # Create list of list of venues/types each user has been to
    for user in users:
        venuePerUser.append(csvFile[net_dict.get(networkType)].loc[csvFile["userId"] == user])

    # initialise interaction dataframe for colocation network
    intdf = []
    
    print("creating interaction dataframe...")
    # create colocation network
    for idx, user in enumerate(users):
        for tidx, targetUser in enumerate(users):
            # If users share at least one venue, add edge between them
            if (np.isin(venuePerUser[idx - 1], venuePerUser[tidx - 1]).sum() > 0) and (user != targetUser):
                intdf.append([user, targetUser])
        # primitive loading bar
        if user % 100 == 0:
             print("-", end = "")
    
    # turn into pandas dataframe
    intdf2 = pd.DataFrame(intdf)
    
    # remove opposite interactions as network is undirected
    frozen = {frozenset(x) for x in intdf}
    
    unique_intdf = [list(x) for x in frozen]
    
    # turn into pandas dataframe
    unique_intdf = pd.DataFrame(unique_intdf)
    
    print("")
    print("writing csv...")
    unique_intdf.to_csv("interaction_dataframes/" + fileName + ".csv")
    print("csv file created")
    
    return unique_intdf


def most_similar_node(specific_user):
    
    '''
    Contains code using data from the Foursquare kaggle dataset 
    (https://www.kaggle.com/chetanism/foursquare-nyc-and-tokyo-checkin-dataset/). 
    The returned dataframe contains the top most similar users to a specified user. 
    
    Parameters
    ----------
    specific_user : integer (required)
        a specific userId to find a list of most similar users   

    Returns
    -------
    interaction_df : pandas.DataFrame
        DataFrame containing interaction edges of user network
        user = integer 
        number_overlap = integer 
        percentage_overlap = double
    '''
    
    # Read in nyc file
    nyc = pd.read_csv("/Users/jackhumble/Documents/KingsCollege/Network_Analysis/Coursework2/data/dataset_TSMC2014_NYC.csv")
    
    #print(nyc.head())
    # Obtain all the venues specified each node has been to
    # Initialise list of list of venues/types each user has been to
    venuePerUser = []
    users = set(nyc["userId"])
    #print(users)
    # Create list of list of venue types each user has been to
    for user in users:
        venuePerUser.append(nyc["venueCategoryId"].loc[nyc["userId"] == user])
    
    overlap = []
    # for specified node, which node overlaps the most
    for targetUser in users:
            overlap.append([targetUser, np.isin(venuePerUser[specific_user - 1], venuePerUser[targetUser - 1]).sum()])
    
    overlap = pd.DataFrame(overlap)
    overlap = overlap.sort_values([1], ascending = False)
    
    # Express overlap as a percentage similarity
    overlap["percentage_overlap"] = round((overlap[1]/overlap.iloc[0][1]) * 100, 2)
    overlap.columns = ["user", "number_overlap", "percentage_overlap"]
    overlap = overlap.reset_index(drop = True)
    
    return overlap


def venue_recommendation(specific_user, no_of_venues_to_return = 5):
    
    '''
    This contains code which recommends a list of 5 venue ID's to a specified user based on
    the users with the most similar taste. 

    Parameters
    ----------
    specific_user : integer (required)
        a specific user to recommend a list of five venues. 
    no_of_venues_to_return : integer (optional)
        the number of recommended venues to return
        
    Returns
    -------
    venue_recommendation : list
        list of five venues for a specfied user.
    '''
    
    # Extract a table of most similar users
    data = most_similar_node(specific_user)
    
    # Extract most similar user
    most_similar_user = data.iloc[1:2, 0]
    
    # Read in nyc file
    nyc = pd.read_csv("/Users/jackhumble/Documents/KingsCollege/Network_Analysis/Coursework2/data/dataset_TSMC2014_NYC.csv")
    
    # Obtain all the venues specified each node has been to
    # Initialise list of list of venues/types each user has been to
    venuePerUser = []
    users = set(nyc["userId"])
    #print(users)
    # Create list of list of venue types each user has been to
    for user in users:
        venuePerUser.append(nyc["venueCategoryId"].loc[nyc["userId"] == user])
    
    # Get venues for each user
    specific_user_venues = venuePerUser[specific_user]
    similar_user_venues = venuePerUser[int(most_similar_user)]
    
    # find venues in similar_user that are not in specific_user
    difference = np.isin(similar_user_venues, specific_user, invert=True)
    
    # return these venues
    return list(compress(similar_user_venues, difference))[0:no_of_venues_to_return]


