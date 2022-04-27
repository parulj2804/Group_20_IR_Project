from flask import Flask, render_template, url_for, request, jsonify,redirect
from utils.twitter_utils import Twitter_Utils
from utils.classifier_utils import Text_Classifier, Text_Classifier_Hindi
from utils.video_audio_utils import VideoAudioUtils
import pandas as pd
from collections import Counter
from datetime import datetime
import pytz
from werkzeug.utils import secure_filename
import os
import logging
from werkzeug.debug import DebuggedApplication 


UTC = pytz.utc
IST = pytz.timezone('Asia/Kolkata')
logging.basicConfig(filename='/var/www/hate_burst/hate_burst_logs.log', level=logging.DEBUG,format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')


app = Flask(__name__)
UPLOAD_FOLDER = '/var/www/hate_burst/uploads/audio_files'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

UPLOAD_FOLDER_VIDEO = '/var/www/hate_burst/uploads/video_files'
app.config['UPLOAD_FOLDER_VIDEO'] = UPLOAD_FOLDER_VIDEO

app.debug = True
application = DebuggedApplication(app, True)

@app.route('/',methods=['GET',])
def index():
    '''
        Returns the Home Page.
    '''
    curr_time=str(datetime.now(IST))
    logging.info("[Web] Website Home Opened | "+curr_time)
    return render_template('index.html')

@app.route('/services',methods=['GET',])
def services_page():
    curr_time=str(datetime.now(IST))
    logging.info("[Web] Website Services Opened | "+curr_time)
    return render_template('services_home.html')


@app.route('/twitter_user_analytics',methods=['GET',])
def service_twitter_user_analytics():
    curr_time=str(datetime.now(IST))
    logging.info("[Web] [Twitter User Analytics] Opened"+" | "+curr_time)
    stats = {}
    stats['counts_pos']=0
    stats['counts_neg']=0
    stats['tweet_count']=0
    stats['average_likes_hate']=0
    stats['average_likes_no_hate']=0
    stats['hashtags_hate']=None
    stats['most_common_words_hate']=None
    stats['most_common_locations']=None
    stats['dataframe']=None
    return render_template('service_twitter_user_analytics.html',user_tweets=stats,empty=True)

@app.route('/service_get_user_tweets',methods=['POST','GET'])
def service_get_user_tweets():
    '''
        It takes in the twitter username by POST and return the list of tweets by that user.
        If accessed via GET, redirects to home page.
    '''
    if request.method=='POST':
        user_id=request.form.get("user_id")
        twitter_utils_obj = Twitter_Utils()
        user_tweets = twitter_utils_obj.get_user_tweets(user_id)
        curr_time=str(datetime.now(IST))
        logging.debug("[Web] [Twitter User Analytics] "+"Username:"+user_id+" | "+curr_time)
        if user_tweets=="invalid username":
            return render_template('error_generic.html',error="Username Doesn't Exists")
        return render_template('service_twitter_user_analytics.html',user_tweets=user_tweets,empty=False)
    else:
        return render_template('index.html')

@app.route('/service_get_trending_tweets',methods=['POST','GET'])
def service_get_trending_tweets():
    '''
        Function Description
    '''
    if request.method=='POST':
        hashtag=request.form.get("hashtag")
        if hashtag=='btn_submit_trend':
            hashtag=request.form["hashtag_input"]
        date=request.form.get("start_date")
        count_tweets=int(request.form.get("count_tweets"))
        curr_time=str(datetime.now(IST))
        msg="[Web] [Twitter Trends Analytics]"+" Trend:"+hashtag+" Date:"+date+" Tweet Count:"+str(count_tweets)
        logging.info(msg+" | "+curr_time)
        twitter_utils_obj = Twitter_Utils()
        trending = twitter_utils_obj.get_trending()
        user_tweets = twitter_utils_obj.get_trending_tweets(hashtag,date,count_tweets)
        print(user_tweets)
        return render_template('service_twitter_trends_analytics.html',user_tweets=user_tweets,trending=trending,empty=False)
    else:
        return render_template('index.html')

@app.route('/service_classify_text',methods=['POST',])
def service_classify_text():
    query=request.form.get("query_text")
    lang=request.form.get("lang")
    print("LANG",lang,"\n\n\n\n\n\n\n\n\n\n\n",query)
    curr_time=str(datetime.now(IST))
    msg="[Web] [Classify Text]"+"Query: "+query+" Language:"+lang
    logging.debug(msg+" | "+curr_time)
    prediction=None
    if lang=='hi':
        text_classifier = Text_Classifier_Hindi()
        prediction = text_classifier.predict(query)
    else:
        text_classifier = Text_Classifier()
        prediction = text_classifier.predict(query)
    return render_template('generic_result.html',result=prediction)

@app.route('/upload_audio',methods = ['GET','POST'])
def upload_file():
    if request.method =='POST':
        file = request.files['query_audio']
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
            va_utils = VideoAudioUtils()
            prediction=va_utils.classify_audio(filename)
            print(prediction)
            return render_template('audio_result.html',prediction=prediction)
    return render_template('services_base.html')

@app.route('/upload_video',methods = ['GET','POST'])
def upload_video():
    if request.method =='POST':
        file = request.files['query_video']
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER_VIDEO'],filename))
            va_utils = VideoAudioUtils()
            prediction=va_utils.classify_video(filename)
            print(prediction)
            return render_template('video_result.html',prediction=prediction,type='video_result')
    return render_template('services_home.html')


@app.route('/analyze_youtube_query',methods = ['GET','POST'])
def analyze_youtube_query():
    if request.method =='POST':
        query=request.form.get("query_video")
        count_results=int(request.form.get("count_results"))
        if count_results<1:
            return render_template('error_generic.html',error="Invalid Count of Results")
        va_utils = VideoAudioUtils()
        result = va_utils.classify_query(query,count_results)
        return render_template('video_result.html',result=result,type="query_result")
    return render_template('services_home.html')


@app.route('/analyze_youtube_video',methods = ['GET','POST'])
def analyze_youtube_video():
    if request.method =='POST':
        url=request.form.get("query_video")
        va_utils = VideoAudioUtils()
        result = va_utils.classify_youtube_video(url)
        if type(result) == type('str'):
            return render_template('error_generic.html',error='Invalid URL')
        return render_template('video_result.html',result=result,type="youtube_video_result")
    return render_template('services_home.html')


@app.route('/api/service_classify_text',methods=['GET',])
def api_service_classify_text():
    query=request.args.get("query")
    curr_time=str(datetime.now(IST))
    msg="[API] [Classify Text]"+"Query: "+query
    logging.debug(msg+" | "+curr_time)
    if query==None or query=="":
        return jsonify({"response_code":901,"response_status":"No argument provided"}) # 901 : No argument provided
    text_classifier = Text_Classifier()
    prediction = text_classifier.predict(query)
    return jsonify({"prediction":prediction,"response_code":900,"response_status":"OK"}) #900: OK


@app.route('/api/twitter_user_analytics/<string:attribute>',methods=['GET',])
def api_twitter_user_analytics(attribute):
    username=request.args.get("username")
    import os
    print(os.getcwd())
    msg="[API] [Twitter User Analytics]"+" Attribute:"+attribute+" Username:"+username
    curr_time=str(datetime.now(IST))
    logging.debug(msg+" | "+curr_time)
    if username==None or username=="":
        return jsonify({"response_code":901,"response_status":"No argument provided"}) # 901 : No argument provided
    twitter_utils_obj = Twitter_Utils()
    user_tweets = twitter_utils_obj.get_user_tweets(username)
    if user_tweets=="invalid username":
        return jsonify({"response_code":902,"response_status":"Username Doesn't Exists"}) # 902 : Username Doesn't Exists
    if attribute=='counts_pos':
        return jsonify({"counts_pos":user_tweets['counts_pos'],"response_code":900,"response_status":"OK"}) #900: OK
    if attribute=='counts_neg':
        return jsonify({"counts_neg":user_tweets['counts_neg'],"response_code":900,"response_status":"OK"}) #900: OK
    if attribute=='tweet_count':
        return jsonify({"tweet_count":user_tweets['tweet_count'],"response_code":900,"response_status":"OK"}) #900: OK
    if attribute=='average_likes_hate':
        return jsonify({"average_likes_hate":user_tweets['average_likes_hate'],"response_code":900,"response_status":"OK"}) #900: OK
    if attribute=='average_likes_no_hate':
        return jsonify({"average_likes_no_hate":user_tweets['average_likes_no_hate'],"response_code":900,"response_status":"OK"}) #900: OK
    if attribute=='hashtags_hate':
        return jsonify({"hashtags_hate":user_tweets['hashtags_hate'],"response_code":900,"response_status":"OK"}) #900: OK
    if attribute=='most_common_words_hate':
        return jsonify({"most_common_words_hate":user_tweets['most_common_words_hate'],"response_code":900,"response_status":"OK"}) #900: OK
    if attribute=='most_common_locations':
        return jsonify({"most_common_locations":user_tweets['most_common_locations'],"response_code":900,"response_status":"OK"}) #900: OK
    if attribute=='dataframe':
        return jsonify({"dataframe":user_tweets['dataframe'],"response_code":900,"response_status":"OK"}) #900: OK
    else:
        return jsonify({"response_code":903,"response_status":"Invalid Attribute"}) # 903 : Invalid Attribute

@app.route('/api/twitter_trends_analytics/<string:attribute>',methods=['GET',])
def api_twitter_trends_analytics(attribute):
    trend=request.args.get("trend")
    if trend==None or trend=="":
        return jsonify({"response_code":901,"response_status":"No argument provided"}) # 901 : No argument provided
    date=request.args.get("date")
    if date==None or date=="":
        return jsonify({"response_code":904,"response_status":"Date Argument Missing"}) # 904 : Date Argument Missing
    try:
        count_tweets=count_tweets.replace('"','')
        count_tweets=count_tweets.replace("'","")
        count_tweets=int(request.args.get("count_tweets"))
        if count_tweets==None or count_tweets=="":
            return jsonify({"response_code":905,"response_status":"Tweet Count Argument Missing"}) # 905 : Tweet Count Argument Missing
        if count_tweets<1:
            return jsonify({"response_code":906,"response_status":"Tweet Count Invalid"}) # 906 : Tweet Count Invalid
    except:
        return jsonify({"response_code":906,"response_status":"Tweet Count Invalid"}) # 906 : Tweet Count Invalid

    twitter_utils_obj = Twitter_Utils()
    user_tweets = twitter_utils_obj.get_trending_tweets(trend,date,count_tweets)
    curr_time=str(datetime.now(IST))
    msg="[API] [Twitter Trends Analytics]"+" Attribute:"+attribute+" Trend:"+trend+" Date:"+date+" Tweet Count:"+str(count_tweets)
    logging.debug(msg+" | "+curr_time)
    if attribute=='counts_pos':
        return jsonify({"counts_pos":user_tweets['counts_pos'],"response_code":900,"response_status":"OK"}) #900: OK
    if attribute=='counts_neg':
        return jsonify({"counts_neg":user_tweets['counts_neg'],"response_code":900,"response_status":"OK"}) #900: OK
    if attribute=='tweet_count':
        return jsonify({"tweet_count":user_tweets['tweet_count'],"response_code":900,"response_status":"OK"}) #900: OK
    if attribute=='average_likes_hate':
        return jsonify({"average_likes_hate":user_tweets['average_likes_hate'],"response_code":900,"response_status":"OK"}) #900: OK
    if attribute=='average_likes_no_hate':
        return jsonify({"average_likes_no_hate":user_tweets['average_likes_no_hate'],"response_code":900,"response_status":"OK"}) #900: OK
    if attribute=='hashtags_hate':
        return jsonify({"hashtags_hate":user_tweets['hashtags_hate'],"response_code":900,"response_status":"OK"}) #900: OK
    if attribute=='most_common_words_hate':
        return jsonify({"most_common_words_hate":user_tweets['most_common_words_hate'],"response_code":900,"response_status":"OK"}) #900: OK
    if attribute=='most_common_locations':
        return jsonify({"most_common_locations":user_tweets['most_common_locations'],"response_code":900,"response_status":"OK"}) #900: OK
    if attribute=='dataframe':
        return jsonify({"dataframe":user_tweets['dataframe'],"response_code":900,"response_status":"OK"}) #900: OK
    else:
        return jsonify({"response_code":903,"response_status":"Invalid Attribute"}) # 903 : Invalid Attribute


@app.route('/twitter_trends_analytics',methods=['GET',])
def service_twitter_trends_analytics():
    twitter_utils = Twitter_Utils()
    trending = twitter_utils.get_trending()
    return render_template('service_twitter_trends_analytics.html',trending=trending,empty=True)

@app.route('/hate_check',methods=['GET',])
def service_hate_check():
    curr_time=str(datetime.now(IST))
    logging.info("[Web] Website Hate Check Opened | "+curr_time)
    return render_template('service_hate_check.html')

@app.route('/apis',methods=['GET',])
def apis():
    curr_time=str(datetime.now(IST))
    logging.info("[Web] Website APIs Opened | "+curr_time)
    return render_template('service_apis.html')

@app.errorhandler(404)
def page_not_found(e):
    curr_time=str(datetime.now(IST))
#    logging.info("[Web] Website Page Not Found Opened | "+curr_time)
    return render_template('error_page_not_found.html'), 404


if __name__ == '__main__':
    app.register_error_handler(404, page_not_found)
    # app.run(debug=True,host=0.0.0.0,port=5000)
    app.run(debug=True)
