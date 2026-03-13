# Honours-Project

This project was developed for my university Honours Project, this implements a web based leaderboard and analytics platform for the Tetris.com competitive community.

Built using Python and the Flask web framework, the system allows users to track, analyse and visualise their performances across the different official web based Tetris games. The platform supports a public leaderboard, with official scores within the community, and a way to track personal scores, allowing users to view their improvement over time.

Verified moderators can submit official scores to the leaderboard, while players can view them on the official leaderboard. 

The system uses Discord OAuth for authentication, allowing users to log in securely without needing to create a new account for the site.

# Features

Discord OAuth authentication for secure user login
Official leaderboard submission by verified moderators
Personal score tracking for individual players
Player profile pages displaying their historical performance
Dynamic graphs on player profiles, showing progression over time
Role based access control for moderator actions
Data deletion functionality, allowing users to delete their accounts with all data
Data export functionality, allowing users to download all data the site holds about them

# Technology used

Backend:
Python
Flask

Database:
SQLite

Authentication:
Discord OAuth with Flask-Dance

Frontend:
HTML
CSS
JavaScript

# System Architecture

The application uses a three-tiered architecture to seperate presentation logic, business rules and database access.

Presentation Layer:
Handles all HTTP routes, template rendering and user requests.

Business Logic Layer:
Handles application rules such as score validations, tier classification, user permissions and leaderboard generation.

Data Layer:
Manages database queries and allows for access and interactions with the SQLite database.

![CI](https://github.com/DenverCav/Honours-Project/actions/workflows/Verify.yml/badge.svg)
