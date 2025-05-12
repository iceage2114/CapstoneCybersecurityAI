Cybersecurity Chatbot

Submitted by: James Archer, Jeffrey Mann, Jonathan Zhang, Matthew Park
Prof. Owrang
Presented to

Department of Computer Science

In Partial Fulfillment of Requirements

CSC-493 Computer Science Capstone

American University

5/3/25 Spring Semester
































Table of Contents








































Abstract
In today’s digital landscape, cybersecurity threats are pervasive and evolving, yet individuals and small businesses often lack the technical expertise or resources to protect themselves effectively. Generic security tools are either too complex for non-technical users or fail to provide real-time, actionable insights tailored to specific risks. This gap leaves vulnerable populations exposed to threats such as data breaches, phishing attacks, and unpatched vulnerabilities. The purpose of this capstone project is to address these challenges by developing an accessible, AI-driven cybersecurity assistant that democratizes threat intelligence and empowers users with personalized guidance.
This project delivers a conversational AI chatbot that leverages Large Language Models (LLMs) and Retrieval-Augmented Generation (RAG) to provide real-time cybersecurity insights. The system integrates with industry-standard APIs, including VirusTotal, Shodan, and the National Vulnerability Database (NVD), to analyze threats like compromised credentials, exposed devices, and software vulnerabilities. We designed a user-friendly interface with Next.js with dual tabs for chat interactions and API management, and implemented a Python-based MLX framework for local AI processing and a Flask backend for secure API calls. We also addressed challenges such as API latency, inconsistent data formats, and security risks (e.g., prompt injection) and optimized responses for non-technical users through clear, contextual recommendations.
The hypothesis driving this work posited that combining LLMs with curated cybersecurity data could bridge the usability gap in personal digital protection. This report documents the design, development, and evaluation of the cybersecurity chatbot prototype. It provides a comprehensive overview of the technical architecture, challenges encountered, and solutions implemented to achieve the project’s goals. Additionally, it assesses the system’s effectiveness in delivering actionable security guidance to non-expert users.
The project demonstrated how AI can transform complex cybersecurity data into accessible, real-time insights, yielding several key outcomes: a functional prototype capable of delivering personalized threat analysis through natural language interactions; a scalable framework designed for future expansions like IoT device monitoring or multi-language support; and validation of RAG's ability to enhance LLM accuracy in domain-specific applications. To further improve the system, recommendations include expanding API integrations to incorporate dark web monitoring and automated patch management, implementing advanced analytics with machine learning for predictive threat detection based on user risk profiles, and developing a mobile companion app to boost accessibility through features like push notifications for urgent security alerts. These enhancements would build upon the project's success while addressing evolving cybersecurity needs. The chatbot’s low development cost and modular design make it a viable solution for underserved audiences. 
By reducing reliance on technical expertise, the system has the potential to significantly mitigate risks for individuals and small businesses. Future iterations could yield broader societal benefits, such as fostering a culture of proactive cybersecurity and reducing the economic impact of preventable breaches. This project explores the transformative role of AI in making enterprise-grade security tools accessible to all, while laying the groundwork for innovations in personalized digital protection.



Introduction
	The Cybersecurity Chatbot is a tool designed for the usage of individuals and small businesses. There are myriad technology companies on the market today that offer personalized cybersecurity assessments and services. The problem, however, is that the bundles and packages offered are incredibly expensive and not feasible for an individual or smaller company to pay into. This creates unnecessary risk, as there are also plenty of free cybersecurity tools on the web, one just needs to know where to find them, which is where Cybersecurity Chatbot comes in. Cybersecurity is no less important for these clients but it is far less accessible.
	With this chabot, which leverages a Large Language Model (LLM) and Retrieval-Augmented Generation (RAG) to provide real-time cybersecurity insights, clients can ask questions and gain advice on their cybersecurity needs. It works like any other AI chatbot (e.g., ChatGPT, Claude, etc.) with a user-friendly user interface focused on ease of use. For users that are more experienced, there is also the API Integration tab. This is where users can enter their API keys and other relevant information that they want the chatbot to consider in its response. The goal is for the user and chatbot to have a seamless conversation in regards to any information the user entered. Less experienced users need not fear because the chatbot can explain what any of the APIs do. 
	There are several APIs that have built-in support on this application: VirusTotal, Shodan, and the National Vulnerability Database (NVD). VirusTotal allows users to upload files and it uses numerous antivirus scanners to ensure the file is virus-free. Shodan is an Internet of Things search engine, among other things. It allows developers to easily monitor their network traffic and provide easily digestible reports on vulnerabilities, VPN usage, and applications. The NVD is a glossary of all common vulnerabilities found and reported by government agencies and companies. It also includes information on the status of vulnerabilities.
	The rest of this report will document what we did, how we did it, and next steps for this project.




















Review
	As mentioned in the introduction, there are many artificial intelligence-based cybersecurity resources already on the market, however none provide the same accessibility or depth as this project. Many projects have a steep price tag, at times only allowing a free demo, such as Charlotte AI from CrowdStrike or Safe X. This pricing is often not feasible for individuals or small businesses. Another reason this product fills a gap in the market is for the tailored and modular design that allows for the user to enter specific API information. Everyday AI chatbots, such as ChatGPT, can help with basic cybersecurity needs, but they do not provide the same depth and customization as this project. This product allows the user and the LLM to interact with specific API and system information to better the experience of the customer. The goal of this project is to provide the best of both worlds when it comes to accessibility and accuracy and depth of responses.


Design Requirements/Details of Project

	This project consists of two main parts: the front end and the back end. The front end was created using a mix of Python and Next.js. The back end was also created using Next.js. Flask is used for secure API interactions.

Feasibility Discussion

Economic: 
	This project was free to create and use. It was built in a manner that enables the developers to continue to provide an accessible and quality service to customers. In the future it may be reasonable for the developers to implement some pricing for this product, but it would be set with the 
Environmental:
Manufacturability:
Technical:
Ethical:
Political:

Final Implementation

Challenges:
Latency
Inconsistent API responses
Security concerns
User Experience

Results

Conclusions
Some next steps for this project include continuing to refine UI and user experience. Also, complete ongoing and continuous testing for speed and accuracy. If there is a hiccup, implement improvements. Continue to strengthen safeguards for the model and users. Implement inherent support for more APIs.
It would be beneficial to develop a companion mobile app for the chatbot, so that users can always obtain real-time information or alerts about their system.

References
https://docs.virustotal.com/docs/how-it-works 
https://www.shodan.io/ 
https://nvd.nist.gov/general 

