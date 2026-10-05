# Discohook website UI preview
This pdf is show each ui and things in https://discohook.app site ui

## Top Bar:
![](Pasted%20image%2020261005002034.png)
- User profile: the Peace there is my discord name and discord pfp both fetch by discohook.
- when you click on it opens a side bar:
![](Pasted%20image%2020261005002141.png)
which has server selection. for example if i click on hoho hub server.
it opens a new tab with url as https://discohook.app/s/906426036772818954 , number being server id.
ui:
![](Pasted%20image%2020261005002323.png)
- home:
![](Pasted%20image%2020261005002359.png)
shows the users server permissions.
- profile:
![](Pasted%20image%2020261005002446.png)
lets u change bot bio and bot name probably server profile only.
- Sessions:
![](Pasted%20image%2020261005002556.png)
shows all the session which have access to this server webhook. make our staff access panel like this. in discohook.app administrator  already have full access to the features.

- Components:
![](Pasted%20image%2020261005002817.png)
shows all the compoents which were send , im not sure whats the use of this.

- Audit log:
  ![](Pasted%20image%2020261005003113.png)
  shows logs who accessed it
  
  - Triggers:
  - lets u create specific triggers
now Top Bar: Backups
![](Pasted%20image%2020261005003348.png)
- import and export: self explain
![](Pasted%20image%2020261005003447.png)
edit ![](Pasted%20image%2020261005003506.png):
![](Pasted%20image%2020261005003535.png)

open backup : ![](Pasted%20image%2020261005003608.png)
opens the backup
![](Pasted%20image%2020261005003716.png)
that img is taken from the message Thumbnail if there is any.

- Link Embeds: not sure whats different about it other than allowing to put videos in the message.

## Classic:
![](Pasted%20image%2020261004222803.png)
- Here you can the default classic ui of discohook.app
- now i will show you what happens when you click the button "Add Webhook"

![](Pasted%20image%2020261004222935.png)
- it opens this window where you can select a server when you want to send a msg or edit one.
- when open the selection menu, it fetches all the server the bot has access to depending on the user access.

when you select a server in the selection menu:

![](Pasted%20image%2020261004223436.png)
- it lists out all the webhook it can access but this isnt really a need for our site cuz we will be sending msg using bot which has access to all channls if head admin or owner perms but if its a staff it will only list channels which the staff was given access  to. what you can do is but the profile selection in this manners.

when you clikc on ![](Pasted%20image%2020261004230245.png) in message box, it lets u give that message box a name.
when you click on ![](Pasted%20image%2020261004230349.png) in message box, it just creats a duplicate message box.
when you click on ![](Pasted%20image%2020261004230439.png) deletes that message box.

now at the bottom right corner of message box:
![](Pasted%20image%2020261004230715.png)
it opens a menu with a lot of options:
![](Pasted%20image%2020261004230810.png)
its for quick pinging a thing in the message, like for mentioning a channel from the server in the message box which adds the data to the message box.
example:
check out <#132324232523245> 

the preview loads the channel name. it also allows to quick mention everything from users, roles and emojis or the time with costume time support: ![](Pasted%20image%2020261004231310.png)
 and it also supports sending emojis which are not in the server it self:
 ![](Pasted%20image%2020261004231425.png)
 
 now at the last thing in the context box:
 ![](Pasted%20image%2020261004231519.png)
 just next to quick paste button there is a drag button which can edit the size of the message box, like make it long only, doesnt make it wider cuz that might mess with preview side.
 thats all in context box.

now we will move directly to "Add ∇" which is just below Attachments:
![](Pasted%20image%2020261004225857.png)
by clicking on the "Add ∇" it drops down this options, where u can add a component or a Embed.

Now i will show what happens when you click on "Add Embed":
![](Pasted%20image%2020261004231937.png)
![](Pasted%20image%2020261004232002.png)

it adds this embed message just below attachments and below the "Add ∇" where it allows u send a embeded message.

![](Pasted%20image%2020261004232819.png)

- Author Url: discord user profile link.
- Fields: added a sub message box in the same embed:
  ![](Pasted%20image%2020261004232943.png)

- everything else is just self explaming.


now to part 2 "Add Row":
![](Pasted%20image%2020261004233128.png)
 by click on that option it added a row box like:
![](Pasted%20image%2020261004233403.png)which gives u option to add a component and when you click on it, it opens a menu like: 
![](Pasted%20image%2020261004233501.png)

if you click button:
![](Pasted%20image%2020261004233606.png)
it added a components with name "Button 1" and shows to preview also.
and if you click on the "Button 1" to edit its name it opens this menu:
![](Pasted%20image%2020261004233821.png)
 where you can put a label on it and give it a custom emoji :
 ![](Pasted%20image%2020261004233917.png)
 which fetch the server emoji and has a custom one where you use a emoji from a different server with no connation needed, just need emoji id:
 like when you click on the "+" button it open this window:![](Pasted%20image%2020261004234054.png)
 which works everywhere its possible and it can be animated emoji or a static one.
 and if a custom emoji is added it is saved in cache till the client bowsers allowed so the users doesnt have to copy and paste the id again and again.
 
 on button componenet edit, you can change the color of the button using style 
 ![](Pasted%20image%2020261004234425.png)

now its move to flow
![](Pasted%20image%2020261004234451.png)
when you click on flow it open this menu:
![](Pasted%20image%2020261004234539.png)
where you can add a action, action like:
![](Pasted%20image%2020261004234643.png)

- Wait for X seconds ui:
![](Pasted%20image%2020261004234823.png)

- Check ui:
  ![](Pasted%20image%2020261004234903.png)
  - Function drop down options:
	    ![](Pasted%20image%2020261004234930.png)
	 we already have most of them but we are missing the "Member has role" check
		 - Member has role selection menu:
		   ![](Pasted%20image%2020261004235046.png)
		 -  Type: Static, Adaptive and Mirror
		 - Role: fetch roles from the server 
		 - Add Action - gives the same menu like the head Add Action.
		   has the same Add Action button on Otherwise tab.
	 we have almost all other options so im not going to show them but they should be made in the same style as these.
- Link button:
  ![](Pasted%20image%2020261004235842.png)
- link button ui:
  ![](Pasted%20image%2020261004235923.png)
  
- Select Menu:
  ![](Pasted%20image%2020261005000000.png)
- Select Menu ui:
![](Pasted%20image%2020261005000135.png)
self explain, flow is same, and add option just adds a option.
 - Preview of select menu:
   ![](Pasted%20image%2020261005000252.png)
 - discohook also alllows u click on the preview to check how it would look if someone click on the select menu.
 - User Select Menu:
   ![](Pasted%20image%2020261005000602.png)- user select menu ui:
	   ![](Pasted%20image%2020261005000643.png)
	   - Add Default Value: adds the ID input.
- Role select menu, User & Role Select menu and Channel select menu: same as User Select Menu.

Now to "Set Link"
![](Pasted%20image%2020261005001021.png)

Now to "Options" gives a drop down menu like this:
![](Pasted%20image%2020261005001116.png)

  - Flags:
![](Pasted%20image%2020261005001215.png)
- Allowed Mentions (off by default):
  ![](Pasted%20image%2020261005001258.png)
evreything else is self explain.

at last "Add Message":
![](Pasted%20image%2020261005001420.png)


## Components v2:
![](Pasted%20image%2020261005001504.png)

- "Add ∇":
![](Pasted%20image%2020261005001539.png)
- Each option:
  ![](Pasted%20image%2020261005001628.png)
- Text 1: Add Accessory:
  ![](Pasted%20image%2020261005001700.png)
- Container 1: Add:
  ![](Pasted%20image%2020261005001750.png)
- Gallery 1:
![](Pasted%20image%2020261005001813.png)
- Add Media: adds Item 1
  
everything else is same just like Classic 
  
  
  that is all the features adn ui in the discohook.app
