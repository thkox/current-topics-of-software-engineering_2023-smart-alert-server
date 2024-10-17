# Current Topics of Software Engineering (2024) - Smart Alert Server

## Project Overview

The Smart Alert Backend is the core system that processes emergency reports and manages notifications for the Smart Alert mobile app. It is designed to collect reports from users, rank incidents based on severity and user proximity, and push location-based alerts to citizens using Firebase Cloud Messaging (FCM). The backend uses Google Cloud services to ensure scalability and reliability in real-time data processing and communication during emergencies.

This project was developed as part of the 7th-semester coursework for the "Modern Topics in Software Technology - Mobile Software" class at the University of Piraeus, Department of Informatics (Academic Year 2023-2024).

## Course Information

- **Institution:** University of Piraeus
- **Department:** Department of Informatics
- **Course:** Current Topics of Software Engineering (2024)
- **Semester:** 7th

## Technologies Used

- Python
- Firebase Authentication
- Firebase Realtime Database
- Firebase Cloud Storage
- Google Cloud Scheduler
- Google Cloud

## Features

1. **Real-Time Incident Management**

    The backend processes emergency reports submitted by users through the Smart Alert app. It evaluates the severity of each incident based on:
   
    - The number of reports submitted for a given incident.
    - The proximity of the reports in terms of geographic location and time.

2. **Automated User Notification**

    If an incident is verified by the employee (civil protection role), the backend triggers an alert to users within a defined radius using Firebase Cloud Messaging. The notification includes details such as the event type, location, timestamp, and safety instructions.

3. **Incident Ranking and Prioritization**

    - The system ranks incidents based on how many reports are submitted and how close they are in time and space.
    - These rankings help employees decide which incidents to approve and notify nearby citizens about.

4. **Cloud Functionality**

    - **Cloud Functions:** Triggered automatically when new incident reports are submitted, the backend processes and categorizes reports for further action.
    - **Google Cloud Scheduler:** Manages periodic tasks like sending reminders or handling time-based checks for expired incident reports.

## Setup Instructions

1. Clone the backend repository:
    ```bash
    git clone https://github.com/thkox/current-topics-of-software-engineering_2023-smart-alert-server.git
    ```

2. Install dependencies and Firebase CLI tools:
    ```bash
    pip install -r requirements.txt
    firebase login
    firebase init
    ```

3. Deploy the backend functions to Firebase:
    ```bash
    firebase deploy --only functions
    ```

## Related Repositories
[Smart Alert Mobile App](https://github.com/thkox/smart-alert)

The Smart Alert Android App is the user-facing component of the Smart Alert system. It allows citizens to report high-risk incidents, receive real-time notifications, and manage their account settings. The app communicates with this backend to process incident reports, manage user authentication, and send notifications through Firebase Cloud Messaging. Together, the app and backend form a complete system for real-time emergency response.

## Contributors

<table>
  <tr>
    <td align="center"><a href="https://github.com/ApostolisSiampanis"><img src="https://avatars.githubusercontent.com/u/75365398?v=4" width="100px;" alt="Apostolis Siampanis"/><br /><sub><b>Apostolis Siampanis</b></sub></a><br /></td>
    <td align="center"><a href="https://github.com/thkox"><img src="https://avatars.githubusercontent.com/u/79880468?v=4" width="100px;" alt="Theodore Koxanoglou"/><br /><sub><b>Theodore Koxanoglou</b></sub></a><br /></td>
    <td align="center"><a href="https://github.com/AlexanderCholis"><img src="https://avatars.githubusercontent.com/u/66769337?v=4" width="100px;" alt="Alexander Cholis"/><br /><sub><b>Alexander Cholis</b></sub></a><br /></td>
  </tr>
</table>

## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.
