- A reflection statement on your use of GenAI for code generation, which should include: (1) the new prompts that you have to use to generate the ideal codes; (2) a description of the code changes in each new version; (3) a description of the strength and weakness of the GenAI tool in your view.

## AI use reflection:

For the client side GUI I gave ChatGPT the project design that we wrote up and it generated a decent GUI for the first generation. I decided to give AI the prompt of “Make the GUI more simple and easier for users to navigate”. I also told AI to improve the code to fix any issues I had before. It generated an improved version of the code that worked great but it was missing the admin panel. For the last prompt I told it to make a button for the admin login and after testing it worked great.

For server side of the code each version did VERSION 1: Handles input from ClientSide and ticket data as well as login validation, VERSION 2: Added GUI and logging, improved error handling and added more admin features, VERSION 3: Closed inputs and made static. The AI prompts became the design document with a similar application style for the first prompt type. 


For client side of the code VERSION 1: Handles connection to ServerSide and ready for client-side UI, VERSION 2: Works in client for specifically user, VERSION 3:Works in client for specifically admin.Overall final prompts would be to create a large array of visuals that the agent can digest and fully base a model of the program on.


## Overview: (What we learned from using AI)

It will all require some customization to our specific app, like the admin display capabilities and specifics of the form.I might also need to go in and fix some text placement, at first glance I'm pretty sure a couple things are out of place.The only way I can think to test the system is to make a ticket and submit through the full pipeline, and we don't need AI for that. Throughout the process the main issue was testing it and being able to understand certain issues that came up for instance we had to move away from html communication because python kept requiring flask. In order to fix this we had to fall back to basic python communication since kernel level compilation couldn’t be changed. In the end as a group the biggest part of communication was getting an accurate visual representation to the model. Text description is different from images especially when the final product is still unknown.

