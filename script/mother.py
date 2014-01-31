from __future__ import print_function
import sys, os, time, praw, re, hashlib
sys.path.append(os.path.realpath('config_files'))
import config_files.config as config, config_files.botconfig as botconfig

#THE ACRONYM PL IS PERMALINK
#I Should have written it out, in hindsight

r = praw.Reddit(user_agent = botconfig.botUserAgentExplanation)

def loginToReddit():
	try:
		r.login( config.username, config.password)
	except praw.errors.NotLoggedIn:
		print("Bot couldn't log in, exiting")
		sys.exit(1)
	
#the format of the data is 'Permalink CommentHash'
def getStringAtIndexFromSaveFile(index):
	try:
		saveFile = open(botconfig.botSaveFileLocation,'r')
	except IOError:
		print("SaveFile not found")
		return None
	fileData = saveFile.read()
	#this is a sanity check
	if re.match('\S+\s\S+', fileData) == None:
		print("MalformatedData in saveFile")
		return None
	saveFile.close()
	return string.split(saveFileString,' ')[index]

def getLastCommentPLFromFile():
	return getStringAtIndexFromSaveFile(0)

def getHashOfLastPostedCommentFromFile():
	return getStringAtIndexFromSaveFile(1)

def saveLastCommentPLAndCommentHash(permalink, commentHash):
	saveFile = open(botconfig.botSaveFileLocation,'w')
	print(permalink + " " + commentHash, file=saveFile, end="")

def waitToRefresh():
	time.sleep(botconfig.botWaitTimeInMinutes * 60)

def getHashOfAboutMe():
	return hashlib.sha224(config.aboutMe).hexdigest()

def isAboutMeTheNewestSubmission():
	redditor = r.get_redditor(config.username)
	comments = redditor.get_comments(limit=1)
	submitted = redditor.get_submitted(limit=1)
	for comment in comments:
		commentTime = comment.created_utc
		commentPL = comment.permalink
	for submission in submitted:
		submissionTime = submission.created_utc
	if submissionTime!=None and commentTime!=None and commentTime<submissionTime:
		return False
	if getHashOfLastPostedCommentFromFile() != getHashOfAboutMe():
		return False
	if commentPL!=None and commentPL==getLastCommentPLFromFile():
		return True
	return False

def deleteAboutMe():
	if(getLastCommentPLFromFile()!=None):
		try:
			commentToDelete = r.get_submission(getLastCommentPLFromFile()).comments[0]
			commentToDelete.delete()
		except IndexError:
			print("older aboutMe comment not found, ignoring")

def makeAboutMeTheNewestComment():
		submissionToCommentOn = r.get_submission(config.submissionPermaLink)
		submissionComment = submissionToCommentOn.add_comment(config.aboutMe)
		saveLastCommentPLAndCommentHash(submissionComment.permalink, getHashOfAboutMe())

def init():
	print('Starting bot..')
	loginToReddit()
	while True:
		if isAboutMeTheNewestSubmission() == False :
			print("AboutMe isn't the newest comment")
			deleteAboutMe()
			makeAboutMeTheNewestComment()
		waitToRefresh()

def tick():
	loginToReddit()
	if isAboutMeTheNewestSubmission() == False :
		deleteAboutMe()
		makeAboutMeTheNewestComment()
