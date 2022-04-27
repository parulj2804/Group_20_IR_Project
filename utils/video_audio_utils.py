from __future__ import unicode_literals
import youtube_dl
import pandas as pd
import os
import moviepy.editor as mp
import speech_recognition as sr
from pydub import AudioSegment
from pydub.silence import split_on_silence
from apiclient.discovery import build
from urllib.error import HTTPError
import pafy
from pytube import YouTube
from .classifier_utils import Text_Classifier
from urllib.parse import urlparse
from urllib.parse import parse_qs
import logging
from datetime import datetime
import pytz

logging.basicConfig(filename='/var/www/hate_burst/hate_burst_logs.log', level=logging.DEBUG,format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
UTC = pytz.utc
IST = pytz.timezone('Asia/Kolkata')


class VideoAudioUtils:
    # url = "https://youtube.com/watch?v="+str(links_list[0])
    def __init__(self,):
        self.r = sr.Recognizer()
        self.downloads_path='uploads/'
        self.DEVELOPER_KEY = "AIzaSyAj9xVvndSfz7NNnDrmopVpUqhi9PEsIFY"
        self.YOUTUBE_API_SERVICE_NAME = "youtube"
        self.YOUTUBE_API_VERSION = "v3"
        self.youtube_object = build(self.YOUTUBE_API_SERVICE_NAME, self.YOUTUBE_API_VERSION,developerKey = self.DEVELOPER_KEY)
        self.project_path = '/var/www/hate_burst/'
        curr_time=str(datetime.now(IST))
        msg="[VideoAudioUtils] [Constructor] "+"Object Created"
        logging.info(msg+" | "+curr_time)

    def downloadVid(self,vid_url,ydl_opts = {}):
      '''
        Takes a Youtube Video Link and Downloads the Video
      '''
      curr_time=str(datetime.now(IST))
      msg="[VideoAudioUtils] [downloadVid] "+"Method Called"
      logging.info(msg+" | "+curr_time)
      msg="[VideoAudioUtils] [downloadVid] "+"Vid URL: "+str(vid_url)
      logging.info(msg+" | "+curr_time)
      with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
          ydl.download([vid_url])
          info = ydl.extract_info(vid_url, download=True)
          # curr_time=str(datetime.now(IST))
          # msg="[VideoAudioUtils] [downloadVid] "+"Vid Info: "+str(info)
          # logging.info(msg+" | "+curr_time)
          filename = ydl.prepare_filename(info)
          msg="[VideoAudioUtils] [downloadVid] "+"Filename: "+str(filename)
          logging.info(msg+" | "+curr_time)
        except:
          curr_time=str(datetime.now(IST))
          msg="[VideoAudioUtils] [downloadVid] "+"Failure"
          logging.error(msg+" | "+curr_time)
          return "Failure"
      return filename

    def vidtoAud(self,filename,dur,vid_id,foldername):
      curr_time=str(datetime.now(IST))
      msg="[VideoAudioUtils] [vidtoAud] "+"Method Called"
      logging.info(msg+" | "+curr_time)
      path = self.downloads_path + str(foldername) + '/' + str(filename)
      print(filename)
      print(os.getcwd())
      print("VidToAUdPath:",self.project_path+path)
      msg="[VideoAudioUtils] [vidtoAud] "+"Path: "+str(path)
      logging.debug(msg+" | "+curr_time)
      try:
        clip = mp.VideoFileClip(self.project_path+path)
        dur  = clip.duration
        clip = clip.subclip(0,int(dur))
      except Exception as e:
        print(e)
        curr_time=str(datetime.now(IST))
        msg="[VideoAudioUtils] [vidtoAud] Failure "+str(e)
        logging.error(msg+" | "+curr_time)
        return "Failure"
      aud_name = filename.split(".")
      clip.audio.write_audiofile(self.project_path+"uploads/audioDataset/"+str(vid_id) + ".wav")
      return "success"

    def get_text_from_audio(self,path,vid_id,audio_folder_name):
      curr_time=str(datetime.now(IST))
      msg="[VideoAudioUtils] [get_text_from_audio] "+"Method Called"
      logging.info(msg+" | "+curr_time)
      path=self.project_path+self.downloads_path+ str(audio_folder_name) + '/'  + path
      print("text from audio path",path)
      msg="[VideoAudioUtils] [get_text_from_audio] "+"Path: "+str(path)
      logging.info(msg+" | "+curr_time)
      if(os.path.isfile(path)):
        print("File Found")
        msg="[VideoAudioUtils] [get_text_from_audio] "+"File Found"
        logging.info(msg+" | "+curr_time)
        audio_sd = AudioSegment.from_wav(path)
        audio_chk = split_on_silence(audio_sd,min_silence_len = 500,silence_thresh = audio_sd.dBFS-14,keep_silence=500)
        folder_name = "sound-chks"
        if not os.path.isdir(self.project_path+self.downloads_path+folder_name):
            os.mkdir(self.project_path+self.downloads_path+folder_name)
        audio_text = ""
        for i, sound_chk in enumerate(audio_chk, start=1):
            chk_fname = os.path.join(self.project_path+self.downloads_path+folder_name, f"chunk{i}.wav")
            sound_chk.export(chk_fname, format="wav")
            with sr.AudioFile(chk_fname) as src:
                audio_sound = self.r.record(src)
                try:
                    sample_text = self.r.recognize_google(audio_sound)
                except Exception as e:
                    curr_time=str(datetime.now(IST))
                    msg="[VideoAudioUtils] [get_text_from_audio] UnknownValueError Error:"+str(e)
                    logging.info(msg+" | "+curr_time)
                    print("Error:", str(e))
                else:
                    sample_text = f"{sample_text.capitalize()}. "
                    audio_text += sample_text
        return audio_text

    def search_kwd_yt(self,query,foldername,audio_folder_name, max_results):
        curr_time=str(datetime.now(IST))
        msg="[VideoAudioUtils] [search_kwd_yt] "+"Method Called"
        logging.info(msg+" | "+curr_time)
        msg="[VideoAudioUtils] [search_kwd_yt] "+"Query: "+str(query)
        logging.info(msg+" | "+curr_time)
        msg="[VideoAudioUtils] [search_kwd_yt] "+"max_results: "+str(max_results)
        logging.info(msg+" | "+curr_time)
        videos_list = []
        links_list = []
        i= 0
        search_keyword = self.youtube_object.search().list(q = query,part = 'id, snippet',
                                                   maxResults = max_results,type='video',videoDuration='short',videoCaption='closedCaption').execute()
        results = search_keyword['items']
        for result in results:
            if result['id']['kind'] == "youtube#video":
                print(result)
                i= i+ 1
                try:
                    video = pafy.new("https://youtube.com/watch?v="+str(result["id"]["videoId"]))
                    dur = video.length
                    print(os.getcwd())
                    # dur = convert_YouTube_duration_to_seconds(result['id']['contentDetails']['duration'])
                    os.chdir(self.project_path+self.downloads_path+ str(foldername) + '/')
                except:
                    continue
                try:
                  temp_res =  self.downloadVid("https://youtube.com/watch?v="+str(result["id"]["videoId"]))
                  curr_time=str(datetime.now(IST))
                  msg="[VideoAudioUtils] [search_kwd_yt] "+"Variable Value temp_res="+str(temp_res)
                  logging.debug(msg+" | "+curr_time)
                  if temp_res == "Failure":
                    os.chdir('../../') #reverse
                    continue
                except HTTPError as e:
                  if e.code == 403:
                    curr_time=str(datetime.now(IST))
                    msg="[VideoAudioUtils] [search_kwd_yt] "+"HTTPError=403"
                    logging.error(msg+" | "+curr_time)
                    os.chdir('../../') #reverse
                    continue
                os.chdir('../../') #reverse

                # os.chdir('uploads/audioDataset/')
                print("HERE",os.getcwd())
                curr_time=str(datetime.now(IST))
                msg="[VideoAudioUtils] [search_kwd_yt] "+"Path for If else: "+self.project_path+self.downloads_path+ str(foldername) + '/' + str(temp_res)
                logging.info(msg+" | "+curr_time)
                if os.path.isfile(self.project_path+self.downloads_path+ str(foldername) + '/' + str(temp_res)):
                  curr_time=str(datetime.now(IST))
                  msg="[VideoAudioUtils] [search_kwd_yt] "+"File Found MP4"
                  logging.info(msg+" | "+curr_time)
                  res = self.vidtoAud(str(temp_res),dur,str(result["id"]["videoId"]),foldername)
                  if res == "Failure":
                    curr_time=str(datetime.now(IST))
                    msg="[VideoAudioUtils] [search_kwd_yt] "+"Failure after File Found"
                    logging.error(msg+" | "+curr_time)
                    # os.chdir('../../') #reverse
                    continue
                elif os.path.isfile(self.project_path+self.downloads_path+ str(foldername) + '/'+ str(temp_res)):
                  curr_time=str(datetime.now(IST))
                  msg="[VideoAudioUtils] [search_kwd_yt] "+"File Found MKV"
                  logging.info(msg+" | "+curr_time)
                  res = self.vidtoAud(str(temp_res),dur,str(result["id"]["videoId"]),foldername)
                  if res == "Failure":
                    # os.chdir('../../') #reverse
                    curr_time=str(datetime.now(IST))
                    msg="[VideoAudioUtils] [search_kwd_yt] "+"Failure after File Found"
                    logging.error(msg+" | "+curr_time)
                    continue
                elif os.path.isfile(self.project_path+self.downloads_path+str(foldername) + '/'+ str(temp_res)):
                  curr_time=str(datetime.now(IST))
                  msg="[VideoAudioUtils] [search_kwd_yt] "+"File Found WEBM"
                  logging.info(msg+" | "+curr_time)
                  res = self.vidtoAud(str(temp_res),dur,str(result["id"]["videoId"]),foldername)
                  if res == "Failure":
                    # os.chdir('../../') #reverse
                    curr_time=str(datetime.now(IST))
                    msg="[VideoAudioUtils] [search_kwd_yt] "+"Failure after File Found"
                    logging.error(msg+" | "+curr_time)
                    continue


                vid_text = self.get_text_from_audio(str(result["id"]["videoId"]) + '.wav',str(result["id"]["videoId"]),audio_folder_name)
                videos_list.append("%s; %s; %s; %s; %s" % (result["snippet"]["title"],
                                result["id"]["videoId"], result['snippet']['description'],
                                "https://youtube.com/watch?v="+str(result["id"]["videoId"]),vid_text))
                links_list.append( "https://youtube.com/watch?v="+str(result["id"]["videoId"]))
                curr_time=str(datetime.now(IST))
                msg="[VideoAudioUtils] [search_kwd_yt] "+"Function Completed"
                logging.error(msg+" | "+curr_time)
                # os.chdir('../../') #reverse
        return self.get_dataframe(videos_list)

    def download_youtube_vid(self,url):
        curr_time=str(datetime.now(IST))
        msg="[VideoAudioUtils] [download_youtube_vid] "+"Method Called"
        logging.info(msg+" | "+curr_time)
        msg="[VideoAudioUtils] [download_youtube_vid] "+"URL: "+str(url)
        logging.info(msg+" | "+curr_time)
        # TODO: Handle the INVALID URL CASE
        foldername='videoDataset'
        audio_folder_name='audioDataset'
        videos_list = []
        links_list = []
        try:
            video = pafy.new(url)
            dur = video.length
        except Exception as e :
            curr_time=str(datetime.now(IST))
            msg="[VideoAudioUtils] [download_youtube_vid] "+"Invalid URL: "+str(e)
            logging.info(msg+" | "+curr_time)
            return "Failure - Invalid URL"
        os.chdir(self.project_path +self.downloads_path+ str(foldername) + '/')

        try:
          temp_res =  self.downloadVid(url)
          curr_time=str(datetime.now(IST))
          msg="[VideoAudioUtils] [download_youtube_vid] "+"Variable Value temp_res="+str(temp_res)
          logging.debug(msg+" | "+curr_time)
          if temp_res == "Failure":
            os.chdir('../../') #reverse
            return temp_res
        except HTTPError as e:
          if e.code == 403:
            os.chdir('../../') #reverse
            return e
        os.chdir('../../') #reverse
        parsed_url = urlparse(url)
        videoId = parse_qs(parsed_url.query)['v'][0]

        # os.chdir('uploads/audioDataset/')
        print("HERE",videoId)
        print("HERE",self.downloads_path+ str(foldername) + '/' + temp_res.split('.')[0]+ ".mp4")
        print("HERE",temp_res.split('.')[0])
        curr_time=str(datetime.now(IST))
        msg="[VideoAudioUtils] [download_youtube_vid] "+"The Path: "+str(self.downloads_path+ str(foldername) + '/' + temp_res.split('.')[0])
        logging.info(msg+" | "+curr_time)
        if os.path.isfile(self.downloads_path+ str(foldername) + '/' + temp_res.split('.')[0] + ".mp4"):
          msg="[VideoAudioUtils] [download_youtube_vid] "+"File Found: MP4"
          logging.info(msg+" | "+curr_time)
          res = self.vidtoAud(temp_res.split('.')[0] + ".mp4",dur,str(videoId),foldername)
          if res == "Failure":
            # os.chdir('../../') #reverse
            return res
        elif os.path.isfile(self.downloads_path+ str(foldername) + '/'+ temp_res.split('.')[0] + ".mkv"):
          msg="[VideoAudioUtils] [download_youtube_vid] "+"File Found: MKV"
          logging.info(msg+" | "+curr_time)
          res = self.vidtoAud(temp_res.split('.')[0]  + ".mkv",dur,str(videoId),foldername)
          if res == "Failure":
            # os.chdir('../../') #reverse
            return res
        elif os.path.isfile(self.downloads_path+str(foldername) + '/'+ temp_res.split('.')[0]+ ".webm"):
          msg="[VideoAudioUtils] [download_youtube_vid] "+"File Found: WEBM"
          logging.info(msg+" | "+curr_time)
          res = self.vidtoAud(temp_res.split('.')[0] + ".webm",dur,str(videoId),foldername)
          if res == "Failure":
            # os.chdir('../../') #reverse
            return res

        vid_text = self.get_text_from_audio(str(videoId) + '.wav',str(videoId),audio_folder_name)
        videos_list.append("% s; % s; % s;" % (str(videoId),url,vid_text))
        links_list.append(url)
        # os.chdir('../../') #reverse
        return self.get_dataframe_single(videos_list)


    def get_dataframe_single(self,videos_list):
        curr_time=str(datetime.now(IST))
        msg="[VideoAudioUtils] [get_dataframe_single] "+"Method Called"
        logging.info(msg+" | "+curr_time)
        print("Videos:\n", "\n".join(videos_list), "\n")
        df1 = pd.DataFrame(data={"topic":videos_list})
        df1[['videoId','video_url','video_text']] = df1['topic'].str.split(";",2, expand=True)
        df1.drop(['topic'],axis=1,inplace=True)
        df1.drop_duplicates(inplace=True)
        return df1

    def get_dataframe(self,videos_list):
        curr_time=str(datetime.now(IST))
        msg="[VideoAudioUtils] [get_dataframe] "+"Method Called"
        logging.info(msg+" | "+curr_time)
        print("Videos:\n", "\n".join(videos_list), "\n")
        df1 = pd.DataFrame(data={"topic":videos_list})
        df1[['title', 'videoId','description','video_url','video_text']] = df1['topic'].str.split(";",4, expand=True)
        df1.drop(['topic'],axis=1,inplace=True)
        df1.drop_duplicates(inplace=True)
        return df1

    def classify_query(self,query,vid_count=3):
        curr_time=str(datetime.now(IST))
        msg="[VideoAudioUtils] [classify_query] "+"Method Called"
        logging.info(msg+" | "+curr_time)
        msg="[VideoAudioUtils] [classify_query] "+"Query: "+str(query)
        logging.info(msg+" | "+curr_time)
        result = self.search_kwd_yt(query,'videoDataset','audioDataset',vid_count)
        text_classifier = Text_Classifier()
        predictions = []
        for text in result['video_text']:
            predictions.append(text_classifier.predict(text))
        result['prediction']=predictions
        return result

    def classify_youtube_video(self,url):
        curr_time=str(datetime.now(IST))
        msg="[VideoAudioUtils] [classify_youtube_video] "+"Method Called"
        logging.info(msg+" | "+curr_time)
        result = self.download_youtube_vid(url)
        if type(result)==type('Failure - Invalid URL'):
            return result
        text_classifier = Text_Classifier()
        predictions = []
        print("RESULT",result)
        for text in result['video_text']:
            predictions.append(text_classifier.predict(text))
        result['prediction']=predictions
        return result

    def classify_audio(self,file_name):
        curr_time=str(datetime.now(IST))
        msg="[VideoAudioUtils] [classify_audio] "+"Method Called"
        logging.info(msg+" | "+curr_time)
        audio_folder_name='audio_files'
        text = self.get_text_from_audio(file_name,file_name,audio_folder_name)
        print(text)
        text_classifier = Text_Classifier()
        prediction = text_classifier.predict(text)
        return [text,prediction]

    def classify_video(self,file_name):
        curr_time=str(datetime.now(IST))
        msg="[VideoAudioUtils] [classify_video] "+"Method Called"
        logging.info(msg+" | "+curr_time)
        foldername='video_files'
        duration=None
        print("classify_video CWD",os.getcwd())
        res = self.vidtoAud(file_name,duration,file_name,foldername)
        if res == "Failure":
          return res

        audio_folder_name='audioDataset'
        text = self.get_text_from_audio(file_name+'.wav',file_name+'.wav',audio_folder_name)
        print(text)
        text_classifier = Text_Classifier()
        prediction = text_classifier.predict(text)
        return [text,prediction]
