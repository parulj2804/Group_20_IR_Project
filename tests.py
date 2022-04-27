from utils.video_audio_utils import VideoAudioUtils
from utils.classifier_utils import Text_Classifier, Text_Classifier_Hindi

# tc=Text_Classifier()

va_utils = VideoAudioUtils()
print(va_utils.classify_query('sexy',3))
# print(va_utils.classify_youtube_video('https://www.youtube.com/watch?v=hoNb6HuNmU0'))
# print(va_utils.classify_video('30 Second Explainer Videos-JzPfMbG1vrE.mp4'))
# print(va_utils.classify_youtube_video('https://www.youtube.com/watch?v=zhWDdy_5v2w'))
