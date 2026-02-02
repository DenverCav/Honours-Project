# This file was made as I wanted to have a way for Admin users to be able to upload official
# scores, but I didn't want to have it done in the database because it would be way more
# difficult. So I chose this lazy way of doing it instead.

ADMIN_IDS = ['1111777563233243327', '721233707570036747' '1455540739613134918', '1454249263705096192' '1454516646986256547', '331301632216268802', '348598263928061957', '1367787837981851740']
#Soki, Ace, Wang, Creative, TheDaved, Ros, Le_Glaude, my alt from Discord

def checkAdmin(discordID):
    return discordID in ADMIN_IDS