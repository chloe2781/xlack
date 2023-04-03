# xlack
### Messaging app connected to PostgreSQL database management system.

The way to interact with our application is by operating as the “user” who joins workspaces in order to communicate with other users. 



## Features
#### NOTE: we included everything that was specified in our proposal. New features are marked in bold.

***NEW FEATURE**: sign-in* \
We included an initial sign-in page of our web application that lets a user sign-in using their email address. Once the user is ready, they hit the next button, which will either direct them to the workspace dashboard if they already are an existing user, or the sign up page if they are not.

*FEATURE: sign-up* \
If a new user would like to set up their account, they can type their email address into the sign-in page, and we will check to ensure we don’t have a user stored with that email address yet. If yes, they are an existing user, and we redirect them to their dashboard page with all the workspaces they have already joined. If not, then we redirect them to a sign-up page, where we show the input email, and they can input their name and date of birth to finish creating their profile. When they hit the submit button, we will redirect them to their workspace dashboard; or if their date of birth was not valid (i.e. dob >= '1923-01-01' AND dob <= '2014-01-01'), we display a message indicating that the date of birth was not valid, to preserve our constraints in SQL and not crash the server. They may then try again with a different date of birth, or they may hit the back button to go back to the sign-in page. 

*FEATURE: workspace dashboard* \
On the workspace dashboard, we retrieve all of the workspaces saved for the current user’s account and display them on the dashboard. From here, we can either click on any of the workspaces that a user has joined (if they exist), or we can hit the “+” button to bring us to a join-workspace menu.  

*FEATURE: join-workspace menu* \
From this menu, a user can create, and therefore join, a new workspace (which does not need to have a unique name). They will thus be the owner of that workspace, and only they will be able to manage the workspace. Additionally, a user can hit the “find workspace” button, which will redirect them to a new menu. Once a user joins (or finds and joins) a workspace, they will have access to all the channels that exist inside it, as well as having access to all the users in the workspace so that they may add a direct message with someone else. From this menu, the user may also hit back, if they would no longer like to create or find a new workspace to join. 

***NEW FEATURE**: find workspace* \
This menu displays all existing workspaces that the user has not already joined, so that they may choose which workspace they would like to join. When they click on the workspace they want to join, they then will join it and enter/access it, gaining access to the channels and users they might want to send a direct message to that already exist in the workspace. The user may also hit back, if they would no longer want to be in this menu. 

*FEATURE: accessing a workspace* \
Once we click on a workspace, we can see all the channels that already exist within it. Additionally, if the user has any existing direct messages, we display the names of the users they are participating in a direct message with. From this page, we can access any of the channels, access any of the direct messages, add a channel, or add a direct message. We can also choose to leave the workspace.

***NEW FEATURE**: leave workspace* \
If the user hits the “leave workspace” button, then they will unjoin the workspace, and it will no longer show up in their workspace dashboard. They will no longer be able to see the channels or direct messages inboxes there, or the messages posted within either. If they wish to see the channels/direct messages or the messages within those, the user must find and rejoin the workspace. 

*FEATURE: accessing a channel and sending messages* \
Each channel is contained within exactly one workspace. We display all the messages and the names of users who sent them in the chat. There is a text box where users can send messages to the channel, which will be able to be seen by all users in the workspace. 

*FEATURE: accessing a direct message and sending messages* \
Each direct message is contained within exactly one workspace. We display all the messages and the names of users who sent them in the direct message chat. Only exactly two users may participate in a direct message. We only show the names of direct messages in the menu when there are already messages sent to each other.  

*FEATURE: add channel* \
Only exactly one user may create a channel. The user can type the name of the new channel they would like to add to the current workspace they are in. However, this name must be unique; if the user tries to add a channel that has the same name as another channel already existing in that workspace, we display a message indicating that the channel name is already taken, to preserve our constraints in SQL and not crash the server. The user can try again with a different name, or they may hit the back button if they no longer wish to add a channel.

*FEATURE: add DM* \
In order to choose which other user the current user may like to participate in a new direct message with, we list all the users who are in the workspace and that the current user does not have an existing direct message chat with yet. The user clicks the other user’s name to start a direct message chat with them and is redirected to the chat page. However, if the current user clicks away from the chat without sending anything, the direct message relation will not be stored, and the other user’s name will not show up in the direct message menu. The user may hit the back button if they no longer wish to add a direct message (which is especially useful if no one else has joined the workspace yet).

*FEATURE: profile* \
On the dashboard (for workspaces, channels, or direct messages), a user can also access their profile, where they see the information associated with their user profile. They also are able to click a button to lead them to a menu where they can manage their workspaces. The user may also click log-out.

*FEATURE: manage workspaces* \
In this menu, the user sees all the workspaces that they own i.e. they were the user who created it. Only the owner may edit or delete workspaces. This includes channels–only the user who owns the workspace can delete the channels within it. This feature captures our weak entity relationships with cascading deletion between direct messages/channels and workspaces, i.e. if a workspace is deleted, then the channels and direct messages within the workspace will also be deleted. This also will affect the messages stored in the channels/direct messages, i.e. if a channel or direct message is deleted, then all the messages within it will also be deleted. All pages in the manage workspace menus have a back to workspace/back to dashboard button, which may redirect them to the workspace they were in (after editing channels), or redirect them to their workspace dashboard if they are done editing/deleting workspaces. 

***NEW FEATURE**: log-out* \
From the profile menu, if a user hits log-out, the page will be redirected to the sign-in page.


## Interesting web pages:

### 1. Chat dashboard
	
This is accessed by clicking on a workspace, then clicking on a channel, which will open the chat window.	

This webpage is very interesting because it is a combination of many of the other 
pages:

* User can access all workspaces that they are currently in (select all workspaces from “workspace” table that match with the “user” attribute in the “join” table)
* User can access all the channels in the workspace (select all channels from “channel” table that match the workspace ID “ws_id” entity with the current workspace and display their names)
* User can access all direct messages they have (select all the direct messages in “is_posted_in_dm” table that correspond with the current user being the recipient, and display the names of the DMs as the names of the sender, which is the other person in the DM)
* User may be redirected to menus for creating channels or direct messages
* User may be redirected to menus for creating workspaces/finding workspaces to join
* User may leave the current workspace (deletes the entry for that user in the “join” table with the current workspace) 
* User may click on “Profile” to access information about their profile or manage any workspaces they may own

Since it is the chat dashboard for the channel, it also includes everything for the chat. We read all the messages posted in the channel and who posted them (selecting from “user”, “message”, and “is_posted_in_channel” to get all the messages corresponding to the current channel and displaying the name and content). 

This webpage is the focal point/center of our application, serving as the main access point for all functionalities that we implemented. 
	
### 2. Manage workspace menu

This is accessed by hitting the “Profile” button, then clicking “Manage Your Workspaces” Button.

We select all the workspaces where the current user is the owner (matches the user_id attribute in the workspace table). There are two options: the first is to edit the channels, where we have a menu that displays all the channels in the respective workspace, and we may choose to delete channels. The second is to delete the workspace. This webpage is interesting because deleting a workspace will trigger the “on delete cascade” functionality for all the direct messages and channels, which is important to demonstrate how these two entities are weak entities of the workspace. The workspace is the top of the hierarchy, containing all the data for channels, direct message inboxes, and messages, so when a workspace is deleted, all of those will also be deleted.  

