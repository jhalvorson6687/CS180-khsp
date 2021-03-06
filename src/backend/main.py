import os
from Modules import ParseDataset
from Modules import SearchFeatures
from Modules import DatasetOperations
from Modules import AnalyticsFeatures
from Modules import ImportExport
from os import listdir
from os.path import isfile, join
from operator import itemgetter
from collections import OrderedDict

from flask import Flask
from flask import request
from flask_cors import CORS
from flask import jsonify

import time

import json

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
CORS(app)

filePath = os.path.abspath(os.path.dirname(os.path.abspath(__file__))) + "/Data/tmdb_movies.csv"
moviesData = ParseDataset.parseCSV(filePath)
topDirectors ={}
topActors={}

def timer(func):
    def timer(*args, **kwargs):
        start_time = time.time()
        item = func(*args, **kwargs)
        end_time = time.time()
        item = {'request_time':end_time - start_time,'data':item}
        print(func.__name__+" took --- %s seconds ---" % (end_time - start_time))
        return item
    return timer

@app.route('/headers', methods=['GET'])
def getData():
    response = {
        'id': 'text',
        #'imdb_id': 'text',
        #'popularity': 'numeric',
        'budget': 'numeric',
        'revenue': 'numeric',
        'original_title': 'text',
        'cast': 'text',
        #'homepage': 'text',
        #'director': 'text',
        #'tagline': 'text',
        #'keywords': 'text',
        'runtime': 'numeric',
        #'genres': 'text',
        #'production_companies': 'text',
        #'release_date': 'text',
        #'vote_count': 'numeric',
        #'vote_average': 'numeric',
        #'release_year': 'numeric',
        #'budget_adj': 'numeric',
        #'revenue_adj': 'numeric'
    }
    return jsonify(response)

@app.route('/searchNumeric', methods=['GET']) 
def search():

    #Get all the parameters from the URL string
    search_field = request.args.get('search_field')
    search_query = request.args.get('search_query')
    search_inequality = request.args.get('search_inequality')

    responseObject = SearchFeatures.fetchMoviesByNumericSearch(search_field,search_query, search_inequality, moviesData)
    return jsonify(responseObject)

@app.route('/searchText', methods=['GET'])
def searchText():

    #Get all the parameters from the URL string
    search_field = request.args.get('search_field')
    search_query = request.args.get('search_query')

    responseObject = SearchFeatures.fetchMoviesByTextSearch(search_field, search_query, moviesData)
    return jsonify(responseObject)

@app.route('/searchFlopMovies', methods=['GET'])
def FlopMovies():
    # Get all the parameters from the URL string
    search_year = request.args.get('search_year')
    responseObject = AnalyticsFeatures.searchFlopMovies(search_year, moviesData)
    return jsonify(responseObject)

@app.route('/highestGrossingMovie', methods=['GET'])
def grossMovie():
    # Get all the parameters from the URL string
    search_year = request.args.get('search_year')
    responseObject = AnalyticsFeatures.highestGrossingMovie(search_year, moviesData)
    return jsonify(responseObject)

@app.route('/highestGrossingDirector', methods=['GET'])
def grossDirector():
    # Get all the parameters from the URL string
    search_year = request.args.get('search_year')
    responseObject = SearchFeatures.highestGrossingDirector(search_year, moviesData)
    return jsonify(responseObject)

@app.route('/highestGrossingActorYear', methods=['GET'])
def highestPaidActor():
    # Get all the parameters from the URL string
    search_year = request.args.get('search_year')
    responseObject = SearchFeatures.highestGrossingActorYear(search_year, moviesData)
    return jsonify(responseObject)

@app.route('/insertData', methods =['POST'])
def insertData():
    data = request.data
    final_data = eval(data)
    global moviesData
    moviesData = DatasetOperations.insertMovie(final_data, moviesData)
    return jsonify({'message':'success'})

@app.route('/editData', methods =['POST'])
def editData():
    data = request.data
    new_data = eval(data)
    global moviesData
    moviesData = DatasetOperations.updateMovie(new_data, moviesData)
    return jsonify({'message':'update successful'})

@app.route('/deleteMovie', methods = ['POST'])
def deleteData():
    data = request.data
    global moviesData
    moviesData = DatasetOperations.deleteMovie(eval(data), moviesData)
    return jsonify({'message':'deleted successfully'})

@app.route('/aggregateMoviesBR', methods =['GET'])
def aggregateMovies():
    responseObject = AnalyticsFeatures.moviesAggregate(moviesData)
    return jsonify(responseObject)

@app.route('/analyticsGrenre', methods =['GET'])
def analyticsGenre():
    search_year = request.args.get('search_year')
    responseObject = AnalyticsFeatures.analyticsGrenre(search_year, moviesData)
    return jsonify(responseObject)


@app.route('/importData', methods =['GET'])
def importData():
    start_time = time.time()
    #data = request.data
    file_name = request.args.get('file_name')
    global moviesData
    moviesData = ImportExport.importData(file_name)
    end_time = time.time()
    return jsonify({'request_time':end_time-start_time,'status':'Imported data'})

@app.route('/exportData', methods =['GET'])
def exportData():
    file_name = request.args.get('file_name')
    response = ImportExport.exportData(file_name, moviesData)
    return jsonify({'request_time':response['request_time'], 'status':'Exported data'})

# @app.route('/popularityBubble', methods =['GET'])
# def popularityBubble():
#     year = request.args.get('year')
#     response = AnalyticsFeatures.analyticsPopularity(year, moviesData)
#     return jsonify(response)


@app.route('/exportList', methods =['GET'])
@timer
def exportList():
    filepath = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "\\backend\\Data\\"
    #onlyfiles = [{f:f} for f in listdir(filepath) if isfile(join(filepath,f))]
    resObject = {}
    for file in listdir(filepath):
        if isfile(join(filepath, file)):
                resObject[file]=file

    print(resObject)


    return resObject

def getTopPerson():
    global topDirectors
    global topActors
    for movie in moviesData:
        director = movie['director']
        if director in topDirectors:
            if director != '':
                count = topDirectors.get(director)
                topDirectors.update({director:count+1})
        else:
            topDirectors.update({director:1})

        actorList = movie['cast']
        for actor in actorList:
            if actor in topActors:
                if actor != '':
                    count = topActors.get(actor)
                    topActors.update({actor:count+1})
            else:
                topActors.update({actor:1})

@app.route('/getTopDirectors', methods =['GET'])
def topDirector():
    start_time = time.time()
    global topDirectors
    topDirectors = sorted(topDirectors.items(), key=lambda x: x[1], reverse=True)
    topDirectors = dict((topDirectors)[0: 10])
    end_time = time.time()
    return jsonify({'request_time':(end_time-start_time),'data':topDirectors})

@app.route('/getTopActors', methods =['GET'])
def topActor():
    start_time = time.time()
    global topActors
    topActors = sorted(topActors.items(), key=lambda x: x[1], reverse=True)
    topActors = dict((topActors)[0: 10])
    end_time = time.time()
    return jsonify({'request_time':(end_time-start_time),'data':topActors})

@app.route('/actorGenres', methods =['GET'])
def actorGenres():
    search_actor = request.args.get('search_actor')
    responseObject = AnalyticsFeatures.actorGenres(search_actor, moviesData)
    return jsonify(responseObject)

@app.route('/directorGenres', methods =['GET'])
def directorGenres():
    search_director = request.args.get('search_director')
    responseObject = AnalyticsFeatures.directorGenres(search_director, moviesData)
    return jsonify(responseObject)

@app.route('/ActorTrajectory', methods =['GET'])
def getActorTrajectory():
    actor = request.args.get('actor')
    response = AnalyticsFeatures.actorTrajectory(actor, moviesData)
    return jsonify(response)

@app.route('/DirectorTrajectory', methods =['GET'])
def getDirectorTrajectory():
    director = request.args.get('director')
    response = AnalyticsFeatures.directorTrajectory(director, moviesData)
    return jsonify(response)

getTopPerson()

if __name__ == '__main__':
    app.run()

