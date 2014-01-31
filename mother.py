from __future__ import print_function
import time
import config
import botconfig
import praw

#THE ACRONYM PL IS PERMALINK
#I Should have written it out, in hindsight

r = praw.Reddit(user_agent = botconfig.botUserAgentExplanation)

def loginToReddit():
	try:
		r.login( config.username, config.password)
	except praw.errors.NotLoggedIn:
		print("Bot couldn't log in, exiting")
		sys.exit(1)
	
def getLastCommentPLFromFile():
	try:
		saveFile = open(botconfig.botSaveFileLocation,'r')
	except IOError:
		return None
	commentPL = saveFile.read();
	saveFile.close()
	return commentPL

def setLastCommentPL(toSet):
	saveFile = open(botconfig.botSaveFileLocation,'w')
	print(toSet, file=saveFile, end="")

def waitToRefresh():
	time.sleep(botconfig.botWaitTimeInMinutes * 60)

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
		setLastCommentPL(submissionComment.permalink)

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
