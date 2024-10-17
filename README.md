# Current Topics of Software Engineering (2024) - Smart Alert Backend

## Project Overview

The **Smart Alert Backend** is a team assignment designed as the core system that powers the [Smart Alert Android App](https://github.com/thkox/current-topics-of-software-engineering_2023-smart-alert), developed for the "Current Topics of Software Engineering - Mobile Software" course, offered in the 7th semester of the 2023-2024 academic year at the University of Piraeus, Department of Informatics. The backend handles emergency reports submitted by users, ranks incidents based on severity and proximity, and sends location-based alerts to citizens in real-time using Firebase Cloud Messaging (FCM).

The backend ensures the scalability and reliability of the Smart Alert system, enabling real-time data processing and communication during emergencies. It integrates with the mobile app to deliver notifications, manage user data, and facilitate incident validation by employees (civil protection role).

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

### 1. Real-Time Incident Management

The backend processes emergency reports submitted by users through the Smart Alert app. It evaluates the severity of each incident based on:

- The number of reports submitted for a given incident.
- The proximity of the reports in terms of geographic location and time.

### 2. Automated User Notification

Once an incident is verified by an employee (civil protection role), the backend triggers an alert to users within a defined radius using Firebase Cloud Messaging (FCM). The notification includes essential information such as event type, location, timestamp, and safety instructions.

### 3. Incident Ranking and Prioritization

- The system ranks incidents based on how many reports are submitted and their geographic and time proximity.
- Incident rankings help employees decide which reports to approve and notify nearby citizens about.

### 4. Cloud Functionality

- **Cloud Functions:** Automatically triggered when new incident reports are submitted, allowing the backend to process and categorize the reports for further action.
- **Google Cloud Scheduler:** Manages periodic tasks, such as sending reminders or handling time-based checks for expired incident reports.

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

## Documentation and Resources

- Full project details can be found in the [Project-documentation.pdf](./docs/Project-documentation.pdf).

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
