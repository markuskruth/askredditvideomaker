import praw, textwrap, pyttsx3, cv2, wave, contextlib
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import VideoFileClip, concatenate_videoclips, vfx, afx, CompositeAudioClip, AudioFileClip, concatenate_audioclips

title = "Who had the biggest fall from grace in history?"
commentAmount = 10
def get_reddit_comments():
	reddit = praw.Reddit(client_id = "in1aJ1hJ6eIaibya1RcETg",
						client_secret = "PxJO-LFswr_NSrc0du9r473Y8zIUEA",
						username = "?????",
						password = "?????",
						user_agent = "chaichoiwoi")


	subreddit = reddit.subreddit("askreddit")
	
#################################################################
	top_posts = subreddit.top(time_filter="year",limit=100)
#################################################################

	for submission in top_posts:
		if submission.title == title:
			comments = submission.comments

			i = 0
			kommentit = []
			for comment in comments:
				if 100 < len(comment.body) < 630 and "https" not in comment.body:
					i+=1
					kommentit.append(comment.body)
				if i==commentAmount:
					break
			break

	return kommentit



def create_comment_imgs(kommentit):


	for i in range(len(kommentit)):
		if kommentit[i][-1] != ".":
			string = kommentit[i]+"."
			kommentit[i] = string

		if "\n" in kommentit[i]:
			kommentit[i] = kommentit[i].replace("\n"," ")



	img = Image.open("black1.png")

	d = ImageDraw.Draw(img)
	fnt = ImageFont.truetype("arialbd.ttf",40)


	filenames = []
	y = 130
	h = 70
	length_limit = 80
	nykyinen_line_length = 0
	for i in range(len(kommentit)):

		y = 130
		j_talteen = 0 #viimeisen lauseen loppukoordinaatti
		kerta = 0
		j_x = 0

		for j in range(len(kommentit[i])):
			if nykyinen_line_length >= length_limit:
				j_x = 0
				y += h
				nykyinen_line_length = 0

			#jos tulee piste vastaan, katkaistaan kommentti siitä
			if kommentit[i][j] == "." and j > j_talteen:


				kerta += 1
				temp_line = kommentit[i][j_talteen:j+1]

				d.text((120+(j_x*19), y), temp_line, font=fnt, fill=(200,200,200))

				y += h
				j_x = 0
				nykyinen_line_length = 0
				j_talteen = j+2

				filename = f"redditkuva{i}a{kerta}.png"
				img.save(filename)
				filenames.append(filename)

			#tai jos ei tule pistettä vastaan mutta yhden lauseen pituus ylittää rivin pituuden
			elif nykyinen_line_length + (j-j_talteen) > length_limit:
				temp_line = kommentit[i][j_talteen:j+1]
				

				a = 0
				try:
					while temp_line[-1] != " ":
						a += 1
						temp_line = kommentit[i][j_talteen:j+1-a]
				except:
					pass

				d.text((120+(j_x*17), y), temp_line, font=fnt, fill=(200,200,200))

				j_x += j-a - j_talteen
				j_talteen = j+1-a
				y += h
				nykyinen_line_length = 0
				j_x = 0

				
		
		img = Image.open("black1.png")
		d = ImageDraw.Draw(img)

	return filenames




def create_voiceover(kommentit):
	engine = pyttsx3.init()

	engine.setProperty('rate',150)
	engine.setProperty('volume',0.2)

	voices = engine.getProperty('voices')
	engine.setProperty('voice',voices[3].id)

	engine.save_to_file(title,"thumbvoice.mp3")

	filenames = []
	for i in range(len(kommentit)):
		filename = f"voiceover{i}.mp3"
		engine.save_to_file(kommentit[i], filename)
		engine.runAndWait()
		filenames.append(filename)

	return filenames


def create_thumb():

	filename = "thumb.png"

	with contextlib.closing(wave.open("thumbvoice.mp3",'r')) as f:
	    frames = f.getnframes()
	    rate = f.getframerate()
	    duration = frames / float(rate)

	fourcc = cv2.VideoWriter_fourcc(*"mp4v")
	frame = cv2.imread(filename)
	size = frame.shape

	video = cv2.VideoWriter("thumbnail.mp4",fourcc,(duration+2)**-1,(size[1],size[0]))


	img = cv2.imread(filename)
	video.write(img)

def create_video_from_img(audio_fnames, img_fnames, kommentit):

	filenames = []
	kohta = 0
	for i in range(len(audio_fnames)):

		with contextlib.closing(wave.open(audio_fnames[i],'r')) as f:
		    frames = f.getnframes()
		    rate = f.getframerate()
		    duration = frames / float(rate)



		osuudet = []
		last_j = 0
		for j in range(len(kommentit[i])):
			if kommentit[i][j] == "." and j-last_j >= 3:
				prosenttiosuus = j/len(kommentit[i])
				osuudet.append(prosenttiosuus)
				last_j = j

		osuudet[-1] = 1

		frame = cv2.imread(img_fnames[i])
		size = frame.shape
		fourcc = cv2.VideoWriter_fourcc(*"mp4v")


		full_dur = 0
		for j in range(len(osuudet)):

			filename = f"commentvid{i}a{j}.mp4"
			filenames.append(filename)

			if len(osuudet) == 1:
				(duration*osuudet[j]+2)**-1

			else:
				if j == 0:
					dur = (duration*osuudet[j])**-1

				else:
					if j == len(osuudet)-1:
						dur = (duration*(osuudet[j]-osuudet[j-1])+2)**-1

					else:
						dur = (duration*(osuudet[j]-osuudet[j-1]))**-1


			full_dur += dur**-1
			video = cv2.VideoWriter(filename,fourcc,dur,(size[1],size[0]))

			img = cv2.imread(img_fnames[kohta])
			kohta += 1
			video.write(img)

		#print("full_dur:",full_dur-2)
		#print("voice_dur:",duration)

		video.release()

	return filenames



def produce_final(vid_fnames,audio_fnames):

	clips_full = []
	audios_full = []

	thumb_clip = VideoFileClip("thumbnail.mp4")
	clips_full.append(thumb_clip)

	thumb_audio = AudioFileClip("thumbvoice.mp3")
	audios_full.append(thumb_audio)
	pause = AudioFileClip("pause1.mp3")
	audios_full.append(pause)

	for i in range(len(vid_fnames)):
		clip = VideoFileClip(vid_fnames[i])
		clips_full.append(clip)

	for i in range(len(audio_fnames)):
		audio = AudioFileClip(audio_fnames[i])
		audios_full.append(audio)

		pause = AudioFileClip("pause1.mp3")
		audios_full.append(pause)



	print(len(clips_full))
	combined = concatenate_videoclips(clips_full,method='compose')

	audio_final = concatenate_audioclips(audios_full)
	combined.audio = CompositeAudioClip([audio_final])

	combined.write_videofile("aafullvideo.mp4",fps=2)




####################################
#MAIN
####################################
def main():
	comments = get_reddit_comments()
	print("COMMENTS EXCTRACTED")
	img_fnames = create_comment_imgs(comments)
	print("CREATED IMAGES FROM COMMENTS")
	audio_fnames = create_voiceover(comments)
	print("DONE VOICEOVER")
	vid_fnames = create_video_from_img(audio_fnames, img_fnames, comments)
	print("CREATED VIDEOS FROM IMAGES")
	create_thumb()
	print("CREATED THUMBNAIL")
	produce_final(vid_fnames,audio_fnames)


if __name__ == "__main__":
	main()
